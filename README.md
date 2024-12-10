# 高光谱图像分类

## 介绍
本仓库为2024秋软件工程理论高光谱图像分类的项目分享仓库

## 任务主题  
使用 Flash 框架开发一个高光谱图像分类 WEB 应用。

## 作业目标  
1. 构建一个功能完善的 WEB 系统，实现以下功能：  
   - 用户上传高光谱图像。  
   - 系统调用深度学习模型，返回地物分类结果。  
   - 结果可视化并支持下载分类图像。  
2. 学习 Flash 开发流程并掌握项目部署方法。

## 使用方法
1. 再文件路径HybridSN卷积模型（flask）/output/20241111-212418内有我们训练好的模型，可以直接使用，或者也可以在HybridSN卷积模型（flask）/main.py下自由训练模型使用，所有与模型有关的内容均在HybridSN卷积模型（flask）内。
2. 前端使用vue框架，需要在/前端/vue的目录下使用npm run serve 启动，具体教程可以参考如下博客：
https://blog.csdn.net/qq_45677671/article/details/114546577?fromshare=blogdetail&sharetype=blogdetail&sharerId=114546577&sharerefer=PC&sharesource=m0_73966002&sharefrom=from_link

3. springboot的后端：springboot/demo/src/main/java/com/example/demo路径下可以直接运行DemoApplication.java启动类启动。

4. 工具教程这一栏里有较为详细的git使用教程，对此不熟悉的可以学习。

5. 项目需求这里有用户，开发工程师，客户等的需求。

6. 参考资料里有我们模型的具体解析。


## 工具与技术栈  

### 编程语言  
- **Python**：用于后端开发与深度学习模型。  
- **HTML/CSS/JavaScript**：用于前端页面设计。

### 框架与库  
- **后端**：Flash。  
- **前端**：Bootstrap 或其他前端框架。  
- **深度学习**：PyTorch。  

### 其他工具  
- **数据处理**：NumPy、Pandas。  
- **数据可视化**：Matplotlib、Seaborn。  
- **部署平台**：云服务器。

 

## 任务分配  
- **模型部分**：负责训练、优化和保存深度学习模型。  
- **后端部分**：负责 Flash 项目搭建、路由设计和 API 实现。  
- **前端部分**：设计简洁易用的上传和结果展示页面。  
- **测试与部署**：测试功能，优化性能，并将系统上线。  



