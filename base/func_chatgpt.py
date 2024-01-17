import requests
import json


class ChatGPT:
    def __init__(self, conf: dict) -> None:

        self.base_url = conf["base_url"]
        self._api_key = conf["api_key"]  # 设置API密钥
        self.model = conf["model"]

    def __repr__(self):
        return 'ChatGPT'

    def get_answer(self, msg: str) -> str:
        url = f'{self.base_url}/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": "OpenAI-Chatbot",
        }
        data = {
            "model": self.model,
            "messages": msg
        }
        try:
            response = requests.post(
                url, headers=headers, data=json.dumps(data))
            return response.json()
        except Exception as e:
            print(f"其他错误：{e}")


