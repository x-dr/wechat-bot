from .history_msg import set_history_msg, get_history_msg
from .func_chatgpt import ChatGPT
from .func_spark import SparkApi
from .func_gemini import Gemini
from utils.utils import json_load, json_upload
from utils.path import *
import json
import datetime
import os
from configuration import Config


def ai_chat(message, id):
    config = Config()
    """处理AI消息"""
    try:
        if get_blackList(id) == 1:
            return "你已被加入黑名单，无法使用AI功能！"
        else:
            if get_model(id) == "chatgpt":
                gpt_config = config.CHATGPT
                chat_gpt = ChatGPT(gpt_config)
                msgMap = get_history_msg(id)
                msgMap.append({"role": "user", "content": f"{message}"})
                msg_json = chat_gpt.get_answer(msgMap)
                if 'choices' in msg_json and msg_json['choices'] and 'message' in msg_json['choices'][0]:
                    msg = msg_json['choices'][0]['message']['content']
                    set_history_msg(id, msgMap)
                    bot_msg = msg_json['choices'][0]['message']
                    get_history_msg(id).append(bot_msg)
                    return msg
                else:
                    return "error"

            if get_model(id) == "spark":
                spark_config = Config().SPARK
                spark_api = SparkApi(spark_config)
                msgMap = get_history_msg(id)
                msgMap.append({"role": "user", "content": f"{message}"})
                msg_json = spark_api.get_answer(msgMap)
                if msg_json['code'] == 1:
                    msg = msg_json['data']
                    set_history_msg(id, msgMap)
                    bot_msg = {"role": "assistant", "content": f"{msg}"}
                    get_history_msg(id).append(bot_msg)
                    return msg
                else:
                    msg = "error"
                    return msg

            if get_model(id) == "gemini":
                gemini_config = Config().GEMINI
                gemini_api = Gemini(gemini_config)
                msgMap = get_history_msg(id)
                msgMap.append(
                    {"role": "user", "parts": [{"text": f"{message}"}]})
                msg_json = gemini_api.get_answer(msgMap)
                if 'candidates' in msg_json and msg_json['candidates'] and 'content' in msg_json['candidates'][0]:
                    msg = msg_json['candidates'][0]['content']['parts'][0]['text']
                    set_history_msg(id, msgMap)
                    bot_msg = msg_json['candidates'][0]['content']['parts'][0]
                    get_history_msg(id).append(bot_msg)
                    return msg
                else:
                    msg = "error"
                    return msg
            else:
                pass

    except Exception as e:
        print(e)
        return "error"


def get_model(id):
    """获取模型"""
    try:
        if not os.path.exists(model_data_path):
            os.makedirs(model_data_path)
        if not os.path.exists(model_data_path / f"{id}_model.json"):
            json_upload(model_data_path /
                        f"{id}_model.json", {"model": "chatgpt"})
            return "chatgpt"
        else:
            dic_ = json_load(model_data_path / f"{id}_model.json")
            if "model" in dic_:
                return dic_["model"]
            else:
                return "chatgpt"
    except Exception as e:
        print(e)
        return "chatgpt"


def get_blackList(id):
    """获取黑名单"""
    # gid=str(id)
    uid = str(id)
    try:
        if not os.path.exists(ailist_data_path):
            os.makedirs(ailist_data_path)
        if not os.path.exists(ailist_data_path / f"blackList.json"):
            json_upload(ailist_data_path / f"blackList.json", {uid: 0})
            return 0
        else:
            dic_ = json_load(ailist_data_path / f"blackList.json")
            if uid not in dic_:
                dic_[uid] = 0
            else:
                return dic_[uid]

    except Exception as e:
        print(e)
        return 1





def switch_model(model: str = None, id=None) -> None:
    """切换模型"""
    if get_blackList(id) == 1:
        return "你已被加入黑名单，无法使用AI功能！"
    else:
        try:
            if model == "gemini":
                set_history_msg(id, [])
            if not os.path.exists(model_data_path):
                os.makedirs(model_data_path)
            if not os.path.exists(model_data_path / f"{id}_model.json"):
                json_upload(model_data_path /
                            f"{id}_model.json", {"model": model})
            else:
                dic_ = json_load(model_data_path / f"{id}_model.json")
                if "model" in dic_:
                    dic_["model"] = model
                    json_upload(model_data_path / f"{id}_model.json", dic_)
                else:
                    json_upload(model_data_path /
                                f"{id}_model.json", {"model": model})
        except Exception as e:
            print(e)


