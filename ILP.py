# -*- encoding: utf-8 -*-
"""
@File    :   ILP.py
@Time    :   2024/08/18 14:57:29
@Author  :   ZeroMaple
@Contact :   LingYingQvQ@gmail.com
"""

# import os
import re

# import sys
import time
import click
import asyncio
import aiohttp
import logging
import requests

# import functools
import threading
import fake_useragent
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup

from download import download_image
from utils.fanqie_decode import dec
from config import Config
from log import Logger
from db import DB
from utils.utils import show_banner, set_title, string_to_md5


class NovelScraper:
    def __init__(self, id: str, alias=None) -> None:
        show_banner()
        set_title()
        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

        self.cfg = Config("./config.json")
        self.MAX_WORKERS = self.cfg.MAX_WORKERS
        self.SLEEP_TIME = self.cfg.SLEEP_TIME
        self.DATA_PATH = self.cfg.PATHS.DATA_PATH
        self.NOVELS_PATH = self.cfg.PATHS.NOVELS_PATH
        self.NOVELS_NEW_PATH = self.cfg.PATHS.NOVELS_NEW_PATH
        self.LOGS_PATH = self.cfg.PATHS.LOGS_PATH
        self.POSTERS_PATH = self.cfg.PATHS.POSTERS_PATH
        self.DB_PATH = self.cfg.PATHS.DB_PATH
        self.db = DB(self.DB_PATH)

        self.id: int = id
        self.title: str = alias
        self.base_url: str = ""
        self.index_url: str = ""

        self.index_page_text: str = ""
        self.HEADERS = {"User-Agent": fake_useragent.UserAgent().random}

        self.thread_lock = threading.Lock()
        self._cancel_event = threading.Event()
        self.executor = None
        self.sem = asyncio.Semaphore(self.MAX_WORKERS)

    def get_index_page(self):
        if not self.index_page_text:
            self.index_page_text = requests.get(
                self.index_url, headers=self.HEADERS
            ).text
        return self.index_page_text

    def get_title(self): ...

    def get_index(self):
        self.get_title()
        self.index_chapter_list = []
        self.index_chapter_md5_id_list = []
        self.index_chapter_id_list = []
        self.index_chapter_title_list = []
        self.index_chapter_url_list = []
        self.index_chapter_sum_list = []

        self.chapter_md5_id_slice = slice(0, 1)
        self.chapter_id_slice = slice(1, 2)
        self.chapter_title_slice = slice(2, 3)
        self.chapter_url_slice = slice(3, 4)
        self.chapter_sum_slice = slice(4, 5)

        if not self.db.table_exists(self.title):
            self.db.create_table(self.title)

    def get_author(self):
        self.get_index_page()
        self.author = ""

    def is_downloaded(self, chapter_title: str) -> bool:
        self.get_title()
        path = Path(f"{self.NOVELS_PATH}/{self.title}")
        files = path.glob("*.txt")
        for file in files:
            if file.stem == chapter_title:
                return True
        return False

    def check_full(self) -> bool:
        self.get_title()
        self.get_index()
        path = Path(f"{self.NOVELS_PATH}/{self.title}")
        if path.exists() and len(list(path.glob("*.txt"))) == len(
            self.index_chapter_title_list
        ):
            return True
        else:
            return False

    def save_novel(self, title: str, chapter: str, chapter_title: str) -> None:
        novels_path = Path(self.NOVELS_PATH)
        chapter_path = Path(f"{chapter_title}.txt")
        title_path = novels_path / Path(title)
        final_path = title_path / chapter_path
        title_path.mkdir(exist_ok=True)
        with open(f"{final_path}", "w", encoding="utf-8") as f:
            f.write(chapter)

    async def get_chapter(self, multi_thread: bool = True) -> None:
        self.get_index()
        self.logger = Logger(f"{self.LOGS_PATH}/{self.title}.log")
        # downloaded_files = Path(
        #     f"{self.NOVELS_PATH}/{self.title}").glob("*.txt")
        # downloaded_chapters = [file.stem for file in downloaded_files]

        # download_list = [
        #     chapter for chapter in self.index_chapter_title_list if chapter not in downloaded_chapters]
        download_list = self.index_chapter_title_list
        download_length = len(download_list)
        self.download_length = download_length
        self.download_list = download_list

        if self.check_full():
            print("所有章节已下载！")
            self.logger.info("所有章节已下载！")
            return

        self.progress_bar = tqdm(
            total=download_length, desc=f"{self.title} - 下载进度", unit="章"
        )
        self.progress_bar.update(0)

        tasks = [self.fetch_chapter(i) for i in range(download_length)]
        await asyncio.gather(*tasks)
        # if self.check_full() == True:
        #     print(f"{self.title} 下载完成！")
        #     self.logger.info(f"{self.title} 下载完成！")
        # else:
        #     print(f"{self.title} 下载失败！")
        #     self.logger.info(f"{self.title} 下载失败！")

    async def fetch_chapter(self, index: int) -> None:
        set_title(f"ILP - {self.title} - {self.download_list[index]}")
        if self.is_downloaded(self.download_list[index]):
            return


