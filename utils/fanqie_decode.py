import logging
from pathlib import Path
from log import Logger
from utils.map import ascii_map

map_ascii_keys = [i for i in ascii_map.keys()]


def decode_ascii(string):
    ascii_code = str(ord(string))
    # print(ascii_code)
    if ascii_code in map_ascii_keys and ascii_map[ascii_code] != "":
        return str(ascii_map[ascii_code])
    else:
        return string


async def dec(
    chapter_title,
    title,
    suffix="",
    log_path="./logs",
    novels_path="./novels",
    novels_new_path="./novels_new",
    debug=False,
):
    new_context = []
    # context = []
    # files = os.listdir(novels_path)

    novels_path = Path(novels_path)
    novels_new_path = Path(novels_new_path)
    log_path = Path(log_path)
    novels_path.mkdir(exist_ok=True)
    novels_new_path.mkdir(exist_ok=True)
    log_path.mkdir(exist_ok=True)

    title_path = Path(title)
    chapter_path = Path(f"{chapter_title}.txt")
    chapter_path_with_suffix = Path(f"{chapter_title}{suffix}.txt")
    old_path = novels_path / title_path
    new_path = novels_new_path / title_path

    old_path.mkdir(exist_ok=True)
    new_path.mkdir(exist_ok=True)

    if debug:
        logger = Logger.get_logger(f"{log_path}/{title}.log", log_level=logging.DEBUG)
    else:
        logger = Logger.get_logger(f"{log_path}/{title}.log")
    # print(title)
    # print(f"{title}:{content_title} 转码中...")
    logger.info(f"开始转码：{title}:{chapter_title}")
    with open(old_path / chapter_path, "r", encoding="utf-8", errors="ignore") as f:
        # with open(f"{novels_path}/{title}/{content_title}.txt", "r", encoding="utf-8", errors="ignore") as f:
        context = f.read()
    cache_str = ""
    for j in context:
        # print(f"{j} --> {ord(j)}")
        cache_str += decode_ascii(j)
        # print(encode_ascii(j))
    new_context.append(cache_str)
    with open(new_path / chapter_path_with_suffix, "w", encoding="utf-8") as f:
        # with open(f"{novels_new_path}{title}/{content_title}{suffix}.txt", "w", encoding="utf-8") as f:
        f.write(cache_str)
    # print(f"{title}:{content_title} 转码完成！")
    logger.info(f"转码完成：{title}:{chapter_title}")
