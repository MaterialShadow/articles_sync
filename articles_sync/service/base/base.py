import logging as log


class PlatformBase(object):
    def __init__(self, page):
        self.page = page

    def get_tab(self, link, open_url):
        """获取标签页"""
        for tab in self.page.get_tabs():
            log.info(f"标题:{tab.title},url:{tab.url},link:{link},link in tab:{link in tab.url}")
            if link in tab.url:
                return tab
        return self.page.new_tab(open_url)

    def check_login(self):
        """检查是否登录"""
        pass

    def check_tab(self):
        """检查tab中是否已经包含目标网站"""
        pass

    def login(self):
        """登录"""
        pass

    def write_article(self, file_path):
        """写文章"""
        pass