class QidianScraper(NovelScraper):
    def __init__(self, id: str, alias: str = None):
        super().__init__(id, alias)
        self.base_url = "https://m.qidian.com"
        self.title_url = f"{self.base_url}/book/{self.id}"
        self.index_url = f"{self.base_url}/book/{self.id}/catalog"
        self.index_page_text = self.get_index_page()
        self.title_page_text = self.get_title_page()

    def get_title_page(self):
        self.title_page_text = requests.get(self.title_url, headers=self.HEADERS).text
        return self.title_page_text

    def get_title(self):
        if self.title is None:
            soup = BeautifulSoup(self.title_page_text, "html.parser")
            self.title = soup.find("h1").text
            return self.title
        else:
            return self.title

    def get_index(self, export_path: str = None, export_type: str = None) -> list:
        super().get_index()
        if self.db.is_table_empty(self.title):
            soup = BeautifulSoup(self.index_page_text, "html.parser")

            title_list = soup.find_all("h2")
            self.index_chapter_title_list = [
                i.text for i in title_list if i.text.strip() != ""
            ]

            url_list = soup.find_all("a", {"data-showeid": "mqd_R127"})
            self.index_chapter_url_list = [
                ("https:" + i["href"]).strip("/") for i in url_list
            ]

            self.index_chapter_md5_id_list = [
                string_to_md5(i) for i in self.index_chapter_url_list
            ]

            self.index_chapter_id_list = [
                i.split("/")[-1] for i in self.index_chapter_url_list
            ]

            self.index_chapter_sum_list = [None for _ in self.index_chapter_title_list]

            for i in range(len(self.index_chapter_title_list)):
                chapter_md5_id = self.index_chapter_md5_id_list[i]
                chapter_id = self.index_chapter_id_list[i]
                chapter_title = self.index_chapter_title_list[i]
                chapter_url = self.index_chapter_url_list[i]
                self.db.insert_data(
                    self.title,
                    chapter_md5_id,
                    chapter_id,
                    chapter_title,
                    chapter_url,
                    None,
                )
                self.index_chapter_list.append(
                    [chapter_md5_id, chapter_id, chapter_title, chapter_url, None]
                )
        elif self.db.is_table_empty(self.title) is None:
            return
        elif not self.db.is_table_empty(self.title):
            all_data = self.db.get_all_data(self.title)
            for data in all_data:
                chapter_md5_id = data[self.chapter_md5_id_slice][0]
                chapter_title = data[self.chapter_title_slice][0]
                chapter_url = data[self.chapter_url_slice][0]
                chapter_sum = data[self.chapter_sum_slice][0]
                chapter_id = data[self.chapter_id_slice][0]
                self.index_chapter_md5_id_list.append(chapter_md5_id)
                self.index_chapter_id_list.append(chapter_id)
                self.index_chapter_title_list.append(chapter_title)
                self.index_chapter_url_list.append(chapter_url)
                self.index_chapter_sum_list.append(chapter_sum)
                self.index_chapter_list.append(
                    [
                        chapter_md5_id,
                        chapter_id,
                        chapter_title,
                        chapter_url,
                        chapter_sum,
                    ]
                )
        if export_path is not None and export_type is not None:
            self.db.export_data(self.title, export_path, export_type)
        return self.index_chapter_list

    def get_author(self) -> str:
        super().get_author()
        self.get_title_page()
        soup = BeautifulSoup(self.title_page_text, "html.parser")
        self.author = soup.find("a", class_="detail__header-detail__author-link").text
        self.author = re.sub(r"作者：|级别：|Lv.\d+|\s", "", self.author)
        return self.author

    def get_picture(self) -> str:
        self.get_title()
        soup = BeautifulSoup(self.title_page_text, "html.parser")
        img = soup.find("img", {"class": "detail__header-cover__img"})
        self.picture_url = "https:" + img["src"]
        path = Path(f"{self.POSTERS_PATH}/{self.title}.png")
        download_image(self.picture_url, path)
        return self.picture_url

    async def fetch_chapter(self, index: int) -> None:
        await super().fetch_chapter(index)
        db = DB(self.DB_PATH)

        chapter_title = self.download_list[index]

        async with self.sem:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.index_chapter_url_list[index], headers=self.HEADERS
                ) as response:
                    chapter_get = await response.text()
                    output_front = (
                        "(" + str(index + 1) + "/" + str(self.download_length) + ")"
                    )
                    output_behind = (
                        "正在爬取 " + self.title + ":" + chapter_title + " 中..."
                    )
                    # print("{:<15} {:}".format(output_front, output_behind))
                    tqdm.write("{:<15} {:}".format(output_front, output_behind))
                    self.logger.info(f"开始爬取 {self.title}:{chapter_title}")

                    soup = BeautifulSoup(chapter_get, "html.parser")
                    p = soup.find_all("p", class_=False)
                    chapter_text = [i.text for i in p]
                    chapter_head = chapter_title + "\n---\n\n"
                    chapter_main = "\n".join(chapter_text)
                    chapter_main = re.sub(r"\u3000", r"", chapter_main)
                    chapter_sum = len(chapter_main)
                    # self.index_chapter_list[index][self.chapter_sum_slice] = chapter_sum
                    chapter_md5 = string_to_md5(self.index_chapter_url_list[index])
                    db.update_data(
                        self.title, "chapter_sum", chapter_sum, "md5_id", chapter_md5
                    )
                    self.save_novel(
                        self.title, chapter_head + chapter_main, chapter_title
                    )
                    self.progress_bar.update(1)
                    await asyncio.sleep(self.SLEEP_TIME)


