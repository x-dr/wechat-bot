from utils.utils import json_load, json_upload
from utils.path import *
import json
import datetime
import os
import re


def replace_tmr(msg: str) -> str:
    """
    原始消息简单处理
    :param msg: 消息字符串
    :return: 去链接等
    """
    find_link = re.compile("(https?://.*[^\u4e00-\u9fa5])")
    links = re.findall(find_link, msg)
    for link in links:
        msg = msg.replace(link, '')
    return msg


def get_group_message_data(group_id,wxid,message) -> dict:
    """
    获取群消息数据
    :param group_id: 群id
    :return: dict
    """
    gid=str(group_id)
    uid=str(wxid)
    msg=str(message).replace(' ', '')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    message_path_group = group_message_data_path / f"{gid}"
    if not os.path.exists(message_path_group):
        os.makedirs(message_path_group)
    if not os.path.exists(message_path_group / f"{today}.json"):  # 日消息条数记录 {uid：消息数}
        json_upload(message_path_group / f"{today}.json", {uid: 1})    
    else:
        dic_ = json_load(message_path_group / f"{today}.json")
        if uid not in dic_:
            dic_[uid] = 1
        else:
            dic_[uid] += 1
        json_upload(message_path_group / f"{today}.json", dic_)
    if not os.path.exists(message_path_group / 'history.json'):  # 历史发言条数记录 {uid：消息数}
        json_upload(message_path_group / 'history.json', {uid: 1})
    else:
        dic_ = json_load(message_path_group / 'history.json')
        if uid not in dic_:
            dic_[uid] = 1
        else:
            dic_[uid] += 1
        json_upload(message_path_group / 'history.json', dic_)
    msg = replace_tmr(msg)
    with open(message_path_group / f"{today}.txt", 'a+', encoding='utf-8') as f:
        f.write(f"{msg}\n")


def get_cmd(id):
    """
    获取命令
    :return: dict
    """
    # print(id)
    try:
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        if not os.path.exists(config_path / 'cmd.json'):
            json_upload(config_path / 'cmd.json', {id: "/ai"})
            return "/ai"
        else:
            dic_ = json_load(config_path / 'cmd.json')
            if id not in dic_:
                dic_[id] = "/ai"
                json_upload(config_path / 'cmd.json', dic_)
                return "/ai"               
            else:
                return dic_[id]
            
            
    except Exception as e:
        print(e)
        return "/ai"
    
def set_blackList(id, status):
    """设置黑名单"""
    # gid=str(id)
    uid = str(id)
    try:
        if not os.path.exists(ailist_data_path):
            os.makedirs(ailist_data_path)
        if not os.path.exists(ailist_data_path / f"blackList.json"):
            json_upload(ailist_data_path / f"blackList.json", {uid: status})
            return 1
        else:
            dic_ = json_load(ailist_data_path / f"blackList.json")
            dic_[uid] = status
            json_upload(ailist_data_path / f"blackList.json", dic_)
            return 1

    except Exception as e:
        print(e)
        return 0
    


def speak_most_today(gid):
    today = datetime.date.today().strftime('%Y-%m-%d')
    dic_ = json_load(group_message_data_path / f"{gid}" / f"{today}.json")
    top = sorted(dic_.items(), key=lambda x: x[1], reverse=True)

    if len(top) == 0:
        return {'wxid': None, 'count': 0}
    else:
        return {'wxid': top[0][0], 'count': top[0][1]}
