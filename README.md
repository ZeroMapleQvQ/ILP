# Novel Scraper

## 介绍

此项目支持多个小说网站内容爬取, 包括:
- [x] [番茄免费小说](https://fanqienovel.com "番茄免费小说")
    - [x] 标题
    - [x] 正文
    - [x] 作者
    - [x] 封面
- [ ] [飞卢小说](https://faloo.com "飞卢小说")
    - [x] 标题
    - [ ] 正文
    - [x] 作者
    - [x] 封面
- [ ] [起点中文网](https://qidian.com "起点中文网")
    - [x] 标题
    - [ ] 正文
    - [x] 作者
    - [ ] 封面
- [ ] 更多...

(目前飞卢小说和起点中文网要通过添加cookie的方式爬取, 故算作未实现)

## 使用

### 从源代码构建/运行

#### 运行
1. 克隆本项目`git clone https://github.com/ZeroMapleQvQ/novel_scraper`
2. 切换到项目目录`cd novel_scraper`
3. 安装依赖`pip install -r requirements.txt`
4. 运行`python novel_scraper.py --help`获取帮助信息

#### 编译
**重要: 请使用与开发环境一致的Python版本(>=3.12)**

1. 克隆本项目`git clone https://github.com/ZeroMapleQvQ/novel_scraper`
2. 切换到项目目录`cd novel_scraper`
3. 安装依赖`pip install -r requirements.txt`
4. 安装Pyinstaller`pip install pyinstaller`
5. 执行`pyinstaller -F novel_scraper.py`进行编译
6. 切换到dist目录`cd ./dist`
7. 运行`novel_scraper.exe --help`获取帮助信息

### 使用二进制文件(Windows Only)
1. 从Github release下载可执行文件
2. 运行`novel_scraper.exe --help`获取帮助信息

## 注意事项
- 请不要滥用本程序, 且用且珍惜
- 用户使用本程序造成的一切后果请自行承担
- 通过本程序爬取的小说需遵守相应网站的版权声明
- 本程序仅供学习交流使用, 请勿用于商业用途
- 本项目是本人写的第一个真正意义上的Python项目, 可能存在许多问题, 还请批评指正