import json
from typing import Union, Optional


def json_load(path) -> Optional[dict]:
    """
    加载json文件
    :return: Optional[dict]
    """
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            contents = json.load(f)
            return contents
    except FileNotFoundError:
        return None


def json_upload(path, dict_content) -> None:
    """
    更新json文件
    :param path: 路径
    :param dict_content: python对象，字典
    """
    with open(path, mode='w', encoding='utf-8') as c:
        c.write(json.dumps(dict_content, ensure_ascii=False, indent=2))