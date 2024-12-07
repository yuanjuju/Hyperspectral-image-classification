<template>
  <div class="container mt-5">
    <h1 class="text-center text-primary fw-bold">高光谱图像分类系统</h1>
    <p class="text-center text-muted">简单快速地分类高光谱图像</p>
    <hr />

    <!-- 文件上传区域 -->
    <div class="card shadow p-4 mb-4">
      <h4 class="mb-4 text-secondary">上传高光谱图像</h4>
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
        <button type="submit" class="btn btn-gradient-primary mt-2">上传并分类</button>
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

    <!-- AI 问答区域 -->
    <div class="card shadow p-4 mt-5">
      <h4 class="mb-4 text-secondary">AI 问答</h4>
      <textarea
        v-model="question"
        class="form-control"
        rows="3"
        placeholder="请输入问题..."
      ></textarea>
      <button
        @click="submitQuestion"
        class="btn btn-gradient-primary mt-3"
        :disabled="loading"
      >
        提交问题
      </button>

      <div v-if="loading" class="mt-3 text-muted">正在获取回答...</div>

      <div v-if="answer" class="mt-4">
        <h5 class="text-success">AI 回答：</h5>
        <p>{{ answer }}</p>
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
          const errorData = await response.json();
          throw new Error(errorData.error || "上传失败");
        }

        this.progress = 100;

        const result = await response.json();
        if (result.predictions) {
          this.resultMessage = "分类成功！以下是预测结果：";
          this.predictions = result.predictions;
        } else {
          this.resultMessage = "分类完成，但未返回预测结果。";
          this.predictions = [];
        }
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
    .then(response => {
        if (response.ok) {
            return response.text();  // 获取完整的回答
        } else {
            return response.json().then(data => {
                console.error("错误：", data.message);
                alert(data.message); // 提示错误信息
            });
        }
    })
    .then(answer => {
        if (answer) {
            this.answer = answer;  // 将完整的 AI 回答显示到页面上
        }
        this.loading = false;  // 停止加载状态
    })
    .catch(error => {
        console.error("请求失败:", error);
        this.loading = false;
    });
}




  },
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: auto;
}

.card {
  border-radius: 12px;
  border: none;
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
