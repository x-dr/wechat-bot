import WebSocket from 'ws'
import rp from 'request-promise'
import chatgptReply from "./utils/chatgpt.js"
import sparkReply from "./utils/sparkmsg.js"
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


const SERVER_HOST = process.env.SERVER_HOST
const ws = new WebSocket(`ws://${SERVER_HOST}`);
const url = `http://${SERVER_HOST}`;
const HEART_BEAT = 5005;
const RECV_TXT_MSG = 1;
const RECV_PIC_MSG = 3;
const USER_LIST = 5000;
const GET_USER_LIST_SUCCSESS = 5001;
const GET_USER_LIST_FAIL = 5002;
const TXT_MSG = 555;
const PIC_MSG = 500;
const AT_MSG = 550;
const CHATROOM_MEMBER = 5010;
const CHATROOM_MEMBER_NICK = 5020;
const PERSONAL_INFO = 6500;
const DEBUG_SWITCH = 6000;
const PERSONAL_DETAIL = 6550;
const DESTROY_ALL = 9999;
const NEW_FRIEND_REQUEST = 37;//微信好友请求消息
const AGREE_TO_FRIEND_REQUEST = 10000;//同意微信好友请求消息
const ATTATCH_FILE = 5003;



ws.on('open', async function open() {
    ws.send(get_personal_info());
    //通讯录
    // ws.send( get_contact_list());
    // const j = await get_personal_info1();
    // console.log(j);
    // ws.send(await get_personal_info1());

});

async function send_txt_msg1(wxid, content) {
    const jpara = {
        id: getid(),
        type: TXT_MSG,
        wxid: wxid,//roomid或wxid,必填
        roomid: 'null',//此处为空
        content: 'hello word',
        nickname: "null",//此处为空
        ext: 'null'//此处为空
        //wxid:'22428457414@chatroom'

    };
    const options =
    {
        //method: 'GET',
        //url: 'https://apis.map.qq.com/ws/district/v1/list',
        url: url + '/api/sendtxtmsg',
        body: {
            para: jpara
        },
        json: true
    };
    let data = rp(options);
    //const j = JSON.parse(data);

    //console.log(j.id); 
    //console.log(j.status);
    return data;


}

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
        case CHATROOM_MEMBER_NICK:
            console.log(j);
            handle_nick(j);
            break;
        case PERSONAL_DETAIL:
            console.log(j);
            break;
        case AT_MSG:
            console.log(j);
            break;
        case DEBUG_SWITCH:
            console.log(j);
            break;
        case PERSONAL_INFO:
            console.log(j);
            break;
        case TXT_MSG:
            // console.log(j);
            break;
        case PIC_MSG:
            console.log(j);
            break;
        case CHATROOM_MEMBER:
            // console.log(j);
            handle_memberlist(j);
            break;
        case RECV_PIC_MSG:
            handle_recv_msg(j);
            break;
        case RECV_TXT_MSG:
            // handle_recv_msg(j);
            // console.log("11");
            // ws.send("hello world");
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
            break;
        case HEART_BEAT:
            heartbeat(j);
            break;
        case USER_LIST:
            console.log(j);
            //handle_wxuser_list(j);
            break;
        case GET_USER_LIST_SUCCSESS:
            handle_wxuser_list(j);
            break;
        case GET_USER_LIST_FAIL:
            handle_wxuser_list(j);
            break;
        case NEW_FRIEND_REQUEST:
            //console.log("---------------37----------");
            console.log(j);
            break;
        case AGREE_TO_FRIEND_REQUEST:
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