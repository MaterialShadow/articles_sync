from pathlib import Path
from urllib.parse import unquote
import re
from datetime import datetime
import logging as log
import requests
from .md5_utils import md5_str
from .picGo_utils import PicGoUtils
import shutil
import json

log.basicConfig(level=log.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def decode_image_link(link):
    return unquote(link)


class MdUtils(object):
    def __init__(self, md_path):
        if isinstance(md_path, Path):
            md_path = str(md_path.resolve())
        if md_path.endswith('.md'):
            if Path(md_path).exists():
                self.md_path = Path(md_path)
            else:
                raise Exception('上传的md文件不存在')
        else:
            raise Exception('上传的不是md文件')
        self.image_pattern = r'!\[.*?\]\((.*?)\)'

    @property
    def content(self):
        """markdown文件的内容"""
        with open(self.md_path.resolve(), 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    @property
    def content_without_toc(self):
        """markdown文件的内容,去除了[Toc]"""
        return self.content.replace("[Toc]", "")

    @property
    def title(self):
        """markdown文件的标题,不包含文件后缀"""
        return Path(self.md_path).stem

    @property
    def links(self):
        """
        获取图片链接列表。

        该属性通过正则表达式匹配内容中的图片链接模式，并将匹配到的链接解码后添加到列表中。
        这样做的目的是为了从文档内容中提取出所有图片的链接，以便进一步处理或使用。

        Returns:
            list: 包含所有解码后图片链接的列表。
        """
        # 使用re.findall来找到所有的匹配项
        matches = re.findall(self.image_pattern, self.content, re.DOTALL)
        return [[decode_image_link(match), match] for match in matches]

    @property
    def local_images(self):
        """
        返回一个列表，列表中的每一项都是图片的本地链接
        列表中每一项为一个列表
            第一项为链接
            第二项为解码后链接
        """
        return [[item[0], item[1]] for item in self.links if not item[1].startswith('http')]

    def backup(self):
        """
        创建当前Markdown文件的备份。

        备份文件的命名规则是在原文件名基础上加上时间戳，格式为YYYYMMDDHHMMSS。
        这样可以确保备份文件的名称是唯一的，避免覆盖之前的备份。
        """
        target = self.md_path.parent.joinpath(self.md_path.stem + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".md")
        # 创建备份文件
        shutil.copy(self.md_path, target)

    def upload_local_imgs(self):
        """
        上传本地图片到图床并更新Markdown文件中的图片链接。

        此方法遍历配置的本地图片链接列表，使用PicGo工具将图片上传到图床，
        然后替换Markdown文件中相应的本地链接为图床链接。在操作前会先备份原Markdown文件。

        注意: 图片上传失败或图片文件不存在时，将不会进行链接替换或采取其他错误处理措施。
        """
        links = self.local_images  # 获取本地图片链接列表
        if not links:
            log.info("No local images found.")
            return
        log.info(f"Preparing to upload images: {links}")  # 记录日志

        picGo = PicGoUtils()  # 初始化图床客户端

        # 为了防止原始内容被无意修改，先备份内容
        original_content = self.content
        self.backup()  # 执行备份操作

        for link in links:
            log.info(f"Processing image: {link[1]}")  # 记录当前处理的图片

            file_path = self.md_path.parent.joinpath(link[0])  # 构建图片绝对路径
            resolved_path = file_path.resolve()  # 解析路径确保绝对

            if not resolved_path.exists():  # 跳过不存在的图片文件
                continue

            try:
                url = picGo.upload_file(str(resolved_path))  # 尝试上传图片并获取URL
                if url:  # 仅当URL有效时才替换
                    original_content = original_content.replace(link[1], url)  # 更新Markdown内容中的链接
            except Exception as e:  # 异常处理（可根据需要细化）
                log.error(f"Failed to upload {link}: {e}")
                continue  # 遇到错误继续处理下一张图片
        log.info("图片上传完成")
        # 检查内容是否有变更，如有则写回文件
        if self.content != original_content:
            with open(self.md_path, 'w', encoding='utf-8') as f:
                f.write(original_content)  # 写入更新后的内容到Markdown文件
        log.info("图片链接更新完成")

    @property
    def img_dir_path(self):
        """
        获取图片文件夹路径。
        """
        return Path(self.md_path.parent, self.title)

    def img2local(self):
        """
           将Markdown文档中的图片链接下载到以其标题命名的本地文件夹中。

           - 确认所有链接均以'http'或'https'开头。
           - 在Markdown文件的父目录下创建一个与文档标题同名的目录。
           - 为每个图片生成一个基于其MD5哈希值和原扩展名的新文件名并下载保存。
           - 记录操作开始与结束的日志信息。

           :raises Exception: 如果有任何链接不是以'http'或'https'开头。
           """
        # 首先创建一个同名文件夹
        img_dir = self.img_dir_path
        if img_dir.exists():
            log.warning(f"{img_dir}已存在，跳过下载。")
            return
        img_dir.mkdir()
        log.info(f"{img_dir}创建成功")
        links = self.links
        # 检验所有链接是否为网页链接
        for link in links:
            if not link[0].startswith(('http:', 'https:')):
                log.warning(f"图片链接 {link[0]} 不是以 'http://' 或 'https://' 开头，请先上传至图床。")
                raise Exception("图片需先上传至图床（链接应以 'http://' 或 'https://' 开头）。")
        log.info("开始图片下载流程。")
        log.info("一共:%s张图片" % len(links))
        log.info("start saving imgs")
        count = 0
        link_rel_info = {}
        for link in links:
            img_path = Path(img_dir, md5_str(link[0]) + "." + link[0].split('.')[-1])
            # 下载并保存图片
            response = requests.get(link[0], stream=True)
            if response.status_code == 200:
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                    count += 1
                    link_rel_info[link[0]] = img_path.name
            else:
                log.warning(f"无法下载 {link}。服务器响应状态码为 {response.status_code}。")
        log.info(link_rel_info)
        # 写入link_rel_info到json文件
        json_string = json.dumps(link_rel_info, indent=4)
        with open(Path(img_dir, "link_rel_info.json"), "w") as f:
            f.write(json_string)
        log.info(f"下载 {count}/{len(links)} 张图片。")
        log.info("图片下载完毕。")

    @property
    def link_rel_info(self):
        """
        返回一个图片映射关系列表
        """
        json_path = self.img_dir_path.joinpath("link_rel_info.json")
        if not json_path.exists():
            return []
        with open(json_path, "r") as f:
            return json.load(f)
