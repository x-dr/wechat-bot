import schedule from "node-schedule"
import {
  requestPromise
} from './req.js'
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()

const API = process.env.PROXY_API ? process.env.PROXY_API : 'https://api.openai.com';
const OPENAI_MODEL = process.env.OPENAI_API_MODEL ? process.env.OPENAI_API_MODEL : 'gpt-3.5-turbo-16k';

const systemMessage = {
  role: 'system',
  content: '你是 ChatGPT，OpenAI 训练的大型语言模型。仔细按照用户的说明进行回复。',
}

const conversationPool = new Map();

async function chatgptReply(wxid, id, nick, rawmsg) {
  console.log(`chat:${wxid}-------${id}\nrawmsg: ${rawmsg}`);
  let response = '🤒🤒🤒出了一点小问题，请稍后重试下...';
  if (rawmsg === "结束对话") {
    conversationPool.delete(id);
    response = `${nick}的对话已结束`
    return response
  } else {

    const datatime = Date.now()
    const messages = conversationPool.get(id) ? [...conversationPool.get(id).messages, {
      role: 'user',
      content: rawmsg
    }] : [systemMessage, {
      role: 'user',
      content: rawmsg
    }];
    const newMessage = {
      datatime: datatime,
      messages
    };
    const data = {
      model: OPENAI_MODEL,
      messages
    };
    let raw_response

    try {
      raw_response = await requestPromise({
        url: `${API}/v1/chat/completions`,
        headers: {
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
          'Content-Type': 'application/json',
          'User-Agent': 'bot'
        },
        body: data,
        method: 'POST',

      })

      // 检查返回的数据是否包含 choices 字段
      console.log(raw_response);
      if (raw_response.data.choices && raw_response.data.choices.length > 0) {
        const response = raw_response.data.choices[0].message;
        console.log(`chat:${wxid}------${id}\nresponse: ${response.content}`);
        // 只有在成功获取到回复时，才将原始消息添加到对话池中
        if (response) {
          conversationPool.set(id, newMessage);
        }
        conversationPool.get(id).messages.push(response);
        return `${rawmsg} \n ------------------------ \n${response.content}`;
      } else {
        console.log('Invalid response:', raw_response);
        response = '🤒🤒🤒出了一点小问题，请稍后重试下...';
      }

    } catch (e) {
      console.log(e);
      if (raw_response.response.data) {
        console.log(raw_response.response.data.error);
      } else {
        console.log(raw_response.response);
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