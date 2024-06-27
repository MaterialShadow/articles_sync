# 文章同步工具

本项目基于[DrissionPage](https://github.com/g1879/DrissionPage),用于同步本地markdown文件至csdn、知乎、掘金、简书平台。


## 目录

- [特性](#特性)
- [先决条件](#先决条件)
- [安装](#安装)
- [使用说明](#使用说明)

## 特性

- 支持CSDN、知乎、掘金、简书平台
- 支持markdown文件
- 支持将markdown中图片上传至PicGo图床(需先配置)
- 浏览器自动化操作

## 先决条件

- python环境
- chrome浏览器
- PicGo图床
- Windows平台(windows平台开发,只针对windows进行了测试)

## 安装

1. 克隆仓库到本地：
```bash
https://github.com/MaterialShadow/articles_sync.git
pip install -r requirements.txt
python setup.py bdist_wheel
cd dist 
pip install articles_sync-*-py3-none-any.whl
```
如果不起作用需要先将python环境的scripts目录添加到环境变量

或者直接`python main.py`


## 使用说明
### 所有参数
```bash
Usage: articles_sync [OPTIONS] COMMAND [ARGS]...

  文章同步工具,暂支持 csdn 知乎 简书 掘金

Options:
  --help  Show this message and exit.

Commands:
  config  配置信息
  login   平台登录,仅记录登录信息,密码存放在keyring中,无需担心被窃取
  sync    将本地markdown文件同步至平台
  upload  上传图片至图床
```

子命令帮助通过`--help`查看

### 配置
```bash
  配置信息

Options:
  --dp    drissionpage相关配置
  --pg    PicGo相关配置
  --help  Show this message and exit.
```
可以配置dp端口及chrome路径、pg图床ip及端口号

### 登录
此处是记录平台账号信息,存在keyring中,无需担心安全性问题


### markdown本地图片上传至图床
```bash
md_sync.exe upload --file "D:\md\test.md"
```

### 上传图片至平台
```bash
md_sync.exe sync --platform csdn --path "D:\md\test.md"
```
