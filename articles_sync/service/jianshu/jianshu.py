import logging as log
import time

from articles_sync.service.base.base import PlatformBase
from articles_sync.utils.drissionpage_utils import tab_to_link
from articles_sync.utils.keyring_utils import get_login_info
from articles_sync.utils.md_utils import MdUtils
from pathlib import Path
import re


class JianShu(PlatformBase):
    def __init__(self, page):
        super().__init__(page)

    def check_login(self):
        if "sign_in" in self.tab.url:
            return False, None
        login_ele = self.tab.ele('x://a[@id="sign_in"]', timeout=3)
        if not login_ele:
            log.info("已经登录")
            return True, None
        log.info("未登录")
        return False, None

    def check_tab(self):
        self.tab = self.get_tab("jianshu.com", "https://www.jianshu.com/")


    def login(self):
        login_flag, login_ele = self.check_login()
        if login_flag:
            return
        self.tab.get("https://www.jianshu.com/sign_in")
        userName, password = get_login_info('jianshu')
        log.info("用户名:{}".format(userName))
        self.tab.ele('#session_email_or_mobile_number').input(userName)
        self.tab.ele('#session_password').input(password)
        self.tab.ele('#sign-in-form-submit-btn').click()

        log.info("等待登录")
        self.tab.ele('x://div[@class="user"]//a[@class="avatar"]', timeout=300).wait.displayed(timeout=300)
        log.info("登录完成")

    def write_article(self, file_path):
        log.info("开始写文章")
        url = "https://www.jianshu.com/"
        if self.tab.url != url:
            self.tab.get(url)
        self.tab.ele('x://a[contains(@href,"write")]').click()
        #切换到https://www.jianshu.com/writer#/notebooks
        tab = tab_to_link(self.page, "www.jianshu.com/writer")
        if not tab:
            raise Exception("没有找到创作页面")

        log.info("切换到简书写作页面")
        tab.ele('x://span[text()="新建文章"]').click()
        #刷新
        tab.refresh()
        tab.ele('x://a[@data-action="to-preview"]').click()
        if not file_path:
            log.info("没有文章")
            return
        md = MdUtils(file_path)
        infos = md.link_rel_info
        content = md.content_without_toc
        for link in infos:
            real_path = md.img_dir_path.joinpath(infos[link])
            if not Path(real_path).exists():
                continue
            log.info(f"link:{link},real_path:{real_path}")
            # 清空编辑框内容
            tab.ele('#arthur-editor').clear(by_js=True)
            tab.ele('x://a[@data-action="openImageModal"]').click()
            #点击上传
            tab.ele('x://label[@for="kalamu-upload-image"]').click.to_upload(real_path)
            time.sleep(1.5)
            # 获取编辑框内容
            urlContent = tab.ele('#arthur-editor').value
            # 匹配图片链接
            matches = re.findall(r'!\[.*?\]\((.*?)\)', urlContent, re.DOTALL)
            if matches:
                url = matches[0]
                content = content.replace(link, url)
            time.sleep(3)
        tab.ele('#arthur-editor').input(content,clear=True)
        tab.ele('x://textarea[@id="arthur-editor"]/preceding-sibling::input').input(md.title,clear=True)
        # 点击保存
        tab.ele('x://a[@data-action="auto-save"]').click(by_js=True)
        # 关闭tab
        tab.close()

