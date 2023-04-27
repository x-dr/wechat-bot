/****************************************
 * get_chat_nick_p()
 * get_contact_list()
 * get_chatroom_memberlist()
 * send_at_msg()
 * send_attatch()
 * send_txt_msg()
 * send_pic_msg()
 * get_personal_info()
 * ***************************************/
import WebSocket from 'ws'
import rp from 'request-promise'
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()
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





export const getid = () => {
    const id = Date.now();
    return id.toString();
}


export const get_chat_nick_p = (s_wxid, s_roomid) => {

    const j = {
        id: getid(),
        type: CHATROOM_MEMBER_NICK,
        wxid: s_wxid,
        roomid: s_roomid,
        content: 'null',
        nickname: "null",
        ext: 'null'


    };
    const s = JSON.stringify(j);
    return s;

}
export const get_chat_nick = () => {
    const j = {
        id: getid(),
        type: CHATROOM_MEMBER_NICK,
        content: '24354102562@chatroom',//chatroom id 23023281066@chatroom  17339716569@chatroom
        //5325308046@chatroom
        //5629903523@chatroom
        wxid: 'ROOT'
    };
    const s = JSON.stringify(j);
    return s;
}

export const handle_nick = (j) => {
    const data = j.content;
    let i = 0;
    for (const item of data) {
        console.log(i++, item.nickname)
    }
}
export const handle_memberlist = (j) => {
    const data = j.content;
    let i = 0;
    //get_chat_nick_p(j.roomid);
    for (const item of data) {
        console.log("---------------", item.room_id, "--------------------");
        //console.log("------"+item.roomid+"--------");
        //ws.send(get_chat_nick_p(item.roomid));
        const memberlist = item.member;

        //console.log("hh",item.address,memberlist);

        //const len = memberlist.length();
        //console.log(memberlist);
        for (const m of memberlist) {
            console.log(m);//获得每个成员的wxid
        }
        /*for(const n of nicklist)//目前不建议使用
        {
          console.log(n);//获得每个成员的昵称，注意，没有和wxi对应的关系
        }*/
    }
}
export const get_chatroom_memberlist = () => {
    const j = {
        id: getid(),
        type: CHATROOM_MEMBER,
        roomid: 'null',//null
        wxid: 'null',//not null
        content: 'null',//not null
        nickname: 'null',
        ext: 'null'
    };
    // console.log(j);
    const s = JSON.stringify(j);
    return s;
}
export const send_attatch = () => {
    /*const j={
      id:getid(),
      type:ATTATCH_FILE,
      content:'C:\\tmp\\log.txt',
      wxid:'23023281066@chatroom'
    };*/
    const j = {
        id: getid(),
        type: ATTATCH_FILE,
        wxid: '23023281066@chatroom',//roomid或wxid,必填
        roomid: 'null',//此处为空
        content: 'C:\\tmp\\log.7z',
        nickname: "null",//此处为空
        ext: 'null'//此处为空
        //wxid:'22428457414@chatroom'

    };
    const s = JSON.stringify(j);
    return s;
}
export const send_at_msg = (roomid, wxid, content, nickname = '') => {
    const j = {
        id: getid(),
        type: AT_MSG,
        roomid: roomid,//not null  23023281066@chatroom
        wxid: wxid,//at
        content: content,//not null
        nickname: nickname,
        ext: 'null'
    };

    const s = JSON.stringify(j);
    return s;
}

export const send_pic_msg = () => {
    const j = {
        id: getid(),
        type: PIC_MSG,
        wxid: '22693709597@chatroom',
        roomid: 'null',
        content: "img",
        nickname: "null",
        ext: 'null'
        //wxid:'22428457414@chatroom'

    };

    const s = JSON.stringify(j);
    //console.log(s);
    return s;
}
export const get_personal_detail = () => {
    /*const j={
      id:getid(),
      type:PERSONAL_DETAIL,
      content:'op:personal detail',
      wxid:'zhanghua_cd'
    };*/
    const s = JSON.stringify(j);
    return s;
}
/**
 * send_txt_msg : 发送消息给好友
 * 
 */
export const get_personal_info = () => {
    const j = {
        id: getid(),
        type: PERSONAL_INFO,
        wxid: 'null',
        roomid: 'null',
        content: 'null',
        nickname: "null",
        ext: 'null'
        //wxid:'22428457414@chatroom'

    };
    const s = JSON.stringify(j);
    return s;
}
export const send_txt_msg = (wxid, content) => {

    //必须按照该json格式，否则服务端会出异常
    const j = {
        id: getid(),
        type: TXT_MSG,
        wxid: wxid,//roomid或wxid,必填
        roomid: 'null',//此处为空
        content: content,
        nickname: "null",//此处为空
        ext: 'null'//此处为空
        //wxid:'22428457414@chatroom'

    };
    /*const j={
      id:getid(),
      type:TXT_MSG,
      content:'hello world',//文本消息内容
      
    };*/
    const s = JSON.stringify(j);
    return s;
}
/**
 * send_wxuser_list  : 获取微信通讯录用户名字和wxid
*/
export const get_contact_list = () => {
    /*const j={
      id:getid(),
      type:USER_LIST,
      content:'user list',
      wxid:'null'
    };*/

    const j = {
        id: getid(),
        type: USER_LIST,
        roomid: 'null',//null
        wxid: 'null',//not null
        content: 'null',//not null
        nickname: 'null',
        ext: 'null'
    };
    const s = JSON.stringify(j);
    //console.log(s);
    return s;
}
/**
 * handle_wxuser_list  : websocket返回的用户信息
 * @param {*} j json数组
 *              数组里面的wxid，要保存下来，供发送微信的时候用
 * 
 */
export const handle_wxuser_list = (j) => {
    const j_ary = j.content;
    var i = 0;
    for (const item of j_ary) {
        i = i + 1;
        const id = item.wxid;
        const m = id.match(/@/);
        if (m != null) {
            //console.log(id);
            console.log(item.wxid, item.name);
        }
        //console.log(m);
        //
    }
}
/**
 * 
 * @param {*} j json对象
 */
export const handle_recv_msg = (j) => {

    const content = j.content;
    const wxid = j.wxid;
    const sender = j.id1;
    // sender} === ''? '' : '发送人：-->${sender}';

    const sender1 = sender === '' ? '' : `发送人：--> ${sender} `;
    console.log(`对话窗口:-->${wxid}\n${sender1}\n内容：-->${content}`);


    //  console.log(j);
}

export const heartbeat = (j) => {
    console.log(j);
    //console.log(utf16ToUtf8(wxid),utf16ToUtf8(name));
}

export const debug_switch = () => {
    const qs = {
        "id": getid(),
        "type": DEBUG_SWITCH,
        "content": "on",
        "wxid": "",
    }
    const s = JSON.stringify(qs)
    return s
}






export const get_member_nick = async (user_id, roomid) => {

    const jpara = {
        id: getid(),
        type: CHATROOM_MEMBER_NICK,
        wxid: user_id,
        roomid: roomid,//23023281066@chatroom
        content: 'null',
        nickname: "null",
        ext: 'null'
        //wxid:'22428457414@chatroom'

    };
    const options =
    {

        url: url + '/api/getmembernick',
        body: {
            para: jpara
        },
        json: true
    };
    const data = await rp(options);
    //const j = JSON.parse(data);

    //console.log(j.id); 
    //console.log(j.status);
    return data;
}
