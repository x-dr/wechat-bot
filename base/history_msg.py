msgHistoryMap = {}
modelMap = {}

def set_history_msg(id, msg):
    """处理AI消息"""
    msgHistoryMap[id] = msg

    

def get_history_msg(id):
    """处理AI消息"""
    # print("AI消息")
    if id not in msgHistoryMap:
        return []
    return msgHistoryMap[id]

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

# set_model("1", "chatgpt")

# print(get_model("1"))