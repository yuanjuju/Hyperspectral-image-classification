<div align="right">

**中文** · [English](README_EN.md)

</div>

# 高光谱图像分类系统

**Hyperspectral Classification · Spectral–Spatial Modeling & Inference**

[![Python pipeline checks](https://github.com/yuanjuju/Hyperspectral-image-classification/actions/workflows/validate.yml/badge.svg)](https://github.com/yuanjuju/Hyperspectral-image-classification/actions/workflows/validate.yml)
![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1-ee4c2c?logo=pytorch&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-547b82)](LICENSE)

![光谱—空间模型与工件数据流示意](docs/assets/spectral-pipeline.svg)

面向高光谱遥感立方体的光谱—空间联合分类系统。以 **HybridSN 混合 3D/2D 卷积与通道重标定**为模型核心，将 PCA whitening、监督训练、模型工件和逐像素推理组织为可验证的 Python 链路，并保留 Vue / Spring Boot 的文件上传与结果下载入口。

[模型与系统架构](docs/architecture.md) · [运行与迁移](docs/operations.md) · [API 契约](docs/api.md) · [验证记录](docs/verification.md)

## 工程实现

| 维度 | 实现 |
| --- | --- |
| 光谱—空间表征 | 三层 3D 卷积编码联合特征，经谱维折叠进入 2D 空间聚合；全局池化与瓶颈门控执行通道重标定 |
| 训练与服务一致性 | PCA 仅在训练中心像素上拟合，均值、投影矩阵与 whitening 参数随权重导出；上传推理复用冻结变换 |
| 工件与实验追踪 | 版本化 manifest、SHA-256 校验、模型配置、随机种子、划分索引和逐轮训练记录；已有输出目录拒绝覆盖 |
| 推理路径 | 惰性空间 patch、可配置 mini-batch、`eval()` / `inference_mode()`；预测覆盖全部像素，不依赖地面真值文件 |
| HTTP 边界 | 上传体积、立方体形状、波段、有限值和像素上限检查；进程内单请求推理，忙碌时返回 503 |
| 回归验证 | 合成数据训练、PCA 数值对照、batch 一致性、工件完整性、Dropout 模式恢复及真实 loopback HTTP smoke |

## 模型路径

```text
H × W × B 立方体
    │ 冻结 PCA + Whitening
H × W × K 光谱投影
    │ 按需提取 S × S 邻域
3D Conv × 3 → Spectral/Feature Fold → 2D Conv
    │ Global Average Pooling → Bottleneck → Sigmoid
Channel Recalibration → MLP → 逐像素类别
```

默认 `K=30 / S=25 / C=16`。模型输出 logits；训练采用 Adam + CrossEntropyLoss，分类头含 Dropout。具体卷积核、逐层形状、内存策略和训练划分约束见[架构说明](docs/architecture.md)。

## 快速验证

从仓库根目录创建项目环境；无需下载数据集即可检查 Python 全链路：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --cache-dir .cache/pip -r requirements-dev.txt
.venv/bin/python -m pytest -q tests
.venv/bin/python tools/smoke.py --output .cache/smoke-local
```

Smoke 执行 **合成 MAT → 训练 CLI → 工件导出 → HTTP 上传 → 分类 JSON**，输出训练日志、源文件摘要和验证结果；结束后自动关闭临时服务。输出目录需为新路径。实际 Indian Pines 训练与服务启动命令见[运行手册](docs/operations.md)。

## 工程结构

```text
HybridSN卷积模型（flask）/
├── main.py                训练入口、评估记录、工件导出
├── predict.py             Flask app factory 与上传接口
├── src/model.py           3D/2D HybridSN + 通道注意力
├── src/pipeline.py        冻结预处理、PatchDataset、工件与 Predictor
├── data/                  原有 Indian Pines 数据
└── output/                原有模型与训练曲线
springboot/demo/           Java 文件转发与原有业务模块
前端/vue/                  Vue 上传与下载界面
tests/                    CPU 回归检查
tools/smoke.py            真实 HTTP 功能验证
docs/                     架构、接口、运行及验证记录
```

## 验证与迁移

当前本地验证：**23 项测试通过**，合成数据完成 2 轮 CPU 训练，健康检查与上传接口返回 200。GitHub Actions 在 Linux CPU 上重复测试和 HTTP smoke；详细证据及源文件摘要见[验证记录](docs/verification.md)。

新版服务使用 `weights.pt + preprocessor.npz + manifest.json`。历史 `model.pth` 与曲线继续保留，但缺少配套 PCA 工件，需重新导出后接入新版服务。当前结果证明功能链路可运行；本轮未报告新的数据集精度、吞吐量或 Java/Vue 全栈验证结果。

## 原有资料与方法来源

- [原始项目说明](docs/archive/README.original.md)、[项目需求](项目需求/)、[会议记录](会议记录/)、[展示 PPT](展示ppt/)
- [模型参考资料](参考资料/)、[工具教程](工具教程/)、[博客资料](自用博客/)
- 基础方法：[HybridSN — Roy et al.](https://arxiv.org/abs/1902.06701) · [作者实现](https://github.com/gokriznastic/HybridSN)
- [MIT License](LICENSE)，保留原有版权与项目资料。
