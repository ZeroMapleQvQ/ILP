# -*- encoding: utf-8 -*-
"""
@File    :   ILP.py
@Time    :   2024/08/18 14:57:29
@Author  :   ZeroMaple
@Contact :   LingYingQvQ@gmail.com
"""

import click
import asyncio
from pathlib import Path

from utils.fanqie_decode import dec
from config import Config
from utils.utils import (
    show_banner,
    set_title,
    create_scraper_instance,
    load_plugins,
    SharedData,
)


cfg = Config()


load_plugins()
scrapers = SharedData().get_data("scrapers")


@click.group()
@click.option("--debug", "-d", is_flag=True, help="调试模式")
def main(**kwargs) -> None:
    set_title()
    show_banner()


@main.command(help="下载小说")
@click.option("--id", "-i", default=None, required=True, help="小说ID")
@click.option("--cookie", "-c", default=None, help="cookie")
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(scrapers),
)
def download(**kwargs):
    global logger
    ctx = click.get_current_context()
    debug = ctx.parent.params.get("debug")
    scraper = create_scraper_instance(
        site_name=kwargs["site"],
        book_id=kwargs["id"],
        cookies=kwargs.get("cookie", None),
        debug=debug,
    )
    logger = scraper.get_logger()
    asyncio.run(scraper.get_chapter())


@main.command(help="解码小说")
@click.option("--title", "-t", default=None, required=True, help="小说标题")
@click.option("--chapter_title", "-ct", default="all", help="小说章节标题,默认为全部")
def decode(**kwargs):
    ctx = click.get_current_context()
    debug = ctx.parent.params.get("debug")
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
            debug=debug,
        )


@main.command(help="获取小说章节目录并缓存到文件")
@click.option("--id", "-i", default=None, required=True, help="小说ID")
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(scrapers),
)
@click.option("--out_put_path", "-op", default=None, help="输出到文件")
@click.option(
    "--out_put_type",
    "-ot",
    default=None,
    help="输出格式",
    type=click.Choice(["html", "json", "csv"]),
)
def get_index(**kwargs):
    ctx = click.get_current_context()
    debug = ctx.parent.params.get("debug")
    scraper = create_scraper_instance(
        site_name=kwargs["site"],
        book_id=kwargs["id"],
        cookies=kwargs.get("cookie", None),
        debug=debug,
    )
    if kwargs["out_put_path"] is None and kwargs["out_put_type"] is None:
        scraper.get_index()
        print("缓存目录到数据库成功")
    elif kwargs["out_put_path"] is not None and kwargs["out_put_type"] is not None:
        scraper.get_index(
            export_path=kwargs["out_put_path"], export_type=kwargs["out_put_type"]
        )
        print(f"输出到{kwargs['out_put_path']}成功")
    else:
        print("输出路径和输出格式必须都指定或都不指定")


@main.command(help="获取小说封面")
@click.option("--id", "-i", default=None, required=True, help="小说ID", type=int)
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(scrapers),
)
def get_picture(**kwargs):
    ctx = click.get_current_context()
    debug = ctx.parent.params.get("debug")
    scraper = create_scraper_instance(
        site_name=kwargs["site"],
        book_id=kwargs["id"],
        cookies=kwargs.get("cookie", None),
        debug=debug,
    )
    picture_url = scraper.get_picture()
    print(f"封面地址: {picture_url}")


@main.command(help="获取小说作者")
@click.option("--id", "-i", default=None, required=True, help="小说ID", type=int)
@click.option(
    "--site",
    "-s",
    default=None,
    required=True,
    help="站点名称",
    type=click.Choice(scrapers),
)
def get_author(**kwargs):
    ctx = click.get_current_context()
    debug = ctx.parent.params.get("debug")
    scraper = create_scraper_instance(
        site_name=kwargs["site"],
        book_id=kwargs["id"],
        cookies=kwargs.get("cookie", None),
        debug=debug,
    )
    author = scraper.get_author()
    print(f"作者: {author}")


if __name__ == "__main__":
    main()
