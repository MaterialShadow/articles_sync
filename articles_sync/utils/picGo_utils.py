import json

import requests
from ..common.command_info import cache_info
from ..common import constants

class PicGoUtils:
    """
    参考
    https://picgo.github.io/PicGo-Doc/zh/guide/advance.html#linux
    """

    def __init__(self):
        ip = cache_info['cache'].get(constants.PICGO_PREFIX + "_ip", constants.PICGO_DEFAULT_IP)
        port = cache_info['cache'].get(constants.PICGO_PREFIX + "_port", constants.PICGO_DEFAULT_PORT)
        self.url = "http://%s:%s/upload" % (ip, port)

    def upload_paste(self):
        url = self.url + ""
        res = requests.post(url)
        print(res)

    def upload_file(self, file_path: str):
        if not isinstance(file_path, str):
            raise Exception("file_path must be str")
        file_list = []
        data = {"list": file_list}
        # 判断file_path是否是列表
        file_list.append(file_path)
        res = requests.post(self.url, data=json.dumps(data))
        if res.status_code == 200:
            return res.json()['result'][0]
        else:
            return ""
