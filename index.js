import WebSocket from 'ws'
import rp from 'request-promise'
import chatgptReply from "./utils/chatgpt.js"
import sparkReply from "./utils/sparkmsg.js"
import geminReply from "./utils/gemini.js"
import { containsTextFileLine } from "./utils/checkword.js"
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()
import {
    get_personal_info,
    getid,
    get_chat_nick_p,
    get_chat_nick,
    handle_nick,
    handle_memberlist,
    get_chatroom_memberlist,
    send_attatch,
    send_at_msg,
    send_pic_msg,
    get_personal_detail,
    send_txt_msg,
    get_contact_list,
    handle_wxuser_list,
    handle_recv_msg,
    heartbeat,
    debug_switch,
    get_member_nick
} from "./server/client.js"

import MessageType from './server/messagetype.js'
const SERVER_HOST = process.env.SERVER_HOST
const ws = new WebSocket(`ws://${SERVER_HOST}`);
const url = `http://${SERVER_HOST}`;




ws.on('open', async function open() {
    ws.send(get_personal_info());
    //通讯录
    // ws.send( get_contact_list());
    // const j = await get_personal_info1();
    // console.log(j);
    // ws.send(await get_personal_info1());

});



ws.on('message', async (data) => {
    //break;
    //return;

    // console.log(data);
    //ws.send("hello world");
    // return;
    const j = JSON.parse(data);
    // handle_wxuser_list(j)
    console.log(j);
    const type = j.type;
    switch (type) {
        case MessageType.CHATROOM_MEMBER_NICK:
            console.log(j);
            handle_nick(j);
            break;
        case MessageType.PERSONAL_DETAIL:
            console.log(j);
            break;
        case MessageType.AT_MSG:
            console.log(j);
            break;
        case MessageType.DEBUG_SWITCH:
            console.log(j);
            break;
        case MessageType.PERSONAL_INFO:
            console.log(j);
            break;
        case MessageType.TXT_MSG:
            // console.log(j);
            break;
        case MessageType.PIC_MSG:
            console.log(j);
            break;
        case MessageType.CHATROOM_MEMBER:
            // console.log(j);
            handle_memberlist(j);
            break;
        case MessageType.RECV_PIC_MSG:
            handle_recv_msg(j);
            break;
        case MessageType.RECV_TXT_MSG:
            const user_id = j.id1 ? j.id1 : j.wxid;
            const raw_msgdata = await get_member_nick(user_id, j.wxid)
            const msgdata = JSON.parse(raw_msgdata.content)
            const roomid = msgdata.roomid
            const userid = msgdata.wxid
            const nick = msgdata.nick
            const msgcontent = j.content
            console.log({ userid, nick, roomid, msgcontent })
            if (j.content.startsWith('/c')) {
                const raw_msg = j.content.replace('/c', '').trim()
                // userid, nick, roomid, msgcontent
                const msg = await chatgptReply(roomid, userid, nick, raw_msg)
                //    await  send_txt_msg1(j.wxid, j.content)
                const new_msg = await containsTextFileLine(msg)
                ws.send(send_txt_msg(roomid, new_msg));
            }
            if(j.content.startsWith('/s')){
                const raw_msg = j.content.replace('/s', '').trim()
                // userid, nick, roomid, msgcontent
                const msg = await sparkReply(roomid, userid, nick, raw_msg)
                //    await  send_txt_msg1(j.wxid, j.content)
                // const new_msg = await containsTextFileLine(msg)
                ws.send(send_txt_msg(roomid, msg));
            }
            if(j.content.startsWith('/g')){
                const raw_msg = j.content.replace('/g', '').trim()
                // userid, nick, roomid, msgcontent
                const msg = await geminReply(roomid, userid, nick, raw_msg)
                //    await  send_txt_msg1(j.wxid, j.content)
                // const new_msg = await containsTextFileLine(msg)
                ws.send(send_txt_msg(roomid, msg));
            }
            break;
        case MessageType.HEART_BEAT:
            heartbeat(j);
            break;
        case MessageType.USER_LIST:
            console.log(j);
            //handle_wxuser_list(j);
            break;
        case MessageType.GET_USER_LIST_SUCCSESS:
            handle_wxuser_list(j);
            break;
        case MessageType.GET_USER_LIST_FAIL:
            handle_wxuser_list(j);
            break;
        case MessageType.NEW_FRIEND_REQUEST:
            //console.log("---------------37----------");
            console.log(j);
            break;
        case MessageType.AGREE_TO_FRIEND_REQUEST:
            console.log("---------------25----------");
            console.log(j);
            break;
        //case SEND_TXT_MSG_SUCCSESS:
        //handle_recv_msg(j);
        //break;
        //case SEND_TXT_MSG_FAIL:
        //handle_recv_msg(j);
        //break;
        default:
            break;
    }
    // console.log(`Roundtrip time: ${Date.now() - data} ms`);

    /*setTimeout(function timeout() {
      ws.send(Date.now());
    }, 500);*/
});


ws.on('close', function close() {
    console.log('disconnected');
});