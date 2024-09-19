import logging
import requests
import asyncio
import aiohttp
import fake_useragent
from tqdm import tqdm
from pathlib import Path

from db import DB
from log import Logger
from config import Config
from utils.utils import SharedData, cookie_parser, set_title


class BaseScraper:
    """爬虫基类"""

    def __init__(self, book_id: int = None, alias=None, cookies=None) -> None:
        self.shared_data = SharedData()

        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

        self.cfg = Config("./config.json")
        self.MAX_WORKERS = self.cfg.MAX_WORKERS
        self.SLEEP_TIME = self.cfg.SLEEP_TIME
        self.DATA_PATH = self.cfg.PATHS.DATA_PATH
        self.NOVELS_PATH = self.cfg.PATHS.NOVELS_PATH
        self.LOGS_PATH = self.cfg.PATHS.LOGS_PATH
        self.POSTERS_PATH = self.cfg.PATHS.POSTERS_PATH
        self.DB_PATH = self.cfg.PATHS.DB_PATH
        self.db = DB(self.DB_PATH)

        self.id: int = book_id
        self.title: str = alias
        self.base_url: str = ""
        self.index_url: str = ""

        self.author: str = ""
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

        self.index_page_text: str = ""
        self.HEADERS = {"User-Agent": fake_useragent.UserAgent().random}
        if cookies is not None:
            cookies = cookie_parser(cookies)
        self.cookies = cookies

        # self.thread_lock = threading.Lock()
        # self._cancel_event = threading.Event()
        self.executor = None
        self.sem = asyncio.Semaphore(self.MAX_WORKERS)

        # self.logger = Logger(f"{self.LOGS_PATH}/{self.id}.log")

    def set_id(self, book_id: int) -> None:
        self.id = book_id

    def set_logger(self):
        self.logger = Logger(f"{self.LOGS_PATH}/{self.id}.log")

    def set_cookies(self, cookies: str) -> None:
        self.cookies = cookie_parser(cookies)

    def add_to_shared_data(self):
        shared_data = SharedData().get_data("scrapers")
        shared_data[self.__class__.__name__[:-7].lower()] = self
        self.shared_data.set_data("scrapers", shared_data)

    def get_logger(self):
        return self.logger

    def get_index_page(self):
        """获取目录页的HTML代码"""
        if not self.index_page_text:
            self.index_page_text = requests.get(
                self.index_url, headers=self.HEADERS
            ).text
        return self.index_page_text

    def get_title(self):
        """获取小说标题"""
        if self.id is None:
            raise ValueError("请设置小说ID！")

    def get_index(self):
        """获取小说目录"""
        self.get_title()

        # 检查是否已缓存
        if not self.db.table_exists(self.title):
            self.db.create_table(self.title)

    def get_picture(self):
        """获取小说封面"""

    def get_author(self):
        """获取小说作者"""
        self.get_index_page()
        author = ""
        return author

    def is_downloaded(self, chapter_title: str) -> bool:
        """检查是否已下载"""
        self.get_title()
        path = Path(f"{self.NOVELS_PATH}/{self.title}")
        files = path.glob("*.txt")
        for file in files:
            if file.stem == chapter_title:
                return True
        return False

    def check_full(self) -> bool:
        """检查是否已下载所有章节"""
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
        """保存小说"""
        novels_path = Path(self.NOVELS_PATH)
        chapter_path = Path(f"{chapter_title}.txt")
        title_path = novels_path / Path(title)
        final_path = title_path / chapter_path
        title_path.mkdir(exist_ok=True)
        with open(f"{final_path}", "w", encoding="utf-8") as f:
            f.write(chapter)

    def parse_chapter(
        self, chapter_response: str, chapter_title: str, index: int
    ) -> str:
        """解析章节内容并保存"""

    def fetch_chapter_callback(self, future) -> None:
        """下载章节回调函数"""
        self.progress_bar.update(1)
        result = future.result()
        chapter_response = result["chapter_response"]
        index = result["index"]
        chapter_title = self.download_list[index]
        self.parse_chapter(chapter_response, chapter_title, index)

    async def get_chapter(self) -> None:
        """利用协程获取所有未下载的章节"""
        self.get_index()

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

        tasks = []
        for i in range(download_length):
            task = asyncio.create_task(self.fetch_chapter(i))
            task.add_done_callback(self.fetch_chapter_callback)
            tasks.append(task)
        # tasks = [self.fetch_chapter(i) for i in range(download_length)]
        await asyncio.gather(*tasks)

    async def async_get(self, url: str, headers=None, cookies=None) -> str:
        async with self.sem:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers, cookies=cookies
                ) as response:
                    return await response.text()

    async def fetch_chapter(self, index: int) -> None:
        """获取单个章节"""
        chapter_title = self.download_list[index]
        set_title(f"ILP - {self.title} - {chapter_title}")
        if self.is_downloaded(chapter_title):
            self.logger.info(f"已经下载：{self.title}:{chapter_title}")
            self.progress_bar.update(1)
            return