class FanqieScraper(NovelScraper):
    def __init__(self, id: str, alias=None) -> None:
        super().__init__(id, alias)
        self.base_url = "https://fanqienovel.com"
        self.index_url = f"https://fanqienovel.com/page/{id}"
        self.api_url = "https://fanqienovel.com/api/reader/full?itemId="
        self.index_page_text = self.get_index_page()

    def get_title(self):
        if self.title is None:
            soup = BeautifulSoup(self.index_page_text, "html.parser")
            self.title = soup.find("h1").text
            return self.title
        else:
            return self.title

    def get_index(self, export_path: str = None, export_type: str = None) -> list:
        super().get_index()
        if self.db.is_table_empty(self.title):
            soup = BeautifulSoup(self.index_page_text, "html.parser")
            index_list = soup.find_all("div", class_="chapter-item")
            for index in range(len(index_list)):
                chapter_title = index_list[index].find("a").text
                chapter_url = self.base_url + index_list[index].find("a")["href"]
                chapter_id = re.sub(
                    r"https://fanqienovel.com/reader/", "", chapter_url
                ).strip("/")
                # print(chapter_id)
                chapter_md5_id = string_to_md5(chapter_url)
                self.db.insert_data(
                    self.title,
                    chapter_md5_id,
                    chapter_id,
                    chapter_title,
                    chapter_url,
                    None,
                )
                self.index_chapter_md5_id_list.append(chapter_md5_id)
                self.index_chapter_id_list.append(chapter_id)
                self.index_chapter_title_list.append(chapter_title)
                self.index_chapter_url_list.append(chapter_url)
                self.index_chapter_sum_list.append(None)
                self.index_chapter_list.append(
                    [chapter_md5_id, chapter_id, chapter_title, chapter_url, None]
                )
        elif self.db.is_table_empty(self.title) is None:
            return
        elif not self.db.is_table_empty(self.title):
            all_data = self.db.get_all_data(self.title)
            for data in all_data:
                chapter_md5_id = data[self.chapter_md5_id_slice][0]
                chapter_title = data[self.chapter_title_slice][0]
                chapter_url = data[self.chapter_url_slice][0]
                chapter_sum = data[self.chapter_sum_slice][0]
                chapter_id = data[self.chapter_id_slice][0]
                self.index_chapter_md5_id_list.append(chapter_md5_id)
                self.index_chapter_id_list.append(chapter_id)
                self.index_chapter_title_list.append(chapter_title)
                self.index_chapter_url_list.append(chapter_url)
                self.index_chapter_sum_list.append(chapter_sum)
                self.index_chapter_list.append(
                    [
                        chapter_md5_id,
                        chapter_id,
                        chapter_title,
                        chapter_url,
                        chapter_sum,
                    ]
                )
        if export_path is not None and export_type is not None:
            self.db.export_data(self.title, export_path, export_type)
        return self.index_chapter_list

    def get_author(self) -> str:
        super().get_author()
        soup = BeautifulSoup(self.index_page_text, "html.parser")
        self.author = soup.find("span", class_="author-name-text").text
        return self.author

    async def fetch_chapter(self, index: int) -> None:
        await super().fetch_chapter(index)

        chapter_title = self.download_list[index]

        from utils.fanqie_decode import dec

        db = DB(self.DB_PATH)
        # cookie = {"novel_web_id": "7357767624615331362"}

        async with self.sem:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}{self.index_chapter_id_list[index]}",
                    headers=self.HEADERS,
                    cookies={"novel_web_id": "7357767624615331362"},
                ) as response:
                    output_front = (
                        "(" + str(index + 1) + "/" + str(self.download_length) + ")"
                    )
                    output_behind = (
                        "正在爬取 " + self.title + ":" + chapter_title + " 中..."
                    )
                    tqdm.write("{:<15} {:}".format(output_front, output_behind))
                    # print("{:<15} {:}".format(output_front, output_behind))
                    self.logger.info(f"开始爬取 {self.title}:{chapter_title}")
                    chapter_json = await response.json()
                    soup = BeautifulSoup(
                        chapter_json["data"]["chapterData"]["content"], "html.parser"
                    )
                    p = soup.find_all("p", class_=False)
                    chapter_text = [i.text for i in p]
                    chapter_main = "\n".join(chapter_text)
                    chapter_main = re.sub(r"\u3000", r"", chapter_main)
                    chapter_head = chapter_title + "\n---\n\n"
                    chapter_sum = chapter_json["data"]["chapterData"][
                        "chapterWordNumber"
                    ]
                    self.index_chapter_list[index][self.chapter_sum_slice] = chapter_sum
                    chapter_md5 = string_to_md5(self.index_chapter_url_list[index])
                    db.update_data(
                        self.title, "chapter_sum", chapter_sum, "md5_id", chapter_md5
                    )
                    self.save_novel(
                        self.title, chapter_head + chapter_main, chapter_title
                    )
                    dec(
                        chapter_title,
                        self.title,
                        log_path=self.LOGS_PATH,
                        novels_path=self.NOVELS_PATH,
                        novels_new_path=self.NOVELS_PATH,
                    )
                    self.progress_bar.update(1)
                    time.sleep(self.SLEEP_TIME)


