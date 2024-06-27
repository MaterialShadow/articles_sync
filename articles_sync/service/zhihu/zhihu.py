import logging as log
import time
from pathlib import Path

from DrissionPage.common import Keys

from articles_sync.service.base.base import PlatformBase
from articles_sync.utils.keyring_utils import get_login_info
from articles_sync.utils.md_utils import MdUtils


class ZhiHu(PlatformBase):
    def __init__(self, page):
        super().__init__(page)

    def check_login(self):
        if "signin" in self.tab.url:
            return False, None
        else:
            log.info("已经登录")
            return True, None

    def check_tab(self):
        self.tab = self.get_tab("csdn.net", "https://www.zhihu.com/")

    def login(self):
        login_flag, login_ele = self.check_login()
        if login_flag:
            return
        userName, password = get_login_info('zhihu')
        log.info("用户名:{}".format(userName))
        log.info("密码:{}".format(password))
        self.tab.ele('x://div[@role="button"][text()="密码登录"]').click()
        self.tab.ele('x://input[@name="username"]').input(userName)
        self.tab.ele('x://input[@name="password"]').input(password)
        self.tab.ele('x://button[@type="submit"]').click()
        try:
            self.page.ele('x://span[text()="请完成安全验证，可使用语音验证"]', timeout=3)
            log.info("请先完成安全验证")
        except Exception:
            pass
        log.info("登录中...")
        self.page.ele('x://div[text()="创作中心"]', timeout=300).wait.displayed(timeout=300)
        log.info("登录完成")

    def write_article(self, file_path):
        log.info("开始写文章")
        # 跳转到创作中心
        self.tab.get('https://zhuanlan.zhihu.com/write')
        self.tab.ele('x://div[@class="Popover"]//button[@aria-label="文档"]').click()
        self.tab.ele('x://div[@class="Menu"]//button[@aria-label="文档"]').click()
        if not file_path:
            log.info("没有文章")
            return
        if not Path(file_path).exists():
            log.info("文章不存在")
            return
        self.tab.ele('x://div[@class="Editable-docModal-uploader-icon"]').click.to_upload(file_path)
        # 设置标题
        self.tab.ele('x://textarea[contains(@placeholder,"请输入标题")]').input(Path(file_path).stem)
        # 尝试删除[Toc]
        try:
            md = MdUtils(file_path)
            if "[Toc]" in md.content:
                time.sleep(2)
                toc_ele = self.page.ele('x://span[text()="[Toc]"]')
                toc_ele.click.at(offset_x=toc_ele.rect.size[0], offset_y=0)
                self.tab.actions.type(Keys.BACKSPACE).type(Keys.BACKSPACE).type(Keys.BACKSPACE).type(
                    Keys.BACKSPACE).type(
                    Keys.BACKSPACE)
        except Exception:
            log.info("删除Toc失败")
        # 点击目录
        self.tab.ele('x://span[text()="目录"]').click()
        time.sleep(3)  # 等待目录生成
        # 回到创作者中心 草稿箱
        self.tab.get("https://www.zhihu.com/creator/manage/creation/draft?type=article")
