#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import os
import shutil
import sys

import yaml


class Config(object):
    def __init__(self) -> None:
        self.reload()

    def _load_config(self) -> dict:
        # pwd = os.path.dirname(sys.executable)
    
    # 拼接相对路径
        # pwd = os.path.join(exe_dir, 'config.yaml')
        pwd = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(f"{pwd}/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)
        except FileNotFoundError:
            shutil.copyfile(f"{pwd}/config.yaml.template", f"{pwd}/config.yaml")
            with open(f"{pwd}/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)

        return yconfig

    def reload(self) -> None:
        # print("reload")
        yconfig = self._load_config()
        logging.config.dictConfig(yconfig["logging"])
        
        self.MANAGERS=yconfig["bot"]["managers"]
        self.GROUPS = yconfig["bot"]["groups"]["enable"]
        self.NEWS = yconfig["bot"]["news"]["receivers"]
        self.BING = yconfig["bot"]["bing"]["receivers"]
        self.REPORT_REMINDERS = yconfig["bot"]["report_reminder"]["receivers"]
        
        self.BOT_CONFIG = yconfig["bot"]["config"]
        self.HISTORY_MSG = yconfig.get("history_msg", {})
        self.CHATGPT = yconfig.get("chatgpt", {})
        self.SPARK = yconfig.get("sparkapi", {})
        self.GEMINI = yconfig.get("gemini", {})
