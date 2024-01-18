from wcferry import Wcf, WxMsg
from configuration import Config

class Job_():
    print("Job_")
    def __init__(self, wcf: Wcf) -> None:
        """ 初始化
        :param wcf: Wcf 实例
        """
        self.config = Config()
        self.wcf = wcf

    def toJobBbing(self) -> bool:
        """
        发送定时消息
        """
        try:
            roomid_list = self.config.BING
            for roomid in roomid_list:
                self.wcf.send_text("必应每日超清壁纸",roomid)
                self.wcf.send_image("https://gh.tryxd.cn/https://raw.githubusercontent.com/x-dr/bing/main/images/latest.png",roomid)
        except Exception as e:
            self.LOG.error(f"发送定时消息出错：{e}")