import logging as log
import re
import time
from pathlib import Path

from DrissionPage.common import Keys

from articles_sync.service.base.base import PlatformBase
from articles_sync.utils.keyring_utils import get_login_info
from articles_sync.utils.md_utils import MdUtils


class Juejin(PlatformBase):
    def __init__(self, page):
        super().__init__(page)
        self.tab = None

    def check_login(self):
        login_ele = self.tab.ele('x://button[contains(text(),"登录")][@class="login-button"]', timeout=3)
        if not login_ele:
            log.info("已经登录")
            return True, None
        log.info("未登录")
        return False, login_ele

    def check_tab(self):
        self.tab = self.get_tab("juejin.cn", "https://juejin.cn/")

    def login(self):
        login_flag, login_ele = self.check_login()
        if login_flag:
            return
        login_ele.click()
        userName, password = get_login_info('juejin')
        log.info("用户名:{}".format(userName))
        log.info("密码:{}".format(password))
        self.tab.ele('x://form[@class="auth-form"]//span[contains(text(),"密码登录")]').click()
        self.tab.ele('x://form[@class="auth-form"]//input[@name="loginPhoneOrEmail"]').input(userName)
        self.tab.ele('x://form[@class="auth-form"]//input[@name="loginPassword"]').input(password)
        self.tab.ele('x://form[@class="auth-form"]//button[contains(text(),"登录")]').click()
        try:
            self.tab.ele('x://div[contains(text(),"请完成下列验证后继续")]', timeout=3)
            log.info("请先进行验证码验证")
        except Exception:
            log.info("没有验证码")
        log.info("登录中...")
        self.tab.ele('x://img/parent::div[contains(@class,"avatar")]', timeout=300).wait.displayed(timeout=300)
        log.info("登录完成")

    def write_article(self, file_path):
        log.info("开始写文章")
        url = "https://juejin.cn/editor/drafts/new?v=2"
        if self.tab.url != url:
            self.tab.get(url)
        if not file_path:
            log.info("没有文章")
            return
        if not Path(file_path).exists():
            log.info("文章不存在")
            return
        juejin_path = Path(file_path).parent.joinpath(Path(file_path).stem+"_juejin.md")

        md = MdUtils(file_path)
        infos = md.link_rel_info
        if infos:
            content = md.content_without_toc
            for link in infos:
                real_path = md.img_dir_path.joinpath(infos[link])
                if not Path(real_path).exists():
                    continue
                self.tab.ele('x://div[@class="bytemd-toolbar-left"]/div[@bytemd-tippy-path="5"]').click.to_upload(real_path)
                time.sleep(5)
                urlContent = self.tab.ele('x://div[@class="CodeMirror-scroll"]').text.strip()
                matches = re.findall(r'!\[.*?\]\((.*?)\)', urlContent, re.DOTALL)
                log.info(matches)
                if matches:
                    url = matches[0]
                    log.info(url)
                    content = content.replace(link, url)
                # 清空
                self.tab.actions.move_to('x://div[@class="CodeMirror-scroll"]').click().type(Keys.CTRL_A).type(
                    Keys.BACKSPACE)
            # 写入文章
            with open(juejin_path.resolve(), "w", encoding="utf-8") as f:
                f.write(content)

        # 上传markdown
        self.tab.ele(
            'x://div[@class="bytemd-toolbar-right"]/div[contains(@class,"bytemd-toolbar-icon")][last()]').click()
        self.tab.ele('x://div[@class="upload-area"]//span[contains(text(),"上传文档")]').click.to_upload(juejin_path.resolve())
        # 设置标题
        self.tab.ele('x://input[contains(@placeholder,"输入文章标题")]').input(Path(file_path).stem)
        # 滚动到顶部
        self.tab.ele('x://div[@class="CodeMirror-vscrollbar"]').scroll.to_top()
        try:
            # 尝试删除[Toc]
            time.sleep(2)
            toc_ele = self.page.ele('x://span[text()="[Toc]"]')
            toc_ele.click.at(offset_x=toc_ele.rect.size[0], offset_y=0)
            self.tab.actions.type(Keys.BACKSPACE).type(Keys.BACKSPACE).type(Keys.BACKSPACE).type(Keys.BACKSPACE).type(
                Keys.BACKSPACE)
        except Exception:
            pass
        # 删除掘金
        juejin_path.unlink()
        # 返回创作者页面
        self.tab.get("https://juejin.cn/creator/content/article/drafts")
