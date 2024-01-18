import time

msgHistoryMap = {}
modelMap = {}

max_list_size=20 # 最大上下文列表长度

def set_history_msg(id, msg):
    """处理AI消息"""
    now_timestamp = time.time()
    msgHistoryMap.setdefault(id, {})['timestamp'] = now_timestamp
    msgHistoryMap[id]['history'] = msg

    

def get_history_msg(id):
    """处理AI消息"""

    if id not in msgHistoryMap:
        return []
    else:
        id_list = msgHistoryMap[id]['history']
        if len(id_list) > max_list_size:
            id_list = id_list[-max_list_size:]  # 删除最早的元素
        return id_list

def set_model(id, model):
    """处理AI消息"""
    # print("AI消息")

    modelMap[id] = model

def get_model(id):
    """处理AI消息"""
    # print("AI消息")
    # print(modelMap)
    if id not in modelMap:
        return "spark"
    
    return modelMap[id]

def clear_history():
    """清除历史记录"""
    try:
        now_timestamp = time.time()

        for id, history_data in msgHistoryMap.items():
            # 获取历史记录的时间戳
            history_timestamp = history_data["timestamp"]

            # 判断历史记录是否超过30分钟
            if history_timestamp + 60 * 60 < now_timestamp:
                msgHistoryMap[id]["history"] = []
                msgHistoryMap[id]["timestamp"] = now_timestamp
            print(msgHistoryMap)
    except Exception as e:
        print(e)