cfg = Config("./config.json")


@click.group()
def main(**kwargs) -> None: ...


# @listen_error(exception=KeyboardInterrupt)
@main.command()
@click.option("--id", "-i", default=None, required=True, help="小说ID")
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(cfg.sites),
)
def download(**kwargs):
    try:
        exec = Exec(kwargs=kwargs)
        exec_func = getattr(exec, kwargs["site"])()
        asyncio.run(exec_func.get_chapter())
    except KeyboardInterrupt:
        tqdm.write("正在退出")


@main.command()
@click.option("--title", "-t", default=None, required=True, help="小说标题")
@click.option("--chapter_title", "-ct", default="all", help="小说章节标题,默认为全部")
def decode(**kwargs):
    if kwargs["chapter_title"] == "all":
        chapter_title_list = []
        file_list = Path(cfg.NOVELS_PATH / kwargs["title"]).glob("*.txt")
        for file in file_list:
            chapter_title_list.append(file.stem)
        for i in range(len(chapter_title_list)):
            dec(
                chapter_title_list[i],
                kwargs["title"],
                log_path=cfg.LOGS_PATH,
                novels_path=cfg.NOVELS_PATH,
                novels_new_path=cfg.NOVELS_PATH,
            )
    else:
        dec(
            kwargs["chapter_title"],
            kwargs["title"],
            log_path=cfg.LOGS_PATH,
            novels_path=cfg.NOVELS_PATH,
            novels_new_path=cfg.NOVELS_PATH,
        )


@main.command()
@click.option("--id", "-i", default=None, required=True, help="小说ID")
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(cfg.sites),
)
@click.option("--out_put_path", "-op", default=None, help="输出到文件")
@click.option(
    "--out_put_type",
    "-ot",
    default=None,
    help="输出格式",
    type=click.Choice(["txt", "json", "csv"]),
)
def get_index(**kwargs):
    exec = Exec(kwargs=kwargs)
    exec_func = getattr(exec, kwargs["site"])()
    if kwargs["out_put_path"] is None and kwargs["out_put_type"] is None:
        exec_func.get_index()
        print("缓存目录到数据库成功")
    elif kwargs["out_put_path"] is not None and kwargs["out_put_type"] is not None:
        exec_func.get_index(
            export_path=kwargs["out_put_path"], export_type=kwargs["out_put_type"]
        )
        print(f"输出到{kwargs['out_put_path']}成功")
    else:
        print("输出路径和输出格式必须都指定或都不指定")


@main.command()
@click.option("--id", "-i", default=None, required=True, help="小说ID")
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(cfg.sites),
)
def get_author(**kwargs):
    exec = Exec(kwargs=kwargs)
    exec_func = getattr(exec, kwargs["site"])()
    author = exec_func.get_author()
    print(f"作者: {author}")


class Exec:
    def __init__(self, kwargs) -> None:
        self.kwargs = kwargs

    def fanqie(self):
        return FanqieScraper(self.kwargs["id"])

    def qidian(self):
        return QidianScraper(self.kwargs["id"])


if __name__ == "__main__":
    # %%
    main()
    # %%
    # qidian = QidianScraper(1041092118)
    # %%
    # fanqie = FanqieScraper(7122740304741927939)
    # print(fanqie.get_title())
