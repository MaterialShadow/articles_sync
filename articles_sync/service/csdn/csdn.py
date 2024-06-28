import logging as log
import time
from pathlib import Path

from DrissionPage.common import Keys

from ..base.base import PlatformBase
from ...utils.keyring_utils import get_login_info


class Csdn(PlatformBase):
    def __init__(self, page):
        super().__init__(page)

    def check_login(self):
        login_ele = self.tab.ele('x://a[@class="toolbar-btn-loginfun"]', timeout=2)
        if login_ele:
            log.info("未登录,准备登录")
            return False, login_ele
        else:
            log.info("已经登录")
            return True, login_ele

    def check_tab(self):
        self.tab = self.get_tab("csdn.net", "https://www.csdn.net/")

    def login(self):
        login_flag, login_ele = self.check_login()
        log.info(login_flag)
        if login_flag:
            return
        # 点击登录
        log.info("点击登录")
        login_ele.click()
        # 获取用户名
        userName, password = get_login_info('csdn')
        log.info("用户名:{}".format(userName))
        self.tab.ele("x://span[text()='密码登录']").click()
        self.tab.ele('x://input[@placeholder="手机号/邮箱/用户名"]').input(userName)
        self.tab.ele('x://input[@placeholder="密码"]').input(password)
        self.tab.ele('x://i[@class="icon icon-nocheck"]').click()
        self.tab.ele('x://button[text()="登录"]').click()
        log.info("登录完成")

    def write_article(self, file_path):
        log.info("开始写文章")
        # 跳转到创作中心
        self.tab.get("https://mp.csdn.net/")
        self.tab.ele('x://a[contains(text(),"发布")]//span').hover()
        self.tab.ele('x:(//ul[@class="createList"]/li)[1]').click()
        # 情况编辑器内容
        self.tab.actions.move_to('x://div[@class="editor"]/pre').click().type(Keys.CTRL_A).type(Keys.BACKSPACE)
        if not file_path:
            log.info("没有文章")
            return
        if not Path(file_path).exists():
            log.info("文章不存在")
            return
        self.tab.ele('x://label[@data-title="导入"]').click.to_upload(file_path)
        # 保存草稿
        self.tab.ele('x://button[contains(text(),"保存草稿")]').click()
        time.sleep(3)
        # 回到创作中心
        self.tab.get("https://mp.csdn.net/")
