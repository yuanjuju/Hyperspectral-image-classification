<template>
  <div class="login-page">
    <!-- 背景图 -->
    <img src="@/assets/background.jpg" alt="背景图" class="background-img" />
  
    <!-- 左上角标题 -->
    <div class="title">
      <div class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
      </div>
      <div class="title-text">
        <h1>中国海洋大学</h1>
        <p>高光谱图像分类系统</p>
      </div>
    </div>
  
    <!-- 左上和右下的标语 -->
    <div class="slogans">
      <p class="slogan-top-left">取则行远</p>
      <p class="slogan-bottom-right">海纳百川</p>
    </div>
  
    <!-- 登录框 -->
    <div class="login-box">
      <div class="tabs">
        <span 
          class="tab" 
          :class="{ active: activeTab === 'account' }" 
          @click="activeTab = 'account'"
        >账号登录</span>
        <span 
          class="tab" 
          :class="{ active: activeTab === 'phone' }" 
          @click="activeTab = 'phone'"
        >手机号登录</span>
      </div>
      <div class="form">
        <!-- 账号登录 -->
        <template v-if="activeTab === 'account'">
          <div class="input-group">
            <input v-model="sno" type="text" placeholder="工号/学号" />
          </div>

          <div class="input-group">
            <input v-model="password" type="password" placeholder="请输入密码" />
          </div>
        </template>

        <!-- 手机号登录 -->
        <template v-else>
          <div class="input-group">
            <input v-model="phone" type="text" placeholder="请输入手机号" />
          </div>

          <div class="input-group code-input">
            <input v-model="code" type="text" placeholder="请输入验证码" />
            <button 
              class="code-button" 
              :disabled="isCodeLoading || codeTimer > 0" 
              @click="sendCode"
            >
              {{ codeTimer > 0 ? `${codeTimer}s后重试` : '获取验证码' }}
            </button>
          </div>
        </template>

        <button 
          class="login-button" 
          @click="handleLogin" 
          :class="{'loading': isLoading}" 
          :disabled="isLoading"
        >
          登录
        </button>

        <!-- 记住密码、忘记密码、帮助说明的布局 -->
        <div class="remember-help">
          <label class="remember-password">
            <input type="checkbox" v-model="rememberMe" /> 记住密码
          </label>
          <router-link to="/find-password">忘记密码</router-link>

          <button class="register-button" @click="toggleRegisterForm">注册账号</button> <!-- 注册按钮 -->
        </div>
  
        <!-- 注册表单弹窗 -->
        <div v-if="showRegisterForm" class="register-form">
          <h3>注册账号</h3>
          <div class="input-group">
            <input v-model="newPhone" type="text" placeholder="请输入手机号" />
          </div>
          <div class="input-group code-input">
            <input v-model="newCode" type="text" placeholder="请输入验证码" />
            <button 
              class="code-button" 
              :disabled="isCodeLoading || codeTimer > 0" 
              @click="sendRegisterCode"
            >
              {{ codeTimer > 0 ? `${codeTimer}s后重试` : '获取验证码' }}
            </button>
          </div>
          <div class="input-group">
            <input v-model="newPassword" type="password" placeholder="设置密码" />
          </div>
          <div class="input-group">
            <input v-model="newConfirmPassword" type="password" placeholder="确认密码" />
          </div>
          <button class="register-submit" @click="submitRegister">提交注册</button>
          <button class="register-close" @click="toggleRegisterForm">关闭</button>
          <div v-if="registerErrorMessage" class="error-message">{{ registerErrorMessage }}</div>
        </div>

        <!-- 学号确认弹窗 -->
        <div v-if="showSnoConfirmation" class="sno-confirmation">
          <p>您的学号是：{{ generatedSno }}</p>
          <button @click="confirmRegistration">确认</button>
        </div>
        <div class="warning-text">
            <p>温馨提示：</p>
            <p>1. 用户名为学号工号。若遗失密码，<a href="https://id.ouc.edu.cn/sso/login?service=https://my.ouc.edu.cn/cas/login#/">请点击查看密码重置方法</a>。</p>
            <p>2. 请使用最新版浏览器。</p>
            <p>3. 部分业务系统校外访问请先登录 <a href="https://v.ouc.edu.cn/portal/#!/login">VPN系统</a>。</p>
          </div>
  
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "UserLogin",
  data() {
    return {
      activeTab: 'account', // 当前选中的登录方式
      sno: "",
      password: "",
      phone: "", // 手机号
      code: "", // 验证码
      rememberMe: false,
      errorMessage: "",  // 错误信息
      isLoading: false,  // 登录按钮加载状态
      isCodeLoading: false, // 验证码请求加载状态
      codeTimer: 0, // 验证码倒计时

      // 注册表单相关数据
      showRegisterForm: false,  // 是否显示注册表单
      newPhone: "",  // 新用户手机号
      newCode: "",  // 注册验证码
      newPassword: "",  // 新用户密码
      newConfirmPassword: "",  // 确认密码
      registerErrorMessage: "",  // 注册错误信息

      // 学号生成后的信息
      generatedSno: "",  // 生成的学号
      showSnoConfirmation: false,  // 是否显示学号确认框
    };
  },
  methods: {
    // 处理登录
    handleLogin() {
      if (this.activeTab === 'account') {
        this.loginWithAccount();
      } else {
        this.loginWithPhone();
      }
    },

    // 账号登录逻辑
    loginWithAccount() {
      if (!this.sno || !this.password) {
        this.errorMessage = "请输入用户名和密码";
        return;
      }
      this.performLogin({
        sno: this.sno,
        password: this.password,
      });
    },

    // 手机号登录逻辑
    loginWithPhone() {
      if (!this.phone || !this.code) {
        this.errorMessage = "请输入手机号和验证码";
        return;
      }
      this.performLogin({
        phone: this.phone,
        code: this.code,
      });
    },

    // 登录 API 调用
    performLogin(loginData) {
      this.isLoading = true;
      this.errorMessage = "";

      axios.post(`http://localhost:8080/api/login`, loginData)
        .then((response) => {
          const result = response.data;

          if (result.code === 1) {
            const token = result.data;
            if (this.rememberMe) {
              localStorage.setItem('jwt_token', token);
            } else {
              sessionStorage.setItem('jwt_token', token);
            }
            this.$router.push('/MyHtmlPage');
          } else {
            this.errorMessage = result.msg || "登录失败，请重试";
          }
        })
        .catch((error) => {
          this.errorMessage = "登录请求失败，请检查网络或重试";
          console.error('Login error:', error);
        })
        .finally(() => {
          this.isLoading = false;
        });
    },

    // 显示注册表单
    toggleRegisterForm() {
      this.showRegisterForm = !this.showRegisterForm;
      this.registerErrorMessage = ""; // 重置注册错误信息
    },

    // 提交注册信息
    submitRegister() {
  // 校验输入信息是否完整
  if (!this.newPhone || !this.newCode || !this.newPassword || !this.newConfirmPassword) {
    this.registerErrorMessage = "请填写完整的注册信息";
    return;
  }

  // 校验密码与确认密码是否一致
  if (this.newPassword !== this.newConfirmPassword) {
    this.registerErrorMessage = "密码和确认密码不一致";
    return;
  }

  // 调用注册 API
  axios.post('http://localhost:8080/api/register', {
    phone: this.newPhone,
    code: this.newCode,
    password: this.newPassword
  })
    .then((response) => {
      // 后端返回学号时，响应格式为 Result.success(sno) 或 Result.error(msg)
      if (response.data.code === 1) {
        // 注册成功，获取生成的学号
        this.generatedSno = response.data.data;  // 后端返回学号（sno）
        this.showSnoConfirmation = true;         // 显示学号确认框
      } else {
        // 注册失败，显示错误信息
        this.registerErrorMessage = response.data.msg || "注册失败";
      }
    })
    .catch((error) => {
      // 网络请求失败，显示错误信息
      this.registerErrorMessage = "注册请求失败，请重试";
      console.error('Register error:', error);
    });
},


    // 确认学号，跳转到目标页面
    confirmRegistration() {
      this.showSnoConfirmation = false;
      this.$router.push('/MyHtmlPage');  // 跳转到指定路由
    },

    // 发送注册验证码
    sendRegisterCode() {
      if (!this.newPhone) {
        this.registerErrorMessage = "请输入手机号";
        return;
      }

      const phoneRegex = /^[1][3-9][0-9]{9}$/;
      if (!phoneRegex.test(this.newPhone)) {
        this.registerErrorMessage = "请输入有效的手机号";
        return;
      }

      if (this.isCodeLoading || this.codeTimer > 0) {
        return;
      }

      this.isCodeLoading = true;
      this.registerErrorMessage = "";  // 清空错误信息

      axios.post(`http://localhost:8080/api/send-register-code`, this.newPhone, {
        headers: {
          'Content-Type': 'application/json',
        }
      })
        .then((response) => {
          if (response.data.code === 1) {
            this.registerErrorMessage = "验证码发送成功，请查收短信";
            this.startCodeTimer(); // 启动倒计时
          } else {
            this.registerErrorMessage = response.data.msg || "验证码发送失败";
          }
        })
        .catch((error) => {
          this.registerErrorMessage = "验证码请求失败，请重试";
          console.error(error);
        })
        .finally(() => {
          this.isCodeLoading = false;
        });
    },

    // 启动验证码倒计时
    startCodeTimer() {
      this.codeTimer = 60; // 设置倒计时为60秒
      const timer = setInterval(() => {
        if (this.codeTimer > 0) {
          this.codeTimer--;
        } else {
          clearInterval(timer);
        }
      }, 1000);
    },
  },
};
</script>


  
  <style scoped>
  /* 保留原本的样式，不做修改 */
  
  /* 页面基础样式 */
  .login-page {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
  }
  
  /* 背景图样式 */
  .background-img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: -1;
  }
  
  /* 左上角标题样式 */
  .title {
    position: absolute;
    top: 20px;
    left: 30px;
    color: white;
    display: flex;
    align-items: center;
  }
  
  .title h1 {
    font-size: 26px;
    margin: 0;
  }
  
  .title p {
    margin: 0;
    font-size: 16px;
  }
  
  /* Logo 容器样式 */
  .logo-container {
    width: 50px;
    height: 50px;
    overflow: hidden;
  }
  
  .logo {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  /* 标语样式 */
  .slogans {
    position: absolute;
    color: #fff;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
    font-family: "KaiTi", serif;
    font-size: 48px;
    font-weight: bold;
  }
  
  .slogan-top-left {
    position: absolute;
    top: 10%;
    left: 5%;
  }
  
  .slogan-bottom-right {
    position: absolute;
    bottom: 10%;
    right: 5%;
  }
  
  /* 登录框样式 */
  .login-box {
    width: 380px;
    padding: 30px;
    background: rgba(255, 255, 255, 0.85);
    border-radius: 8px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    position: absolute;
    right: 10%;
    font-size: 16px;
    height: 580px;
  }
  
  .tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 15px;
    font-size: 18px;
    font-weight: bold;
  }
  
  .tab {
    flex: 1;
    text-align: center;
    padding-bottom: 10px;
    cursor: pointer;
  }
  
  .tab.active {
    color: #007bff;
    border-bottom: 3px solid #007bff;
  }
  
  .form .input-group {
    position: relative;
    margin-bottom: 15px;
  }
  
  .form input {
    width: calc(100% - 20px);
    padding: 15px;
    margin: 8px 0;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
  }
  
  .login-button {
    width: 100%;
    padding: 15px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 18px;
    cursor: pointer;
  }
  
  .login-button.loading {
    background-color: #999;
  }
  
  .error-message {
    color: red;
    font-size: 14px;
    margin-top: 10px;
  }
  /* 记住密码与帮助信息 */
  .remember-help {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    font-size: 14px;
  }
  
  .remember-password {
    display: inline-flex; /* 保证复选框和文字在一行 */
    align-items: center;
  }
  
  .wechat-login {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 15px 0;
  }
  
  .wechat-login img {
    width: 35px;
    height: 35px;
    margin-right: 8px;
  }
  
  .warning-text {
    font-size: 14px;
    color: #333;
    line-height: 1.6;
    margin-top: 15px;
  }
  
  .warning-text p {
    margin: 0;
  }
  
  .warning-text a {
    color: #007bff;
    text-decoration: none;
  }
  .register-form {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 360px; /* 增大注册表单宽度 */
  padding: 20px 40px; /* 增加左右内边距，右边空白会更大 */
  background-color: white;
  border-radius: 8px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.register-form input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.register-submit {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.register-close {
  width: 100%;
  padding: 10px;
  background-color: #f0f0f0;
  color: black;
  border: 1px solid #ccc;
  margin-top: 10px;
  cursor: pointer;
}

/* 学号确认框样式 */
.sno-confirmation {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 360px; /* 增大确认框的宽度 */
  padding: 20px 40px; /* 增加左右内边距 */
  background-color: white;
  border-radius: 8px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.sno-confirmation button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
  </style>
  