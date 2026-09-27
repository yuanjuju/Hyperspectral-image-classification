# 验证记录

[返回首页](../README.md) · [机器可读记录与源文件摘要](verification.json)

记录日期：2026-09-27。验证针对本次 Python 路径重构，不为历史曲线补填实验条件。

## 本地验证

| 检查 | 观察结果 |
| --- | --- |
| 环境 | macOS 26.5 arm64，Python 3.12.14，PyTorch 2.5.1，NumPy 2.1.3 |
| 依赖一致性 | `pip check` 通过 |
| CPU 回归 | 23 passed，0 failures，0 errors，0 skipped |
| 训练 CLI | `8×8×16` 合成立方体，3 类任意标签，2 epoch，48 个训练中心 / 16 个测试中心 |
| 工件 | 导出 manifest、state_dict、冻结 PCA、划分索引后成功重新加载 |
| 健康接口 | 实际 loopback HTTP `GET /health` → 200 / ready |
| 上传接口 | 实际 multipart MAT 上传 → 200，64 个类别，返回形状 `[8,8]` |
| 回收 | smoke 脚本关闭临时 HTTP 服务；环境和缓存均在项目目录 |

本地测试出现 3 条来自 scikit-learn 参考 PCA 变换矩阵乘法的 NumPy RuntimeWarning（divide by zero / overflow / invalid value）。本次有限值结果的数值对照断言通过；根因未确定，未屏蔽这些警告。该现象与测试失败分别记录，不能据此宣称所有数值后端都已验证。

## 覆盖的契约

- 训练两个 epoch 时，评估后恢复 Dropout 的训练状态。
- 固定 PCA 对未见输入的投影与 sklearn 参考变换数值一致，保存/加载后结果一致。
- 单 patch 与不同 batch 大小推理返回同样的类别和空间顺序。
- 损坏权重摘要、不支持的架构、非法模型配置会被拒绝。
- 原有工件目录不可覆盖。
- 非法形状、空数组、非有限值、复数立方体及复数标签被拒绝。
- 默认网络仍保留历史分类头尺寸 `18496`。
- 上传成功、缺字段、缺 key、错误 MAT、波段不匹配和上传超限。
- 像素上限在 patch 构造前生效。
- 并发上传返回 503，完成或出错后锁释放，后续有效请求仍可执行。

## 如何重跑

```bash
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q tests --junitxml=.cache/test-results.xml
.venv/bin/python tools/smoke.py --output .cache/smoke-recheck
```

Smoke 使用新输出目录，`result.json` 记录运行环境和相关源码 SHA-256。`docs/verification.json` 是本次本地运行的快照；修改源码后应重新运行，不能沿用旧摘要证明新代码。

GitHub Actions 配置位于 [validate.yml](../.github/workflows/validate.yml)，在 Ubuntu / Python 3.12 / CPU torch 下执行 pytest 与真实 HTTP smoke。JUnit 和 smoke 结果作为 CI artifact 保存；最新远程状态见 [Actions](https://github.com/yuanjuju/Hyperspectral-image-classification/actions/workflows/validate.yml)。

## 尚未覆盖

- 没有为本轮重新完成 Indian Pines 全量训练或报告新的 OA / AA / Kappa。
- 没有 GPU 训练、CUDA/MPS 推理、吞吐、尾延迟、内存峰值或多进程压测结果。
- 没有完成 Java/Vue 的构建和完整浏览器端到端测试。现有页面缺少 `aaa.png` 源资源，Java 环境也未在本轮配置。
- 没有生产部署、外部身份认证、存储服务、任务队列或模型注册中心验证。

合成样本的训练精度只检验代码能否运行，不作为遥感模型质量指标。
