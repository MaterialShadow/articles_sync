import logging as log

import click
import keyring
from DrissionPage import ChromiumPage, ChromiumOptions
from diskcache import Cache

from articles_sync.common import constants
from articles_sync.common.command_info import info, cache_info
from articles_sync.service.csdn.csdn import Csdn
from articles_sync.service.jianshu.jianshu import JianShu
from articles_sync.service.juejin.juejin import Juejin
from articles_sync.service.zhihu.zhihu import ZhiHu
from articles_sync.utils.md_utils import MdUtils
from pathlib import Path

log.basicConfig(level=log.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

page = None
cache_info['cache'] = Cache(str(Path.home().joinpath('.diskcache').joinpath("..").resolve()))


@click.group()
def cli():
    """文章同步工具,暂支持 csdn 知乎 简书 掘金"""
    pass


@cli.command()
@click.option('--dp', is_flag=True, help='drissionpage相关配置')
@click.option('--pg', is_flag=True, help='PicGo相关配置')
def config(dp, pg):
    """配置信息"""
    if dp:
        port = click.prompt("请输入dp启动端口,默认9225", default=constants.DRISSIONPAGE_DEFAULT_PORT, type=int)
        store = Path.home().joinpath('.drissionpage', str(port))
        data_path = click.prompt("请输入dp启动数据目录,默认为%s" % store, default=store)
        if Path(data_path).exists():
            Path(data_path).mkdir(parents=True, exist_ok=True)
        # 保存配置信息
        cache_info['cache'].set(constants.DRISSIONPAGE_PREFIX + "_port", port)
        cache_info['cache'].set(constants.DRISSIONPAGE_PREFIX + "_store", data_path)
    if pg:
        ip = click.prompt("请输入PicGo的ip,默认127.0.0.1", default=constants.PICGO_DEFAULT_IP)
        port = click.prompt("请输入PicGo的端口,默认36677", default=constants.PICGO_DEFAULT_PORT, type=int)
        # 保存配置信息
        cache_info['cache'].set(constants.PICGO_PREFIX + "_ip", ip)
        cache_info['cache'].set(constants.PICGO_PREFIX + "_port", port)


@cli.command()
@click.option('--platform', type=click.Choice(['csdn', 'zhihu', 'juejin', 'jianshu']), prompt='选择要登录的平台')
def login(platform):
    """平台登录,仅记录登录信息，密码存放在keyring中,无需担心被窃取"""
    username = click.prompt('请输入%s的用户名' % info[platform])
    # 使用 hide_input=True 来隐藏密码输入
    password = click.prompt('请输入%s的密码' % info[platform], hide_input=True)
    log.info("密码信息登记完成")
    keyring.set_password(constants.KEYRING_PREFIX + "_" + platform, username, password)
    cache_info['cache'].set(constants.KEYRING_PREFIX + "_" + platform, username)


@cli.command()
@click.option('--file', default="", help='文件路径')
def upload(file):
    """上传图片至图床"""
    file_path = Path(file)
    if not file_path.exists():
        log.error("文件不存在")
        return
    md = MdUtils(file_path)
    md.upload_local_imgs()

@cli.command()
@click.option('--platform', type=click.Choice(['csdn', 'zhihu', 'juejin', 'jianshu']), prompt='选择要同步的平台')
@click.option('--file', default="", help='文件路径')
def sync(platform, file):
    """将本地markdown文件同步至平台"""
    if file == "":
        file = click.prompt('请输入要同步的文件路径')
    file_path = Path(file)
    if not file_path.exists():
        log.error("文件不存在")
        return
    md = MdUtils(file_path)
    if md.local_images:
        log.error("检测到存在本地图片,请先将图片上传至图床")
        return
    md.img2local()
    if not page:
        init_page()
    # 同步文章
    if platform == "csdn":
        site = Csdn(page)
        log.info("csdn")
    elif platform == "zhihu":
        site = ZhiHu(page)
        log.info("zhihu")
    elif platform == "juejin":
        site = Juejin(page)
        log.info("juejin")
    elif platform == "jianshu":
        site = JianShu(page)
        log.info("jianshu")
    else:
        log.error("暂不支持该平台")
        return
    site.check_tab()
    site.login()
    site.write_article(file)


def init_page():
    port = cache_info['cache'].get(constants.DRISSIONPAGE_PREFIX + "_port", constants.DRISSIONPAGE_DEFAULT_PORT)
    store = cache_info['cache'].get(constants.DRISSIONPAGE_PREFIX + "_store",
                                    Path.home().joinpath('.drissionpage', str(port)))
    # 设置浏览器参数
    co = ChromiumOptions().set_local_port(port).set_user_data_path(store)
    global page
    page = ChromiumPage(addr_or_opts=co)
    page.set.window.max()