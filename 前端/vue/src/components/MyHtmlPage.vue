<template>
  <div class="container">
    <div class="content-wrapper">
      <!-- 左侧：文件上传区域 -->
      <div class="upload-section">
        <div class="card shadow p-4">
          <h1 class="text-center text-primary fw-bold">高光谱图像分类系统</h1>
          <h4 class="mb-4 text-secondary">上传高光谱图像</h4>
          
          <!-- 插入图片 -->
          <div class="image-container mb-6"> <!-- 增加了 mb-6 来增加间距 -->
            <img src="@/assets/aaa.png" alt="High Spectral Image" class="img-fluid" />
          </div>
          
          <form @submit.prevent="handleFileUpload">
            <div class="mb-3">
              <label for="fileInput" class="form-label">选择文件：</label>
              <input
                type="file"
                class="form-control"
                id="fileInput"
                @change="handleFileChange"
                accept=".mat,.tif"
                required
              />
            </div>
            <!-- 调整按钮的上间距 -->
            <button type="submit" class="btn btn-gradient-primary mt-4 w-100">上传并分类</button>
          </form>
        </div>
            <!-- 上传进度 -->
    <div v-if="uploading" class="progress-container mt-4">
      <div
        class="progress-bar"
        :style="{ width: progress + '%' }"
      >
        {{ progress }}%
      </div>
    </div>

    <!-- 分类结果显示 -->
    <div v-if="resultMessage" class="card shadow mt-5 p-4">
      <h4 class="text-success">分类结果</h4>
      <p>{{ resultMessage }}</p>
      <div v-if="predictions.length" class="prediction-results mt-3">
        <h5>预测结果:</h5>
        <ul class="list-group">
          <li v-for="(prediction, index) in predictions" :key="index" class="list-group-item">
            样本 {{ index + 1 }}: {{ prediction }}
          </li>
        </ul>
      </div>
    </div>
      </div>

      <!-- 右侧：AI 问答区域 -->
      <div class="chat-section">
        <div class="card shadow p-4">
          <h4 class="mb-4 text-secondary">AI 问答</h4>

          <!-- 对话历史 -->
          <div class="chat-history mb-3" v-if="conversation.length">
            <div v-for="(msg, index) in conversation" :key="index" :class="{'user-msg': msg.role === 'user', 'ai-msg': msg.role === 'ai'}">
              <p><strong>{{ msg.role === 'user' ? '用户' : 'AI' }}:</strong> {{ msg.content }}</p>
            </div>
          </div>

          <!-- 输入框和按钮 -->
          <div class="input-section">
            <textarea
              v-model="question"
              class="form-control"
              rows="2"
              placeholder="请输入问题..."
            ></textarea>
            <button
              @click="submitQuestion"
              class="btn btn-gradient-primary mt-3 w-100"
              :disabled="loading || !question.trim()"
            >
              提交问题
            </button>
            <div v-if="loading" class="mt-3 text-muted">正在获取回答...</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
      uploading: false,
      progress: 0,
      resultMessage: "",
      predictions: [],
      question: "",
      answer: "",
      loading: false,
      conversation: [], // 存储对话历史
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },

    async handleFileUpload() {
      if (!this.selectedFile) {
        alert("请选择一个文件进行上传！");
        return;
      }

      this.uploading = true;
      this.progress = 0;

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        const interval = setInterval(() => {
          if (this.progress < 100) {
            this.progress += 10;
          }
        }, 200);

        const response = await fetch("http://localhost:8080/api/uploadfile", {
          method: "POST",
          body: formData,
        });

        clearInterval(interval);

        if (!response.ok) {
          const errorData = await response.text();
          throw new Error(errorData || "上传失败");
        }

        this.progress = 100;

        // 处理下载文件
        const blob = await response.blob(); // 获取文件数据
        const link = document.createElement('a');
        const url = window.URL.createObjectURL(blob);
        link.href = url;
        link.setAttribute('download', 'predictions.json'); // 设置下载的文件名
        document.body.appendChild(link);
        link.click(); // 触发下载
        window.URL.revokeObjectURL(url);

      } catch (error) {
        this.resultMessage = "发生错误：" + error.message;
        this.predictions = [];
      } finally {
        this.uploading = false;
      }
    },

    submitQuestion() {
      if (!this.question.trim()) {
        alert("请输入问题！");
        return;
      }

      // 清空之前的答案
      this.answer = "";
      this.loading = true;

      // 1. 向后端发送问题 (POST 请求)
      fetch("http://localhost:8080/ai/send", {
        method: "POST",  // 确保使用 POST 请求
        body: JSON.stringify({ question: this.question }),  // 发送问题内容
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => {
          if (response.ok) {
            return response.text();  // 获取完整的回答
          } else {
            return response.json().then((data) => {
              console.error("错误：", data.message);
              alert(data.message); // 提示错误信息
            });
          }
        })
        .then((answer) => {
          if (answer) {
            this.conversation.push({ role: "user", content: this.question }); // 添加用户提问到对话历史
            this.conversation.push({ role: "ai", content: answer }); // 添加AI回答到对话历史
            this.question = ""; // 清空输入框
          }
          this.loading = false;  // 停止加载状态
        })
        .catch((error) => {
          console.error("请求失败:", error);
          this.loading = false;
        });
    },
  },
};

