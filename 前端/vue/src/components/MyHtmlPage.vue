<template>
  <div class="container mt-5">
    <!-- 云朵背景 -->
    <div id="cloud-background" class="cloud-background"></div>

    <!-- 内容区域 -->
    <h1 class="text-center text-primary fw-bold">高光谱图像分类系统</h1>
    <p class="text-center text-muted mb-5">简单快速地分类高光谱图像</p>
    <hr />

    <!-- 文件上传区域 -->
    <div class="card shadow-lg p-4 mb-5">
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
        <button type="submit" class="btn btn-primary mt-2 w-100">上传并分类</button>
      </form>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="progress-container mt-4">
      <div class="progress-bar" :style="{ width: progress + '%' }">
        {{ progress }}%
      </div>
    </div>

    <!-- 分类结果显示 -->
    <div v-if="resultMessage" class="card shadow-lg mt-5 p-4">
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
    <div class="card shadow-lg p-4 mt-5">
      <h4 class="mb-4 text-secondary">AI 问答</h4>
      <textarea
          v-model="question"
          class="form-control"
          rows="4"
          placeholder="请输入问题..."></textarea>
      <button
          @click="submitQuestion"
          class="btn btn-primary mt-3 w-100"
          :disabled="loading">
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
import * as THREE from 'three'; // 导入 THREE.js

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
    },

    initCloudEffect() {
      if (typeof THREE === 'undefined') return;

      const container = document.getElementById('cloud-background');
      const width = window.innerWidth;
      const height = window.innerHeight;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(width, height);
      container.appendChild(renderer.domElement);

      // 云朵纹理
      const texture = new THREE.TextureLoader().load('/cloud10.png');  // 使用 public 目录下的路径
      const material = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        opacity: 0.8,
      });
      const geometry = new THREE.PlaneGeometry(8000, 8000);

      // 添加多个云朵
      for (let i = 0; i < 30; i++) {
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(
            Math.random() * width - width / 2,
            Math.random() * height - height / 2,
            Math.random() * 1000 - 500
        );
        mesh.rotation.z = Math.random() * Math.PI;
        scene.add(mesh);
      }

      camera.position.z = 800;

      function animate() {
        requestAnimationFrame(animate);
        scene.children.forEach((child) => {
          child.position.x += 0.1;
          if (child.position.x > width) child.position.x = -width;
        });
        renderer.render(scene, camera);
      }

      animate();
    }
  },
  mounted() {
    this.initCloudEffect();  // 页面加载后启动云朵效果
  },
};
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: auto;
  padding: 20px;
  position: relative; /* 确保云朵背景不会干扰前端内容 */
}

.card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
}

#cloud-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1; /* 确保它在背景中 */
}

.progress-container {
  background: #f4f4f4;
  border-radius: 8px;
  height: 20px;
  margin-top: 15px;
  width: 100%;
}

.progress-bar {
  background: #28a745;
  height: 100%;
  border-radius: 8px;
  text-align: center;
  color: white;
  font-weight: bold;
  line-height: 20px;
}

textarea.form-control {
  resize: none;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #ddd;
}

textarea.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.3);
}
</style>
