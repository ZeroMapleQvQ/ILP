import json
import re
import time
import requests
from db import DB
from bs4 import BeautifulSoup
from utils.utils import string_to_md5
from scraper.base_scraper import BaseScraper


class FanqieScraper(BaseScraper):
    def __init__(self, book_id: int = None, alias: str = None, cookies=None) -> None:
        super().__init__(book_id, alias, cookies)
        self.base_url = "https://fanqienovel.com"
        self.index_url = f"https://fanqienovel.com/page/{book_id}"
        self.index_api_url = (
            "https://fanqienovel.com/api/reader/directory/detail?bookId="
        )
        self.chapter_api_url = (
            "https://novel.snssdk.com/api/novel/reader/full/v1/?item_id="
        )
        self.index_page_text = self.get_index_page()

    def get_title(self):
        super().get_title()
        if self.title is None:
            json_data = requests.get(
                f"https://api5-normal-sinfonlineb.fqnovel.com/reading/bookapi/multi-detail/v/?aid=1967&iid=1&version_code=999&book_id={self.id}",
                headers=self.HEADERS,
            ).json()
            self.title = json_data["data"][0]["book_name"]
            return self.title
        else:
            return self.title

    def get_index(self, export_path: str = None, export_type: str = None) -> list:
        super().get_index()
        if self.db.is_table_empty(self.title):
            index_api_page_response = requests.get(
                f"{self.index_api_url}{self.id}", headers=self.HEADERS
            ).json()
            index_data = index_api_page_response["data"]
            chapter_list = index_data["chapterListWithVolume"]
            for volumes in chapter_list:
                for chapter in volumes:
                    chapter_title = chapter["title"]
                    chapter_url = f"https://fanqienovel.com/reader/{chapter["itemId"]}"
                    chapter_id = chapter["itemId"]
                    chapter_md5_id = string_to_md5(chapter_id)
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
            return []
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

    def parse_chapter(
        self, chapter_response: str, chapter_title: str, index: int
    ) -> None:
        db = DB(self.DB_PATH)

        chapter_response = json.loads(chapter_response)
        chapter_main = re.sub(r"(<.*?>)+", "\n", chapter_response["data"]["content"])
        chapter_head = chapter_title + "\n---\n\n"
        chapter_sum = chapter_response["data"]["novel_data"]["word_number"]
        chapter_md5 = string_to_md5(self.index_chapter_id_list[index])
        self.save_novel(self.title, chapter_head + chapter_main, chapter_title)
        self.logger.info(f"下载完成：{self.title}:{chapter_title}")

        db.update_data(self.title, "chapter_sum", chapter_sum, "md5_id", chapter_md5)

        del db

    async def fetch_chapter(self, index: int) -> None:
        await super().fetch_chapter(index)

        response = await self.async_get(
            url=f"{self.chapter_api_url}{self.index_chapter_id_list[index]}",
            headers=self.HEADERS,
            cookies=self.cookies,
        )

        chapter_response = response
        time.sleep(self.SLEEP_TIME)
        return {
            "chapter_response": chapter_response,
            "index": index,
            "chapter_title": self.index_chapter_title_list[index],
        }
