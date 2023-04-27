import { ChatGPTAPI } from 'chatgpt';
import schedule from "node-schedule"
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()

let apiKey = '';
const api = new ChatGPTAPI({
    apiKey: apiKey || process.env.OPENAI_API_KEY,
    apiBaseUrl: process.env.PROXY_API || 'https://api.openai.com/v1'
});

const conversationPool = new Map();
async function chatgptReply(wxid, id,nick, rawmsg) {
    let chat = id
    console.log(`chat:${wxid}-------${id}\nrawmsg: ${rawmsg}`);
    // console.log(rawmsg, id);
    let response = '🤒🤒🤒出了一点小问题，请稍后重试下...';
    if (rawmsg === "清除所有对话" && id === "wxid_xxxxxxxxxxxxxxx") {
        conversationPool.clear()
        response = `所有的对话已清空`
        return response
    } else if (rawmsg === "结束对话") {
        conversationPool.delete(id);
        response = `${nick}的对话已结束`
        return response
    } else {
        try {
            let opts = {};
            // conversation
            let conversation = conversationPool.get(id);
            if (conversation) {
                opts = conversation;
            }
            opts.timeoutMs = 2 * 60 * 1000;
            let res = await api.sendMessage(rawmsg, opts);
            response = res.text;
            console.log(`chat:${wxid}------${id}\nresponse: ${response}`);
            const datatime= Date.now()
            conversation = {
                // conversationId: res.conversationId,
                datatime: datatime,
                parentMessageId: res.id
            };
            conversationPool.set(id, conversation);
            console.log(conversationPool);
        } catch (e) {
            console.log(e);
            if (e.message === 'ChatGPTAPI error 429') {
                response = '🤯🤯🤯请稍等一下哦，我还在思考你的上一个问题';
            }
            console.error(e);
        }
        response = `${rawmsg} \n ------------------------ \n` + response;

        return response
    }


}


const clearMap = async () => {
    const now = Date.now();
    const promises = Array.from(conversationPool.entries())
      .filter(([key, value]) => now - value.datatime >= 1000 * 600)
      .map(([key, value]) =>
        new Promise((resolve, reject) => {
          conversationPool.delete(key);
          resolve();
        })
      );
  
    try {
      await Promise.all(promises);
      console.log('Keys deleted successfully');
    //   console.log(conversationPool);
    } catch (err) {
      console.error(err);
    }
  };

// 每隔30分钟执行一次clearMap()方法
schedule.scheduleJob('*/30 * * * *', clearMap);


export default chatgptReply