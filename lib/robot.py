# -*- coding: utf-8 -*-

import logging
import re
import time
import xml.etree.ElementTree as ET
from lxml import etree
import json
from queue import Empty
from threading import Thread
import random
from wcferry import Wcf, WxMsg

from configuration import Config
# from .get_plugin import get_plugin

from base.func_ai import ai_chat,switch_model
from .msg_analyze import get_group_message_data, get_cmd,set_blackList,speak_most_today
from base.history_msg import set_history_msg

class Robot():
    print("Robot")
    def __init__(self, wcf: Wcf) -> None:
        # print("Robot __init__")
        # print(self)
        """ 初始化
        :param wcf: Wcf 实例
        """

        self.config = Config()
        self.wcf = wcf

        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()
        self.LOG = logging.getLogger("Robot")






    def processMsg(self, msg: WxMsg) -> None:
        msgdata = {}
        # msgdata["id"] = msg.id
        # msgdata["ts"] = msg.ts
        # msgdata["sign"] = msg.sign
        msgdata["type"] = msg.type
        msgdata["xml"] = msg.xml
        msgdata["sender"] = msg.sender
        msgdata["roomid"] = msg.roomid
        msgdata["content"] = msg.content
        msgdata["thumb"] = msg.thumb
        msgdata["extra"] = msg.extra
        msgdata["is_at"] = msg.is_at(self.wcf.self_wxid)
        msgdata["is_self"] = msg.from_self()
        msgdata["is_group"] = msg.from_group()

        
        # print(msgdata)
        
        self.LOG.info(msgdata)

        """当接收到消息的时候，会调用本方法。如果不实现本方法，则打印原始消息。
        此处可进行自定义发送的内容,如通过 msg.content 关键字自动获取当前天气信息，并发送到对应的群组@发送者
        群号：msg.roomid  微信ID：msg.sender  消息内容：msg.content
        content = "xx天气信息为："
        receivers = msg.roomid
        self.sendTextMsg(content, receivers, msg.sender)
        """

        #记录消息
        

        if msg.content == "/help":
            message="""/ai 提问或交谈
/help 查看帮助信息
/sw:gemini 切换为 gemini-pro 模型
/sw:chatgpt 切换为 gpt-3.5-turbo 模型
/sw:spark 切换为 spark 模型
/sw 随机选择模型
/new 重置上下文内容
/ban @用户 将用户加入黑名单
/unban @用户 将用户移出黑名单
水王  查看今天说话最多的人"""

            sender = msg.roomid if msg.from_group() else msg.sender
            at_id = msg.sender if msg.from_group() else ""
            self.sendTextMsg(f"{message.strip()}", sender, at_id)

        
        if msg.content.startswith("/sw"):
            self.get_switch_model(msg)

        # 群聊消息
        elif msg.from_group():
            if msg.roomid in self.config.HISTORY_MSG['group']:
                get_group_message_data(msg.roomid, msg.sender, msg.content)
            aicmd = get_cmd(msg.sender)
            if self.config.GROUPS == []:  # 群聊消息，但是没有配置群聊
                if msg.content.startswith("/ai") or msg.content.startswith(aicmd):
                    self.get_ai_chat(msg)
                if msg.content=="/new":
                    set_history_msg(msg.sender,[])
                    self.sendTextMsg(f"已清空对话",msg.roomid, msg.sender)

                if msg.content=="水王":
                    self.get_speak_most_today(msg.roomid)


            if msg.roomid in self.config.GROUPS:
                aicmd = get_cmd(msg.sender)
                if msg.content.startswith("/ai") or msg.content.startswith(aicmd):
                    self.get_ai_chat(msg)
                elif msg.content=="/new":
                    set_history_msg(msg.sender,[])
                    self.sendTextMsg(f"已清空对话",msg.roomid, msg.sender)

                elif msg.content.startswith("/ban"):
                    if msg.sender in self.config.MANAGERS:
                        ban_wxid =json.loads(self.xml_to_json(msg.xml))["atuserlist"]
                        ban_wxid = ban_wxid.split(",")
                        for uid in ban_wxid:
                            stuts=set_blackList(uid,1)
                            if stuts == 1:
                                aliasname=self.wcf.get_alias_in_chatroom(uid, msg.roomid)
                                self.sendTextMsg(f"\n已将{aliasname}\n加入黑名单", msg.roomid)                       
                    else:
                        self.sendTextMsg(f"你没有权限", msg.roomid)
                elif msg.content.startswith("/unban"):
                    if msg.sender in self.config.MANAGERS:
                        ban_wxid =json.loads(self.xml_to_json(msg.xml))["atuserlist"]
                        ban_wxid = ban_wxid.split(",")
                        for uid in ban_wxid:
                            stuts=set_blackList(uid,0)
                            if stuts == 1:
                                aliasname=self.wcf.get_alias_in_chatroom(uid, msg.roomid)
                                self.sendTextMsg(f"\n已将{aliasname}\n移出黑名单", msg.roomid)                       
                    else:
                        self.sendTextMsg(f"你没有权限", msg.roomid)
                elif msg.content=="水王":
                    # print(msg.roomid)
                    self.get_speak_most_today(msg.roomid)
                else:
                    pass

            if msg.roomid not in self.config.GROUPS:  
                # print("不在配置的响应的群列表里，忽略")
                # pass
                return

            if msg.is_at(self.wxid):  # 被@
                print("被@")
                # self.toAt(msg)
                self.send_pat_msg(msg)

            else:  # 其他消息
                pass
            return  # 处理完群聊信息，后面就不需要处理了

        # 非群聊信息，按消息类型进行处理
        elif msg.type == 37:  # 好友请求
            self.autoAcceptFriendRequest(msg)

        elif msg.type == 10000:  # 系统信息
            self.sayHiToNewFriend(msg)

        elif msg.type == 0x01:  # 文本消息
            # 让配置加载更灵活，自己可以更新配置。也可以利用定时任务更新。
            # print("文本消息")
            # print(msg)
            if msg.sender in self.config.MANAGERS and msg.content == "/update":
                # if msg.content == "^更新$":
                self.config.reload()
                self.sendTextMsg("配置已更新", msg.sender)
                self.LOG.info("已更新")
            else:
                if msg.content.startswith("/ai"):
                    self.get_ai_chat(msg)
                elif msg.content=="/new":
                    set_history_msg(msg.sender,[])
                    self.sendTextMsg(f"已清空对话",msg.sender)
                else:
                    message="""/ai 提问或交谈
/help 查看帮助信息
/sw:gemini 切换为 gemini-pro 模型
/sw:chatgpt 切换为 gpt-3.5-turbo 模型
/sw:spark 切换为 spark 模型
/sw 随机选择模型
/new 重置上下文内容
/ban @用户 将用户加入黑名单
/unban @用户 将用户移出黑名单
水王  查看今天说话最多的人"""
                    self.sendTextMsg(f"你好，我是机器人;\n发送：\n{message.strip()}", msg.sender)

    def sendTextMsg(self, msg: str, receiver: str, at_list: str = ""):
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为：notify@all
        """

        # print("sendTextMsg")
        # # 消息中的特殊字符需要转义

        # msg 中需要有 @ 名单中一样数量的 @
        ats = ""
        if at_list:
            if at_list == "notify@all":  # @所有人
                ats = " @所有人"
            else:
                wxids = at_list.split(",")
                for wxid in wxids:
                    # 根据 wxid 查找群昵称
                    ats += f" @{self.wcf.get_alias_in_chatroom(wxid, receiver)}"

        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三
        if ats == "":
            # self.LOG.info(f"To {receiver}: {msg}")
            self.wcf.send_text(f"{msg}", receiver, at_list)
        else:
            # self.LOG.info(f"To {receiver}: {ats}\r{msg}")
            self.wcf.send_text(f"{ats}\n\n{msg}", receiver, at_list)

    def toAt(self, msg: WxMsg) -> bool:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        print("@@@")
        return self.toChitchat(msg)

    def get_ai_chat(self, msg: WxMsg) -> None:
        """
        获取AI回复
        """
        raw_msg = msg.content.replace("/ai", "")
        send_msg = ai_chat(raw_msg, msg.sender)
        # print(send_msg)
        sender = msg.roomid if msg.from_group() else msg.sender

        self.sendTextMsg(f"{send_msg}", sender)

    def sayHiToNewFriend(self, msg: WxMsg) -> None:
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        welcome = """/help 查看帮助信息
/ai 提问或交谈
/sw:gemini 切换为 gemini-pro 模型
/sw:chatgpt 切换为 gpt-3.5-turbo 模型
/sw:spark 切换为 spark 模型
/sw 随机选择模型
/new 重置上下文内容"""
        if nickName:
            # 添加了好友，更新好友列表
            self.allContacts[msg.sender] = nickName[0]
            self.sendTextMsg(
                f"Hi {nickName[0]}，我自动通过了你的好友请求。\n{welcome}", msg.sender)
    def getAllContacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def autoAcceptFriendRequest(self, msg: WxMsg) -> None:
            try:
                xml = ET.fromstring(msg.content)
                v3 = xml.attrib["encryptusername"]
                v4 = xml.attrib["ticket"]
                scene = int(xml.attrib["scene"])
                self.wcf.accept_new_friend(v3, v4, scene)   

            except Exception as e:
                self.LOG.error(f"同意好友出错：{e}")

    def send_pat_msg(self, msg: WxMsg) -> None:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        roomid = msg.roomid
        wxid = msg.sender
        self.wcf.send_pat_msg(roomid, wxid)
        # return self.toChitchat(msg)
    def xml_to_json(self,xml_string):
    # 用XML字符串创建Element对象
        root = ET.fromstring(xml_string)

        # 将Element对象转换为字典
        def element_to_dict(element):
            result = {}
            for child in element:
                result[child.tag] = element_to_dict(child) if len(child) > 0 else child.text
            return result

        xml_dict = element_to_dict(root)

        # 将字典转换为JSON字符串
        json_string = json.dumps(xml_dict, indent=2)
        return json_string
    
    def get_switch_model(self, msg: WxMsg) -> bool:
        """
        处理切换模型
        """
        model_list=["chatgpt","spark","gemini"]
        list=msg.content.split(":")
        print(len(list))
        if msg.from_group():
            if (msg.roomid in self.config.GROUPS or self.config.GROUPS==[]) and len(list) == 2 and list[1] in model_list:
                switch_model(list[1], msg.sender)
                self.sendTextMsg(f"已切换至:{list[1]}模型", msg.roomid,msg.sender)
            elif (msg.roomid in self.config.GROUPS or self.config.GROUPS==[]) and len(list) == 1:
                selected_model = random.choice(model_list)
                switch_model(selected_model, msg.sender)
                self.sendTextMsg(f"已切换至:{selected_model}模型", msg.roomid, msg.sender)
            else:
                self.sendTextMsg(f"你没有权限", msg.roomid,msg.sender)
        else:
            if len(list) == 2 and list[1] in model_list:
                switch_model(list[1], msg.sender)
                self.sendTextMsg(f"已切换至:{list[1]}模型", msg.sender)
            elif len(list) == 1:
                selected_model = random.choice(model_list)
                switch_model(selected_model, msg.sender)
                self.sendTextMsg(f"已切换至:{selected_model}模型", msg.sender)
            else:
                self.sendTextMsg(f"你没有权限", msg.sender)

    def get_speak_most_today(self, roomid) -> None:
        """
        获取当天说话最多的人
        """
        m_wxid=speak_most_today(roomid)
        if m_wxid['wxid']:
            aliasname=self.wcf.get_alias_in_chatroom(m_wxid['wxid'], roomid)
            self.sendTextMsg(f"今天说话最多的人是：{aliasname}，说了{m_wxid['count']}句", roomid)
        else:
            self.sendTextMsg(f"今天没有人说话", roomid)
