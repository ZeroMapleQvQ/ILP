# ILP

## 关于ILP
本项目名称来源于动漫作品「魔法禁书目录」中的「禁书目录」（Index-Librorum-Prohibitorum）的缩写。意指本程序的功能是获取「禁书」。

「ILP」可以有多个含义，包括：

(以下内容使用ChatGPT生成)

~~(ILP无确切的含义，选择一个你喜欢的就好)~~

- Internet Literature Puller（互联网文学抓取器）
- Ingenious Literature Picker（巧妙文学选择器）
- Internet Literature Profiler（互联网文学剖析器）

## 介绍

此项目支持多个小说网站内容爬取，包括：
- [x] [番茄免费小说](https://fanqienovel.com "番茄免费小说")
    - [x] 标题
    - [x] 正文
    - [x] 作者
    - [ ] 封面
- [x] [起点中文网](https://qidian.com "起点中文网")
    - [x] 标题
    - [x] 正文
    - [x] 作者
    - [x] 封面
- [ ] [飞卢小说](https://faloo.com "飞卢小说")
    - [x] 标题
    - [ ] 正文
    - [x] 作者
    - [x] 封面
- [ ] 更多...

## 特性
- 使用协程
- 断点续传
- 下载进度条
- 缓存目录到数据库
- 保存为多章节文件

## TODO
- [ ] 支持选择爬取范围
- [ ] 支持单文件输出
- [ ] 支持缓存目录到Excel文件
- [ ] 支持缓存目录到Redis
- [ ] 支持跨平台（当前未测试在*Unix系统上是否可运行）

## 使用

### 从源代码构建/运行

#### 运行
1. 克隆本项目`git clone https://github.com/ZeroMapleQvQ/ILP`
2. 切换到项目目录`cd ILP`
3. 安装依赖`pip install -r requirements.txt`
4. 运行`python novel_scraper.py --help`获取帮助信息

#### 编译
**重要：请使用与开发环境一致的Python版本（>=3.12）**

**本程序未能成功使用nuitka编译**

1. 克隆本项目`git clone https://github.com/ZeroMapleQvQ/ILP`
2. 切换到项目目录`cd ILP`
3. 安装依赖`pip install -r requirements.txt`
4. 安装Pyinstaller`pip install pyinstaller`
5. 执行`pyinstaller -F ILP.py`进行编译
6. 切换到dist目录`cd dist`
7. 运行`ILP.exe --help`获取帮助信息

### 使用二进制文件（Windows And Linux）

#### Windows
1. 从Github Actions页面下载压缩包（ILP-windows-latest-{commit-id}）
2. 解压
3. 运行`ILP-windows-latest-{commit-id}.exe --help`获取帮助

#### Linux
1. 从Github Actions页面下载压缩包（ILP-ubuntu-latest-{commit-id}）
2. 解压
3. 运行`ILP-ubuntu-latest-{commit-id} --help`获取帮助

## 注意事项
- 请不要滥用本程序，且用且珍惜
- 用户使用本程序造成的一切后果请自行承担
- 通过本程序爬取的小说需遵守相应网站的版权声明
- 本程序仅供学习交流使用，请勿用于商业用途
- 本项目是本人第一个真正意义上的Python项目，可能存在许多问题，还请批评指正
