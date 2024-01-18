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
from job_mgmt import Job

from base.history_msg import  clear_history
from base.func_job import Job_



logging.basicConfig(
    level='DEBUG', format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
LOG = logging.getLogger("Demo")





def run_http_server(app, host, port):
    uvicorn.run(app=app, host=host, port=port)


def main():
    LOG.info("Start demo...")
    config = Config()
    
    job=Job()
    

    cb = config.BOT_CONFIG["callback"]
    http_port = config.BOT_CONFIG["http_port"]
    http_host = config.BOT_CONFIG["http_host"]
    print(http_port, http_host, cb)
    wcf = Wcf(debug=False) 

    runjob=Job_(wcf)

    sleep(5)  # 等微信加载好，以免信息显示异常
    LOG.info(f"已经登录: {True if wcf.is_login() else False}")
    LOG.info(f"wxid: {wcf.get_self_wxid()}")
    if not cb:
        print("没有设置接收消息回调，消息直接通过日志打印；请通过 --cb 设置消息回调")
        print(f"回调接口规范参考接收消息回调样例：http://{http_host}:{http_port}/docs")
    http = Http(wcf=wcf,
                cb=cb,
                title="WeChatFerry HTTP 客户端",
                description=f"Github: <a href='https://github.com/x-dr/wechat-bot'>",)

    # 启动http服务
    Thread(target=run_http_server, name="HttpServer", args=(
        http,  http_host, http_port,), daemon=True).start()
    
    
    job.onEveryMinutes(10, clear_history)
    job.onEveryTime("01:38", runjob.toJobBbing)
    job.runPendingJobs()



if __name__ == "__main__":
    main()

