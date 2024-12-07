// src/services/websocket.js

class WebSocketService {
    constructor() {
      this.socket = null;
    }
  
    // 连接 WebSocket
    connect() {
      this.socket = new WebSocket('wss://2530-211-64-159-126.ngrok-free.app/ws');  // 使用 Ngrok 提供的 WebSocket 地址
      this.socket.onopen = () => {
        console.log('WebSocket connection established');
      };
      this.socket.onmessage = (event) => {
        console.log('Message from server: ', event.data);
      };
      this.socket.onerror = (error) => {
        console.error('WebSocket Error: ', error);
      };
      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
      };
    }
  
    // 发送消息到 WebSocket
    sendMessage(message) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(message);
      } else {
        console.error('WebSocket is not open');
      }
    }
  
    // 关闭 WebSocket 连接
    close() {
      if (this.socket) {
        this.socket.close();
      }
    }
  }
  
  export default new WebSocketService();
  