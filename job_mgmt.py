# -*- coding: utf-8 -*-

import time
from typing import Any, Callable

import schedule


class Job(object):
    def __init__(self) -> None:
        pass

    def onEverySeconds(self, seconds: int, task: Callable[..., Any], *args, **kwargs) -> None:
        """
        每 seconds 秒执行
        :param seconds: 间隔，秒
        :param task: 定时执行的方法
        :return: None
        """
        schedule.every(seconds).seconds.do(task, *args, **kwargs)

    def onEveryMinutes(self, minutes: int, task: Callable[..., Any], *args, **kwargs) -> None:
        """
        每 minutes 分钟执行
        :param minutes: 间隔，分钟
        :param task: 定时执行的方法
        :return: None
        """
        schedule.every(minutes).minutes.do(task, *args, **kwargs)

    def onEveryHours(self, hours: int, task: Callable[..., Any], *args, **kwargs) -> None:
        """
        每 hours 小时执行
        :param hours: 间隔，小时
        :param task: 定时执行的方法
        :return: None
        """
        schedule.every(hours).hours.do(task, *args, **kwargs)

    def onEveryDays(self, days: int, task: Callable[..., Any], *args, **kwargs) -> None:
        """
        每 days 天执行
        :param days: 间隔，天
        :param task: 定时执行的方法
        :return: None
        """
        schedule.every(days).days.do(task, *args, **kwargs)

    def onEveryTime(self, times: int, task: Callable[..., Any], *args, **kwargs) -> None:
        """
        每天定时执行
        :param times: 时间字符串列表，格式:
            - For daily jobs -> HH:MM:SS or HH:MM
            - For hourly jobs -> MM:SS or :MM
            - For minute jobs -> :SS
        :param task: 定时执行的方法
        :return: None

        例子: times=["10:30", "10:45", "11:00"]
        """
        if not isinstance(times, list):
            times = [times]

        for t in times:
            schedule.every(1).days.at(t).do(task, *args, **kwargs)

    def runPendingJobs(self) -> None:
        while True:
            # print("runPendingJobs")
            schedule.run_pending()
            time.sleep(1)


