import _thread as thread
import base64
# import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
# from configuration import Config

import websocket  # 使用websocket_client
answer = ""

class SparkApi:
    # 初始化
    def __init__(self, conf: dict) -> None:
        self.APPID = conf["appid"]
        self.APIKey = conf["api_key"]
        self.APISecret = conf["api_secret"]
        parsed_url = urlparse(conf["Spark_url"])
        self.host = parsed_url.netloc
        self.path = parsed_url.path
        self.Spark_url = conf["Spark_url"]
        self.domain = conf["domain"]

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


    # 收到websocket错误的处理
    def on_error(self,ws, error):
        # print("### error:", error)
        ws.has_error = True
    

    # 收到websocket关闭的处理
    def on_close(self,ws, one, two):
        ws.close()
        # print(" ")


    # 收到websocket连接建立的处理
    def on_open(self,ws):
        thread.start_new_thread(self.run, (ws,))


    def run(self,ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
        ws.send(data)


    # 收到websocket消息的处理
    def on_message(self,ws, message):
        # print(message)
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            # print(content,end ="")
            global answer
            answer += content
            # print(1)
            if status == 2:
                ws.close()


    def gen_params(self,appid, domain,question):
        """
        通过appid和用户的提问来生成请参数
        """
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }
        return data


    def get_answer(self,question):
        websocket.enableTrace(False)
        # enableTrace(False)
        wsUrl = self.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_open=self.on_open)
        ws.appid = self.APPID
        ws.question = question
        ws.domain = self.domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        msg=answer
        answer=""
        if hasattr(ws, 'has_error') and ws.has_error:
            # print(ws.has_error)
            # print("spark connection failed.")
            return {"code": 0,
                    "error": "spark connection failed."}
        return {
            "code": 1,
            "data": msg
        }


# if __name__ == "__main__":
#     from configuration import Config
#     config = Config().SPARKAPI
#     if not config:
#         exit(0)
#     gemini = SparkApi(config)
#     data=[{"role": "user","content": "hello world"}]
#     print(gemini.get_answer(data))





