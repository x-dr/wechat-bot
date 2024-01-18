import requests
import json

class Gemini:
    def __init__(self, conf: dict) -> None:

        self.base_url = conf["url"]
        self._api_key = conf["api_key"]  # 设置API密钥
        self.model = conf["model"]

    def __repr__(self):
        return 'Gemini'

    def get_answer(self, msg:str) -> str:
        url = f'{self.base_url}/v1beta/models/gemini-pro:generateContent?key={self._api_key}'
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            "contents": msg,
            "generationConfig": {
                "temperature": 0.9,
            }
        }
        # print(data)
        try:
            response = requests.post(url,headers=headers, data=json.dumps(data))
            # candidates[0].content.parts[0].text
            return response.json()
        except Exception as e:
            print(f"其他错误：{e}")


# if __name__ == "__main__":
#     from configuration import Config
#     config = Config().GEMINI
#     if not config:
#         exit(0)
#     gemini = Gemini(config)
#     gemini.get_answer("hello world")
# """
# {
#     "contents": [
#         {
#             "role": "user",
#             "parts": [
#                 {
#                     "text": "你是？"
#                 }
#             ]
#         }
#     ]
# }
# """
            

# """
# {
#   "candidates": [
#     {
#       "content": {
#         "parts": [
#           {
#             "text": "In the heart of the tranquil village of Belleau, nestled amidst rolling hills and verdant meadows, lived a young girl named Antoinette. Amidst the charm of the 1600s, Antoinette possessed a secret that would forever change her life – a magical backpack."
#           }
#         ],
#         "role": "model"
#       },
#       "finishReason": "STOP",
#       "index": 0,
#       "safetyRatings": [
#         {
#           "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#           "probability": "NEGLIGIBLE"
#         },
#         {
#           "category": "HARM_CATEGORY_HATE_SPEECH",
#           "probability": "NEGLIGIBLE"
#         },
#         {
#           "category": "HARM_CATEGORY_HARASSMENT",
#           "probability": "NEGLIGIBLE"
#         },
#         {
#           "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#           "probability": "NEGLIGIBLE"
#         }
#       ]
#     }
#   ],
#   "promptFeedback": {
#     "safetyRatings": [
#       {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "probability": "NEGLIGIBLE"
#       },
#       {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "probability": "NEGLIGIBLE"
#       },
#       {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "probability": "NEGLIGIBLE"
#       },
#       {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "probability": "NEGLIGIBLE"
#       }
#     ]
#   }
# }

# """