import re
import time
import requests
from db import DB
from pathlib import Path
from bs4 import BeautifulSoup

from utils.utils import string_to_md5
from download import download_image
from scraper.base_scraper import BaseScraper


class QidianScraper(BaseScraper):
    def __init__(self, book_id: int = None, alias: str = None, cookies=None) -> None:
        super().__init__(book_id, alias, cookies)
        self.base_url = "https://m.qidian.com"
        self.title_url = f"{self.base_url}/book/{self.id}"
        self.index_url = f"{self.base_url}/book/{self.id}/catalog"
        self.index_page_text = self.get_index_page()
        self.title_page_text = self.get_title_page()

    def get_title_page(self):
        """获取小说标题所在页的HTML代码"""
        self.title_page_text = requests.get(self.title_url, headers=self.HEADERS).text
        return self.title_page_text

    def get_title(self):
        super().get_title()
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
                string_to_md5(i) for i in self.index_chapter_id_list
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
                    {
                        "md5_id": chapter_md5_id,
                        "id": chapter_id,
                        "title": chapter_title,
                        "url": chapter_url,
                        "sum": None,
                    }
                )
                # self.index_chapter_list.append(
                #     [chapter_md5_id, chapter_id, chapter_title, chapter_url, None]
                # )
        elif self.db.is_table_empty(self.title) is None:
            return []
        # 从数据库中获取缓存
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
                    {
                        "md5_id": chapter_md5_id,
                        "id": chapter_id,
                        "title": chapter_title,
                        "url": chapter_url,
                        "sum": chapter_sum,
                    }
                )
                # self.index_chapter_list.append(
                #     [
                #         chapter_md5_id,
                #         chapter_id,
                #         chapter_title,
                #         chapter_url,
                #         chapter_sum,
                #     ]
                # )
        if export_path is not None and export_type is not None:
            self.db.export_data(self.title, export_path, export_type)
        return self.index_chapter_list

    def get_author(self) -> str:
        super().get_author()
        self.get_title_page()
        soup = BeautifulSoup(self.title_page_text, "html.parser")
        author = soup.find("a", class_="detail__header-detail__author-link").text
        author = re.sub(r"作者：|级别：|Lv.\d+|\s", "", author)
        self.author = author
        return author

    def get_picture(self) -> str:
        self.get_title()
        soup = BeautifulSoup(self.title_page_text, "html.parser")
        img = soup.find("img", {"class": "detail__header-cover__img"})
        picture_url = "https:" + img["src"]
        path = Path(f"{self.POSTERS_PATH}/{self.title}.png")
        download_image(picture_url, path)
        return picture_url

    def parse_chapter(
        self, chapter_response: str, chapter_title: str, index: int
    ) -> None:
        db = DB(self.DB_PATH)

        soup = BeautifulSoup(chapter_response, "html.parser")
        p = soup.find_all("p", class_=False)
        chapter_head = chapter_title + "\n---\n\n"
        chapter_text = [i.text for i in p]
        chapter_main = "\n".join(chapter_text)
        chapter_sum = len(chapter_main)
        chapter_md5 = string_to_md5(self.index_chapter_list[index]["id"])
        self.save_novel(self.title, chapter_head + chapter_main, chapter_title)
        self.logger.info(f"下载完成：{self.title}:{chapter_title}")

        db.update_data(self.title, "chapter_sum", chapter_sum, "md5_id", chapter_md5)

        del db

    async def fetch_chapter(self, index: int) -> None:
        await super().fetch_chapter(index)

        response = await self.async_get(
            self.index_chapter_list[index]["url"],
            headers=self.HEADERS,
            cookies=self.cookies,
        )

        chapter_response = response
        time.sleep(self.SLEEP_TIME)
        return {
            "chapter_response": chapter_response,
            "index": index,
            "chapter_title": self.index_chapter_list[index]["title"],
        }
