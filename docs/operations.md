# 运行与工件迁移

[返回首页](../README.md) · [架构](architecture.md) · [API](api.md) · [验证记录](verification.md)

以下命令从仓库根目录运行。Python 环境、pip 缓存和模型输出均放在项目目录，不修改全局 Python。

## 1. 项目环境

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --cache-dir .cache/pip -r requirements-dev.txt
```

仅运行训练/服务时可安装 `requirements.txt`。主版本锁定在 Python 3.12 / PyTorch 2.5.1 的已验证组合。Linux CPU CI 先从 PyTorch CPU wheel 索引安装 torch，再安装其余依赖。GPU wheel、CUDA/MPS 训练和其他 Python 版本不在本轮验证范围内。

## 2. 无数据集功能检查

```bash
.venv/bin/python -m pytest -q tests
.venv/bin/python tools/smoke.py --output .cache/smoke-local
```

`smoke.py` 生成 `8×8×16` 合成立方体和任意标签，通过训练 CLI 执行 2 个 epoch，导出工件；随后启动临时 loopback HTTP 服务，检查 `/health` 和 multipart 上传，最后关闭服务。输出目录包含 `training.log`、`result.json`、`predictions.json` 和模型工件。输出路径必须不存在，重复执行时请换一个目录名。

这里的标签和精度只用于检验流程，不能当作 Indian Pines 实验结果。

## 3. 训练实际数据

仓库原有数据位于 `HybridSN卷积模型（flask）/data/`。稀疏检出时需先取回该目录；完整 clone 则直接使用。可从[原始数据发布页](https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes#Indian_Pines)核对数据说明。

```bash
.venv/bin/python 'HybridSN卷积模型（flask）/main.py' \
  --cube 'HybridSN卷积模型（flask）/data/Indian_pines_corrected.mat' \
  --labels 'HybridSN卷积模型（flask）/data/Indian_pines_gt.mat' \
  --output artifacts/indian-pines-run-01 \
  --components 30 --window 25 --classes 16 \
  --epochs 40 --batch-size 128 --test-ratio 0.9 \
  --learning-rate 0.00037 --seed 345 --device cpu
```

`--test-ratio 0.9` 沿用原来的 10% 训练 / 90% 测试中心比例，可显式调整。小样本类别需满足分层划分要求，训练中心数不得少于 PCA 分量数。输入 key 默认为 `indian_pines_corrected` / `indian_pines_gt`，可用 `--data-key` / `--label-key` 改写。

每轮输出一行 JSON，包含损失、监测准确率和样本数。工件目录不得已存在，避免覆盖实验记录。这里提供的是实际数据运行命令，本轮没有重新跑完正式数据集训练或报告新精度。

## 4. 启动 Python 服务

```bash
.venv/bin/python 'HybridSN卷积模型（flask）/predict.py' \
  --artifact artifacts/indian-pines-run-01 \
  --host 127.0.0.1 --port 5000 \
  --batch-size 128 --max-upload-mb 10 --max-pixels 250000
```

模型目录必须来自上一阶段，或使用 smoke 输出下的 `model/`。smoke 工件只接受 16 波段合成数据，不适用于 200 波段实际场景。

这是 Flask 开发服务器，默认只绑定本机；不包含生产网关、身份认证、TLS 或部署编排。推理固定在 CPU，训练设备单独配置。请求格式及错误见 [API 文档](api.md)。服务启动完成后：

```bash
curl --fail http://127.0.0.1:5000/health
curl --fail-with-body \
  -F 'file=@HybridSN卷积模型（flask）/data/Indian_pines_corrected.mat' \
  http://127.0.0.1:5000/api/upload > predictions.json
```

## 历史模型与兼容性

原有 `output/20241109-111322/` 和 `output/20241111-212418/` 模型、损失曲线与准确率曲线均保留。原 README 另存为 [历史说明](archive/README.original.md)。

旧流程在运行时重新拟合 PCA，未将预处理参数与权重一起导出，因此仅有 `model.pth` 无法证明训练与服务使用了相同投影。新版 `predict.py` 需要显式 `--artifact`，不会静默选取旧权重。建议通过新版训练入口重新导出配套工件；不应将旧权重与新拟合 PCA 随意组合。

旧 `forecast.py`、`forecast2.py`、`src/data_processing.py` 和 `download.py` 仍作为历史实验代码保留，尚未迁移到新工件契约。旧环境导出保存为 `requirements.legacy.txt`，只用于追溯，不与新版环境混装；其中可能包含平台限定包。

## 原有完整 Web 工程

- 前端：`前端/vue/`，Vue 2 / Vue CLI，入口 `npm run serve`。
- Java：`springboot/demo/`，Spring Boot 3.3.5，POM 指定 Java 17。
- 转发路径和服务端口见 [API 文档](api.md#java--vue-衔接)。Java multipart 上限仍为 10 MB，增大 Python 上限时也需检查 Java 配置。

这部分保留原实现与配置，本轮没有重新配置数据库、Redis、短信或问答账户，也没有验证完整 Java/Vue 构建。当前检出的 Vue 组件引用了不存在于 Git 树中的 `src/assets/aaa.png`；完整 Web 启动前需补齐该资源或修正引用。Python 独立训练/推理验证不受此问题影响。
