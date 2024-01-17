#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import signal
from queue import Empty
from threading import Thread
from time import sleep
import uvicorn
from wcferry import Wcf
from lib.httpapi_core import Http
from configuration import Config


logging.basicConfig(
    level='DEBUG', format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
LOG = logging.getLogger("Demo")


def process_msg(wcf: Wcf):
    """处理接收到的消息"""
    while wcf.is_receiving_msg():
        try:
            msg = wcf.get_msg()
            # print(msg)
            LOG.info(f"msg:\n{msg}")  # 简单打印
        except Empty:
            continue  # Empty message
        except Exception as e:
            LOG.error(f"Receiving message error: {e}")


def run_http_server(app, host, port):
    uvicorn.run(app=app, host=host, port=port)


def main():
    LOG.info("Start demo...")
    config = Config()

    cb = config.BOT_CONFIG["callback"]
    http_port = config.BOT_CONFIG["http_port"]
    http_host = config.BOT_CONFIG["http_host"]
    print(http_port, http_host, cb)

    wcf = Wcf(debug=True)             # 默认连接本地服务

    sleep(5)  # 等微信加载好，以免信息显示异常
    LOG.info(f"已经登录: {True if wcf.is_login() else False}")
    LOG.info(f"wxid: {wcf.get_self_wxid()}")

    # cb = "http://192.168.1.10:3000/reciver"
    if not cb:
        print("没有设置接收消息回调，消息直接通过日志打印；请通过 --cb 设置消息回调")
        print(f"回调接口规范参考接收消息回调样例：http://0.0.0.0:9999/docs")
    http = Http(wcf=wcf,
                cb=cb,
                title="WeChatFerry HTTP 客户端",
                description=f"Github: <a href=",)
    # 允许接收消息
    # wcf.enable_receiving_msg(pyq=True)  # 同时允许接收朋友圈消息
    # Thread(target=process_msg, name="GetMessage", args=(wcf,), daemon=True).start()

    # 启动http服务
    Thread(target=run_http_server, name="HttpServer", args=(
        http,  http_host, http_port,), daemon=True).start()

    return wcf


if __name__ == "__main__":
    wcf = main()

    # 一直运行
    wcf.keep_running()
