import logging as log


def tab_to_link(page, link: str):
    tabs = page.get_tabs()
    # 获取tab数量
    log.info(f"current tab count is:{len(tabs)}")
    for tab in tabs:
        log.info(f"标题:{tab.title},url:{tab.url},link:{link},link in tab:{link in tab.url}")
        if link in tab.url:
            return tab
    return None


