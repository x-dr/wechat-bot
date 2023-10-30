import dayjs from 'dayjs';
import crypto from 'crypto';
import WebSocket from 'ws';

class ChatClient {
  constructor(APIKey, APISecret, APPID, UID, host) {
    this.APIKey = APIKey;
    this.APISecret = APISecret;
    this.APPID = APPID;
    this.UID = UID;
    this.host = host || 'spark-api.xf-yun.com';
    this.req_path = '/v3.1/chat';
    this.ws = null;
    // this.conversationPool = new Map();
  }

  async connect() {
    const gmtDate = new Date().getTime() + ((new Date().getTimezoneOffset() / 60) * 60 * 60 * 1000);
    const date = dayjs(gmtDate).format('ddd[,] DD MMM YYYY HH:mm:ss [GMT]');

    const tmp = `host: ${this.host}\ndate: ${date}\nGET ${this.req_path} HTTP/1.1`;
    const tmp_sha = crypto.createHmac('sha256', this.APISecret).update(tmp).digest();
    const signature = tmp_sha.toString('base64');
    const authorization_origin = `api_key="${this.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="${signature}"`;
    const authorization = Buffer.from(authorization_origin).toString('base64');

    const url = `wss://${this.host}${this.req_path}?authorization=${encodeURIComponent(authorization)}&date=${encodeURIComponent(date).replace(new RegExp('%20', 'g'), '+')}&host=${encodeURIComponent(this.host)}`;
    // console.log(url);
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      this.ws.on('open', () => {
        resolve();
      });

      this.ws.on('error', (err) => {
        reject(err);
      });
    });
  }

  async sendMessage(message) {
    // console.log(message);
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket connection is not open.');
    }

    const payload = {
      header: {
        app_id: this.APPID,
        uid: this.UID
      },
      parameter: {
        chat: {
          domain: 'generalv3',
          temperature: 0.5,
          max_tokens: 4096,
        }
      },
      payload: {
        message: {
          text: message
        }
      }
    };

    this.ws.send(JSON.stringify(payload));
  }

  async receiveMessages() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket connection is not open.');
    }

    return new Promise((resolve, reject) => {
      const texts = [];

      this.ws.on('message', (data) => {
        const obj = JSON.parse(data);
        // console.log(obj.payload.choices);
        const text = obj.payload.choices.text;
        text.forEach(item => {
          texts.push(item.content);
        });

        if (obj.payload.choices.status === 2) {
          //   resolve(texts);
          resolve(texts.join(''));
        }
      });

      this.ws.on('error', (err) => {
        reject(err);
      });
    });
  }

  async close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
  }
}

export default ChatClient;