</script>

<style scoped>
html {
  height: 100%;
}
body {
  height: 100%;
  margin: 0;
}
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-image: linear-gradient(to right, #fbc2eb, #a6c1ee);
}
.content-wrapper {
  display: flex;
  width: 80%; /* 调整整体宽度 */
  max-width: 1400px;
  height: 90%; /* 高度占90% */
}

.upload-section,
.chat-section {
  flex: 1; /* 两个区域占据等分宽度 */
  margin: 10px;
  display: flex;
  flex-direction: column; /* 使内容上下排列 */
  justify-content: flex-start; /* 向上对齐 */
}

.card {
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* 增加阴影效果 */
  background-color: white; /* 设置卡片背景色为白色 */
  opacity: 0.8; /* 可选：调整透明度 */
  flex: 1; /* 使卡片在区域内填满 */
  padding: 20px;
  display: flex;
  flex-direction: column; /* 使内容上下排列 */
}

h1, h4 {
  font-size: 2rem; /* 调整标题字体大小 */
}

h4, .form-label, .btn {
  font-size: 1.2rem; /* 增加字体大小 */
}

textarea {
  font-size: 1.1rem; /* 调整文本框内文字大小 */
  height: 90px; /* 使输入框更适中 */
  width: 100%; /* 确保输入框占满可用宽度 */
  resize: none; /* 禁止改变大小 */
  padding: 10px; /* 增加内边距 */
}

.btn {
  background-image: linear-gradient(to right, #a6c1ee, #fbc2eb);
  color: white;
}

.progress-container {
  margin-top: 20px;
}

.progress-bar {
  height: 20px;
  background-color: #4caf50;
  text-align: center;
  color: white;
  line-height: 20px;
}

.chat-history {
  max-height: 400px; /* 增加聊天历史的最大高度 */
  overflow-y: auto;
  margin-bottom: 15px;
}

.chat-history .user-msg {
  background-color: #d1e7ff;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
  max-width: 80%;
  margin-left: auto;
}

.chat-history .ai-msg {
  background-color: #f1f1f1;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
  max-width: 80%;
  margin-right: auto;
}

/* Ensuring input section is at the bottom */
.input-section {
  margin-top: auto; /* Push input section to the bottom */
}

/* 调整选择文件输入框和按钮之间的间距 */
.mb-3 {
  margin-bottom: 2rem; /* 增加间距 */
}

.mt-4 {
  margin-top: 2rem; /* 增加按钮的上间距 */
}

/* 新增图片容器样式 */
.image-container {
  margin-bottom: 3rem; /* 增加图片和选择文件之间的间距 */
}

.btn-gradient-primary {
  background: linear-gradient(to right, #007bff, #0056b3);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  transition: background 0.3s;
}

.btn-gradient-primary:hover {
  background: linear-gradient(to right, #0056b3, #003f8f);
}

.progress-container {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 5px;
}

.progress-bar {
  background: linear-gradient(to right, #28a745, #218838);
  height: 20px;
  border-radius: 10px;
  text-align: center;
  color: #fff;
  font-weight: bold;
  line-height: 20px;
}

.list-group-item {
  border: none;
  background-color: #f8f9fa;
}

img {
  max-width: 100%;
  height: auto;
}
</style>
