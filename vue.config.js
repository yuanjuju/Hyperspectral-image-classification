const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: 'http://localhost:8080', 
    allowedHosts: 'all',  // 将所有 /api/ 的请求代理到后端 API
    // 如果你有多个后端API接口，可以像这样进行更多的配置：
    // proxy: {
    //   '/api': {
    //     target: 'http://localhost:5000',
    //     changeOrigin: true,
    //     secure: false
    //   },
    // }
  }
})
