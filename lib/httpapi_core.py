#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import logging
from queue import Empty
from threading import Thread
from typing import Any

import requests
from fastapi import Body, FastAPI, Query
from pydantic import BaseModel
from wcferry import Wcf, WxMsg
from .robot import Robot

from configuration import Config

__version__ = "39.0.10.0"


class Msg(BaseModel):
    id: int
    ts: int
    sign: str
    type: int
    xml: str
    sender: str
    roomid: str
    content: str
    thumb: str
    extra: str
    is_at: bool
    is_self: bool
    is_group: bool


class Http(FastAPI):
    """WeChatFerry HTTP 客户端，文档地址：http://IP:PORT/docs"""

    def __init__(self, wcf: Wcf, cb: str, **extra: Any) -> None:
        super().__init__(**extra)
        self.config = Config()
        self.LOG = logging.getLogger(__name__)
        self.LOG.info(f"wcfhttp version: {__version__}")
        self.wcf = wcf 
        self._set_cb(cb)
        self.add_api_route("/msg_cb", self.msg_cb, methods=["POST"], summary="接收消息回调样例", tags=["示例"])

        self.add_api_route("/login", self.is_login, methods=["GET"], summary="获取登录状态")
        self.add_api_route("/wxid", self.get_self_wxid, methods=["GET"], summary="获取登录账号 wxid")
        self.add_api_route("/user-info", self.get_user_info, methods=["GET"], summary="获取登录账号个人信息")
        self.add_api_route("/msg-types", self.get_msg_types, methods=["GET"], summary="获取消息类型")
        self.add_api_route("/contacts", self.get_contacts, methods=["GET"], summary="获取完整通讯录")
        self.add_api_route("/friends", self.get_friends, methods=["GET"], summary="获取好友列表")
        self.add_api_route("/dbs", self.get_dbs, methods=["GET"], summary="获取所有数据库")
        self.add_api_route("/{db}/tables", self.get_tables, methods=["GET"], summary="获取 db 中所有表")
        self.add_api_route("/pyq", self.refresh_pyq, methods=["GET"], summary="刷新朋友圈（数据从消息回调中查看）")
        self.add_api_route("/chatroom-member", self.get_chatroom_members, methods=["GET"], summary="获取群成员")
        self.add_api_route("/alias-in-chatroom", self.get_alias_in_chatroom, methods=["GET"], summary="获取群成员名片")
        self.add_api_route("/ocr-result", self.get_ocr_result, methods=["GET"], summary="获取 OCR 结果")

        self.add_api_route("/text", self.send_text, methods=["POST"], summary="发送文本消息")
        self.add_api_route("/image", self.send_image, methods=["POST"], summary="发送图片消息")
        self.add_api_route("/file", self.send_file, methods=["POST"], summary="发送文件消息")
        self.add_api_route("/rich-text", self.send_rich_text, methods=["POST"], summary="发送卡片消息")
        self.add_api_route("/pat", self.send_pat_msg, methods=["POST"], summary="发送拍一拍消息")
        # self.add_api_route("/xml", self.send_xml, methods=["POST"], summary="发送 XML 消息")
        # self.add_api_route("/emotion", self.send_emotion, methods=["POST"], summary="发送表情消息")
        self.add_api_route("/sql", self.query_sql, methods=["POST"], summary="执行 SQL，如果数据量大注意分页，以免 OOM")
        self.add_api_route("/new-friend", self.accept_new_friend, methods=["POST"], summary="通过好友申请")
        self.add_api_route("/chatroom-member", self.add_chatroom_members, methods=["POST"], summary="添加群成员")
        self.add_api_route("/cr-members", self.invite_chatroom_members, methods=["POST"], summary="邀请群成员")
        self.add_api_route("/transfer", self.receive_transfer, methods=["POST"], summary="接收转账")
        self.add_api_route("/dec-image", self.decrypt_image, methods=["POST"], summary="（废弃）解密图片")
        self.add_api_route("/attachment", self.download_attachment, methods=["POST"], summary="（废弃）下载图片、文件和视频")
        self.add_api_route("/save-image", self.download_image, methods=["POST"], summary="下载图片")
        self.add_api_route("/save-audio", self.get_audio_msg, methods=["POST"], summary="保存语音")

        self.add_api_route("/chatroom-member", self.del_chatroom_members, methods=["DELETE"], summary="删除群成员")

    def _forward_msg(self, msg: WxMsg, cb: str):
        data = {}
        data["id"] = msg.id
        data["ts"] = msg.ts
        data["sign"] = msg.sign
        data["type"] = msg.type
        data["xml"] = msg.xml
        data["sender"] = msg.sender
        data["roomid"] = msg.roomid
        data["content"] = msg.content
        data["thumb"] = msg.thumb
        data["extra"] = msg.extra
        data["is_at"] = msg.is_at(self.wcf.self_wxid)
        data["is_self"] = msg.from_self()
        data["is_group"] = msg.from_group()

        try:
            rsp = requests.post(url=cb, json=data, timeout=30)
            if rsp.status_code != 200:
                self.LOG.error(f"消息转发失败，HTTP 状态码为: {rsp.status_code}")
        except Exception as e:
            self.LOG.error(f"消息转发异常: {e}")

    def _set_cb(self, cb: str):
        def process_msg(wcf: Wcf):
            """处理接收到的消息"""
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    robot.processMsg(msg)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}")    
        def callback(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    # self.LOG.info(msg)
                    robot.processMsg(msg)
                    self._forward_msg(msg, cb)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}")

        if cb:
            self.LOG.info(f"消息回调: {cb}")
            robot = Robot(self.wcf)
            robot.sendTextMsg(f"机器人启动成功,消息回调: {cb}", "filehelper")
            self.wcf.enable_receiving_msg(pyq=True)  # 同时允许接收朋友圈消息
            Thread(target=callback, name="GetMessage", args=(self.wcf,), daemon=True).start()
        else:
            self.LOG.info(f"没有设置回调，打印消息")
            robot = Robot(self.wcf)
            robot.sendTextMsg("机器人启动成功,没有设置回调，打印消息", "filehelper")
            # self.wcf.enable_recv_msg(print)
            self.wcf.enable_receiving_msg(pyq=True)  # 同时允许接收朋友圈消息
            Thread(target=process_msg, name="GetMessage", args=(self.wcf,), daemon=True).start()



    def is_login(self) -> dict:
        """获取登录状态"""
        ret = self.wcf.is_login()
        return {"status": 0, "message": "成功", "data": {"login": ret}}

    def get_self_wxid(self) -> dict:
        """获取登录账号 wxid"""
        ret = self.wcf.get_self_wxid()
        if ret:
            return {"status": 0, "message": "成功", "data": {"wxid": ret}}
        return {"status": -1, "message": "失败"}

    def get_msg_types(self) -> dict:
        """获取消息类型"""
        ret = self.wcf.get_msg_types()
        if ret:
            return {"status": 0, "message": "成功", "data": {"types": ret}}
        return {"status": -1, "message": "失败"}

    def get_contacts(self) -> dict:
        """获取完整通讯录"""
        ret = self.wcf.get_contacts()
        if ret:
            return {"status": 0, "message": "成功", "data": {"contacts": ret}}
        return {"status": -1, "message": "失败"}

    def get_friends(self) -> dict:
        """获取好友列表"""
        ret = self.wcf.get_friends()
        if ret:
            return {"status": 0, "message": "成功", "data": {"friends": ret}}
        return {"status": -1, "message": "失败"}

    def get_dbs(self) -> dict:
        """获取所有数据库"""
        ret = self.wcf.get_dbs()
        if ret:
            return {"status": 0, "message": "成功", "data": {"dbs": ret}}
        return {"status": -1, "message": "失败"}

    def get_tables(self, db: str) -> dict:
        """获取 db 中所有表

        Args:
            db (str): 数据库名（可通过 `get_dbs` 查询）

        Returns:
            List[dict]: `db` 下的所有表名及对应建表语句
        """
        ret = self.wcf.get_tables(db)
        if ret:
            return {"status": 0, "message": "成功", "data": {"tables": ret}}
        return {"status": -1, "message": "失败"}

    def get_user_info(self) -> dict:
        """获取登录账号个人信息"""
        ret = self.wcf.get_user_info()
        if ret:
            return {"status": 0, "message": "成功", "data": {"ui": ret}}
        return {"status": -1, "message": "失败"}

    def get_ocr_result(self, extra: str = Body("C:/...", description="消息中的 extra"),
                       timeout: int = Body("30", description="超时时间（秒）")) -> dict:
        """获取 OCR 结果。鸡肋，需要图片能自动下载；通过下载接口下载的图片无法识别。

        Args:
            extra (str): 待识别的图片路径，消息里的 extra

        Returns:
            str: OCR 结果
        """
        ret = self.wcf.get_ocr_result(extra, timeout)
        if ret:
            return {"status": 0, "message": "成功", "data": {"ocr": ret}}
        return {"status": -1, "message": "可能失败，可以看看日志。这接口没啥用，别用了。"}

    def msg_cb(self, msg: Msg = Body(description="微信消息")):
        """示例回调方法，简单打印消息"""
        print(f"收到消息：{msg}")
        return {"status": 0, "message": "成功"}

    def send_text(
            self, msg: str = Body(description="要发送的消息，换行用\\n表示"),
            receiver: str = Body("filehelper", description="消息接收者，roomid 或者 wxid"),
            aters: str = Body("", description="要 @ 的 wxid，多个用逗号分隔；@所有人 用 notify@all")) -> dict:
        """发送文本消息，可参考：https://github.com/lich0821/WeChatRobot/blob/master/robot.py 里 sendTextMsg

        Args:
            msg (str): 要发送的消息，换行使用 `\\n`；如果 @ 人的话，需要带上跟 `aters` 里数量相同的 @
            receiver (str): 消息接收人，wxid 或者 roomid
            aters (str): 要 @ 的 wxid，多个用逗号分隔；`@所有人` 只需要 `notify@all`

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_text(msg, receiver, aters)
        return {"status": ret, "message": "成功"if ret == 0 else "失败"}

    def send_image(self,
                   path: str = Body("C:\\Projs\\WeChatRobot\\TEQuant.jpeg", description="图片路径"),
                   receiver: str = Body("filehelper", description="消息接收者，roomid 或者 wxid")) -> dict:
        """发送图片，非线程安全

        Args:
            path (str): 图片路径，如：`C:/Projs/WeChatRobot/TEQuant.jpeg` 或 `https://raw.githubusercontent.com/lich0821/WeChatRobot/master/TEQuant.jpeg`
            receiver (str): 消息接收人，wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_image(path, receiver)
        return {"status": ret, "message": "成功"if ret == 0 else "失败"}

    def send_file(self,
                  path: str = Body("C:\\Projs\\WeChatRobot\\TEQuant.jpeg", description="本地文件路径，不支持网络路径"),
                  receiver: str = Body("filehelper", description="roomid 或者 wxid")) -> dict:
        """发送文件

        Args:
            path (str): 本地文件路径，如：`C:/Projs/WeChatRobot/README.MD`
            receiver (str): 消息接收人，wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_file(path, receiver)
        return {"status": ret, "message": "成功"if ret == 0 else "失败"}

    def send_rich_text(
            self, name: str = Body("碲矿", description="左下显示的名字"),
            account: str = Body("gh_75dea2d6c71f", description="填公众号 id 可以显示对应的头像"),
            title: str = Body("【FAQ】WeChatFerry 机器人常见问题 v39.0.10", description="标题，最多两行"),
            digest: str = Body("先看再问，少走弯路。", description="最多三行，会占位"),
            url:
            str = Body(
                "http://mp.weixin.qq.com/s?__biz=MzI0MjI1OTk0OQ==&amp;mid=2247487601&amp;idx=1&amp;sn=1bf7a0d1c659f8bc78a00cba18d7b204&amp;chksm=e97e52f3de09dbe591fe23f335ce73bc468bd107a8c7bc5a458752a47f9d2d55a5fcdc5dd386&amp;mpshare=1&amp;scene=1&amp;srcid=1209eP4EsXnynxyRQHzCK2bY&amp;sharer_shareinfo=a12096ee76b4e3a9e72c9aedaf51a5ef&amp;sharer_shareinfo_first=a12096ee76b4e3a9e72c9aedaf51a5ef#rd",
                description="点击后跳转的链接"),
            thumburl: str = Body("https://mmbiz.qpic.cn/mmbiz_jpg/XaSOeHibHicMGIiaZsBeYYjcuS2KfBGXfm8ibb9QrKJqk0H0W3JHia9icVica9nlWMiaD0xWmA0pKHpMOWbeBCJaAQc2IQ/0?wx_fmt=jpeg", description="缩略图的链接"),
            receiver: str = Body("filehelper", description="接收人, wxid 或者 roomid")) -> dict:
        """发送卡片消息
        卡片样式（格式乱了，看这里：https://github.com/lich0821/WeChatFerry/blob/master/clients/python/wcferry/client.py#L421）：
            |-------------------------------------|
            |title, 最长两行
            |(长标题, 标题短的话这行没有)
            |digest, 最多三行，会占位    |--------|
            |digest, 最多三行，会占位    |thumburl|
            |digest, 最多三行，会占位    |--------|
            |(account logo) name
            |-------------------------------------|
        Args:
            name (str): 左下显示的名字
            account (str): 填公众号 id 可以显示对应的头像（gh_ 开头的）
            title (str): 标题，最多两行
            digest (str): 摘要，三行
            url (str): 点击后跳转的链接
            thumburl (str): 缩略图的链接
            receiver (str): 接收人, wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_rich_text(name, account, title, digest, url, thumburl, receiver)
        return {"status": ret, "message": "成功"if ret == 0 else "失败，原因见日志"}

    def send_pat_msg(
            self, roomid: str = Body(description="要发送的消息，换行用\\n表示"),
            wxid: str = Body("filehelper", description="消息接收者，roomid 或者 wxid")) -> dict:
        """拍一拍群友

        Args:
            roomid (str): 群友所在群 roomid
            wxid (str): 要拍的群友的 wxid

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.send_pat_msg(roomid, wxid)
        return {"status": ret, "message": "成功"if ret == 1 else "失败，原因见日志"}

    def send_xml(
            self, receiver: str = Body("filehelper", description="roomid 或者 wxid"),
            xml:
            str = Body(
                '<?xml version="1.0"?><msg><appmsg appid="" sdkver="0"><title>叮当药房，24小时服务，28分钟送药到家！</title><des>叮当快药首家承诺范围内28分钟送药到家！叮当快药核心区域内7*24小时全天候服务，送药上门！叮当快药官网为您提供快捷便利，正品低价，安全放心的购药、送药服务体验。</des><action>view</action><type>33</type></appmsg><fromusername>wxid_xxxxxxxxxxxxxx</fromusername><scene>0</scene><appinfo><version>1</version><appname /></appinfo><commenturl /></msg>',
                description="xml 内容"),
            type: int = Body(0x21, description="xml 类型，0x21 为小程序"),
            path: str = Body(None, description="封面图片路径")) -> dict:
        """发送 XML

        Args:
            receiver (str): 消息接收人，wxid 或者 roomid
            xml (str): xml 内容
            type (int): xml 类型，如：0x21 为小程序
            path (str): 封面图片路径

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_xml(receiver, xml, type, path)
        return {"status": ret, "message": "成功"if ret == 0 else "失败"}

    def send_emotion(self,
                     path: str = Body("C:/Projs/WeChatRobot/emo.gif", description="本地文件路径，不支持网络路径"),
                     receiver: str = Body("filehelper", description="roomid 或者 wxid")) -> dict:
        """发送表情

        Args:
            path (str): 本地表情路径，如：`C:/Projs/WeChatRobot/emo.gif`
            receiver (str): 消息接收人，wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_emotion(path, receiver)
        return {"status": ret, "message": "成功"if ret == 0 else "失败"}

    def query_sql(self,
                  db: str = Body("MicroMsg.db", description="数据库"),
                  sql: str = Body("SELECT * FROM Contact LIMIT 1;", description="SQL 语句")) -> dict:
        """执行 SQL，如果数据量大注意分页，以免 OOM

        Args:
            db (str): 要查询的数据库
            sql (str): 要执行的 SQL

        Returns:
            List[dict]: 查询结果
        """
        ret = self.wcf.query_sql(db, sql)
        if ret:
            for row in ret:
                for k, v in row.items():
                    print(k, type(v))
                    if type(v) is bytes:
                        row[k] = base64.b64encode(v)
            return {"status": 0, "message": "成功", "data": {"bs64": ret}}
        return {"status": -1, "message": "失败"}

    def accept_new_friend(self,
                          v3: str = Body("v3", description="加密用户名 (好友申请消息里 v3 开头的字符串)"),
                          v4: str = Body("v4", description="Ticket (好友申请消息里 v4 开头的字符串)"),
                          scene: int = Body(30, description="申请方式 (好友申请消息里的 scene)")) -> dict:
        """通过好友申请

        Args:
            v3 (str): 加密用户名 (好友申请消息里 v3 开头的字符串)
            v4 (str): Ticket (好友申请消息里 v4 开头的字符串)
            scene: 申请方式 (好友申请消息里的 scene)

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.accept_new_friend(v3, v4, scene)
        return {"status": ret, "message": "成功"if ret == 1 else "失败"}

    def add_chatroom_members(self,
                             roomid: str = Body("xxxxxxxx@chatroom", description="待加群的 id"),
                             wxids: str = Body("wxid_xxxxxxxxxxxxx", description="要加到群里的 wxid，多个用逗号分隔")) -> dict:
        """添加群成员

        Args:
            roomid (str): 待加群的 id
            wxids (str): 要加到群里的 wxid，多个用逗号分隔

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.add_chatroom_members(roomid, wxids)
        return {"status": ret, "message": "成功"if ret == 1 else "失败"}

    def invite_chatroom_members(self,
                                roomid: str = Body("xxxxxxxx@chatroom", description="待加群的 id"),
                                wxids: str = Body("wxid_xxxxxxxxxxxxx", description="要加到群里的 wxid，多个用逗号分隔")) -> dict:
        """邀请群成员

        Args:
            roomid (str): 待加群的 id
            wxids (str): 要加到群里的 wxid，多个用逗号分隔

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.invite_chatroom_members(roomid, wxids)
        return {"status": ret, "message": "成功"if ret == 1 else "失败"}

    def del_chatroom_members(self,
                             roomid: str = Body("xxxxxxxx@chatroom", description="群的 id"),
                             wxids: str = Body("wxid_xxxxxxxxxxxxx", description="要删除的 wxid，多个用逗号分隔")) -> dict:
        """删除群成员

        Args:
            roomid (str): 群的 id
            wxids (str): 要删除的 wxid，多个用逗号分隔

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.del_chatroom_members(roomid, wxids)
        return {"status": ret, "message": "成功"if ret == 1 else "失败"}

    def receive_transfer(self,
                         wxid: str = Body("wxid_xxxxxxxxxxxxx", description="转账消息里的发送人 wxid"),
                         transferid: str = Body("transferid", description="转账消息里的 transferid"),
                         transactionid: str = Body("transactionid", description="转账消息里的 transactionid")) -> dict:
        """接收转账

        Args:
            wxid (str): 转账消息里的发送人 wxid
            transferid (str): 转账消息里的 transferid
            transactionid (str): 转账消息里的 transactionid

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.receive_transfer(wxid, transferid, transactionid)
        return {"status": ret, "message": "成功"if ret == 1 else "失败"}

    def refresh_pyq(self, id: int = Query(0, description="开始 id，0 为最新页")) -> dict:
        """刷新朋友圈

        Args:
            id (int): 开始 id，0 为最新页

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.refresh_pyq(id)
        return {"status": ret, "message": "成功"if ret == 1 else "失败"}

    def decrypt_image(self,
                      src: str = Body("C:\\...", description="加密的图片路径，从图片消息中获取"),
                      dst: str = Body("C:\\...", description="解密的图片路径")) -> dict:
        """解密图片:

        Args:
            src (str): 加密的图片路径
            dst (str): 解密的图片路径

        Returns:
            bool: 是否成功
        """
        ret = self.wcf.decrypt_image(src, dst)
        return {"status": ret, "message": "成功"if ret else "废弃，请使用 save-image"}

    def download_attachment(self,
                            id: int = Body("0", description="消息中的id"),
                            thumb: str = Body("C:/...", description="消息中的 thumb"),
                            extra: str = Body("C:/...", description="消息中的 extra")) -> dict:
        """下载附件（图片、视频、文件）

        Args:
            id (int): 消息中 id
            thumb (str): 消息中的 thumb
            extra (str): 消息中的 extra

        Returns:
            str: 成功返回存储路径；空字符串为失败，原因见日志。
        """
        ret = self.wcf.download_attach(id, thumb, extra)
        if ret:
            return {"status": 0, "message": "成功", "data": {"path": ret}}

        return {"status": -1, "message": "废弃，请使用 save-image"}

    def download_image(self,
                       id: int = Body("0", description="消息中的id"),
                       extra: str = Body("C:/...", description="消息中的 extra"),
                       dir: str = Body("C:/...", description="保存图片的目录"),
                       timeout: int = Body("30", description="超时时间（秒）")) -> dict:
        """下载图片

        Args:
            id (int): 消息中 id
            extra (str): 消息中的 extra
            dir (str): 存放图片的目录
            timeout (int): 超时时间（秒）

        Returns:
            str: 成功返回存储路径；空字符串为失败，原因见日志。
        """
        ret = self.wcf.download_image(id, extra, dir, timeout)
        if ret:
            return {"status": 0, "message": "成功", "data": {"path": ret}}

        return {"status": -1, "message": "失败，原因见日志"}

    def get_audio_msg(self,
                      id: int = Body("0", description="消息中的id"),
                      dir: str = Body("C:/...", description="保存语音的目录"),
                      timeout: int = Body("30", description="超时时间（秒）")) -> dict:
        """保存语音

        Args:
            id (int): 消息中 id
            dir (str): 存放图片的目录
            timeout (int): 超时时间（秒）

        Returns:
            str: 成功返回存储路径；空字符串为失败，原因见日志。
        """
        ret = self.wcf.get_audio_msg(id, dir, timeout)
        if ret:
            return {"status": 0, "message": "成功", "data": {"path": ret}}

        return {"status": -1, "message": "失败，原因见日志"}

    def get_chatroom_members(self, roomid: str = Query("xxxxxxxx@chatroom", description="群的 id")) -> dict:
        """获取群成员

        Args:
            roomid (str): 群的 id

        Returns:
            List[dict]: 群成员列表
        """
        ret = self.wcf.get_chatroom_members(roomid)
        return {"status": 0, "message": "成功", "data": {"members": ret}}

    def get_alias_in_chatroom(self, wxid: str = Query("wxid_xxxxxxxxxxxxx", description="wxid"),
                              roomid: str = Query("xxxxxxxx@chatroom", description="群的 id")) -> dict:
        """获取群成员名片

        Args:
            roomid (str): 群的 id
            wxid (str): wxid

        Returns:
            str: 名片
        """
        ret = self.wcf.get_alias_in_chatroom(wxid, roomid)
        return {"status": 0, "message": "成功", "data": {"alias": ret}}