import hashlib


def md5(file_path):
    """
    计算文件的md5值
    :param file_path: 文件路径
    :return: md5值
    """
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def md5_str(string):
    """
    计算字符串的md5值
    :param string: 字符串
    :return: md5值
    """
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()
