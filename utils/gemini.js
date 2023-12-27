import schedule from "node-schedule"
import {
    requestPromise
} from './req.js'
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()


const geminiPool = new Map();

async function geminReply(wxid, id, nick, rawmsg) {
    console.log(`chat:${wxid}-------${id}\nrawmsg: ${rawmsg}`);
    let response = '🤒🤒🤒出了一点小问题，请稍后重试下...';
    if (rawmsg === "结束对话") {
        geminiPool.delete(id);
        response = `${nick}的对话已结束`
        return response
    } else {

        const datatime = Date.now()
        const messages = geminiPool.get(id) ? [...geminiPool.get(id).messages, {
            "role": "user",
            "parts": [{
                "text": rawmsg
            }]
        }] : [{
            "role": "user",
            "parts": [{
                "text": rawmsg
            }]
        }];


        const newMessage = {
            datatime: datatime,
            messages
        };
        const data = JSON.stringify({
            "contents": [messages]
        });
        let raw_response
        try {
            raw_response = await requestPromise({
                url: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${process.env.GEMINI_API_KEY}`,
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'bot'
                },
                body: data,
                method: 'POST',

            })
            // 检查返回的数据是否包含 choices 字段
            // console.log(raw_response.data.candidates[0].content);
            if (raw_response.data.candidates[0].content) {
                const response = raw_response.data.candidates[0].content.parts[0].text
                console.log(`chat:${wxid}------${id}\nresponse: ${response.content}`);
                // 只有在成功获取到回复时，才将原始消息添加到对话池中
                if (response) {
                    geminiPool.set(id, newMessage);
                }
                // data.candidates[0].content
                geminiPool.get(id).messages.push(raw_response.data.candidates[0].content);
                return `${rawmsg} \n ------------------------ \n${response}`;
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
    const promises = Array.from(geminiPool.entries())
        .filter(([key, value]) => now - value.datatime >= 1000 * 600)
        .map(([key, value]) =>
            new Promise((resolve, reject) => {
                geminiPool.delete(key);
                resolve();
            })
        );

    try {
        await Promise.all(promises);
        console.log('Keys deleted successfully');
        //   console.log(geminiPool);
    } catch (err) {
        console.error(err);
    }
};

// 每隔30分钟执行一次clearMap()方法
schedule.scheduleJob('*/30 * * * *', clearMap);


export default geminReply