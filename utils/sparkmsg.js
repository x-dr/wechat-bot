import ChatClient from './spark.js';
import schedule from "node-schedule"
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()


const sparkPool = new Map();

async function sparkReply(wxid, id, nick, rawmsg) {
  console.log(`chat:${wxid}-------${id}\nrawmsg: ${rawmsg}`);

  // let response = '🤒🤒🤒出了一点小问题，请稍后重试下...';
  const sparkAPIKey =  process.env.sparkAPIKey || 'xxx';
  const sparkAPISecret = process.env.sparkAPISecret || 'xxxm';
  const sparkAPPID = process.env.sparkAPPID || 'xxx9a';
  const sparkUID = process.env.sparkUID || 'wx';

  if (rawmsg === "结束对话") {
    sparkPool.delete(id);
    const response = `${nick}的对话已结束`
    return response
  } else {
    const client = new ChatClient(sparkAPIKey, sparkAPISecret, sparkAPPID, sparkUID);
    try {
      const datatime = Date.now()
      const messages = sparkPool.get(id) ? [...sparkPool.get(id).messages, { role: 'user', content: rawmsg }] : [{ role: 'user', content: rawmsg }]
      const newMessage = { datatime: datatime, messages };
      await client.connect();

      await client.sendMessage(messages);

      const responses = await client.receiveMessages();
      const assistantmsg= {"role": "assistant", "content": responses}
      if(responses){
        sparkPool.set(id, newMessage);
        sparkPool.get(id).messages.push(assistantmsg)
      }
      return `${rawmsg} \n ------------------------ \n${responses}`;
    } catch (err) {
      console.error('Error:', err);
      return err
    } finally {
      await client.close();
    }

  }


}


const clearMap = async () => {
  const now = Date.now();
  const promises = Array.from(sparkPool.entries())
    .filter(([key, value]) => now - value.datatime >= 1000 * 600)
    .map(([key, value]) =>
      new Promise((resolve, reject) => {
        sparkPool.delete(key);
        resolve();
      })
    );

  try {
    await Promise.all(promises);
    console.log('Keys deleted successfully');
    //   console.log(sparkPool);
  } catch (err) {
    console.error(err);
  }
};

// 每隔30分钟执行一次clearMap()方法
schedule.scheduleJob('*/30 * * * *', clearMap);



export default sparkReply