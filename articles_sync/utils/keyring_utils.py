import keyring
from ..common.command_info import cache_info
from ..common.constants import KEYRING_PREFIX


def get_login_info(service: str):
    """获取登录信息"""
    key = KEYRING_PREFIX + "_" + service
    userName = cache_info['cache'].get(key, None)
    if userName is None:
        raise Exception(f"{key} not found in cache")
    password = keyring.get_password(key, userName)
    if password is None:
        raise Exception(f"{key} not found in keyring")
    return userName, password

