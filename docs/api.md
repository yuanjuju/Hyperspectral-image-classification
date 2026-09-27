# 推理接口与数据契约

[返回首页](../README.md) · [运行手册](operations.md)

服务启动时加载一次有效模型工件。默认监听 `127.0.0.1:5000`。

## GET /health

工件成功加载后返回 200：

```json
{"status":"ready","architecture":"HybridSN-channel-attention","schema_version":1}
```

此接口表示进程已初始化，不执行预测，也不表示当前没有正在处理的请求。

## POST /api/upload

请求：`multipart/form-data`，文件字段名 `file`。默认 MAT key 为 `indian_pines_corrected`，可通过 `--data-key` 修改。

输入数组必须为非空 `H×W×B` 实数有限值立方体；`B` 必须与训练工件的 bands 一致。默认上限为请求体 10 MiB、250,000 像素。上传不需要地面真值。MAT v7.3/HDF5、GeoTIFF 和 ENVI 当前不支持。

```bash
curl --fail-with-body \
  -F 'file=@HybridSN卷积模型（flask）/data/Indian_pines_corrected.mat' \
  http://127.0.0.1:5000/api/upload > predictions.json
```

下面仅演示字段含义，不是实测预测结果：

```json
{
  "predictions": ["class_1", "class_3", "class_2", "class_1"],
  "class_ids": [1, 3, 2, 1],
  "shape": [2, 2],
  "label_offset": 1,
  "order": "row-major",
  "model": "HybridSN-channel-attention"
}
```

- `class_ids` 和 `predictions` 均含 `H×W` 项，按先行后列展开，可将前者 reshape 为 `shape`。
- 类别范围 `1..classes`；训练背景标签 0 不作为输出类别。全图推理会对所有像素给出类别，背景掩膜需由下游单独应用。
- `predictions` 保留字符串数组以兼容 Java 的字段检查，但内容使用明确的 `class_n`。地物名称需要与训练标签定义配套映射，避免复用错位的旧类别表。
- 响应不包含概率、置信度或不确定性估计。

## 错误语义

| HTTP | 触发条件 | 响应 |
| --- | --- | --- |
| 400 | 缺少文件、MAT 无法读取、缺 key、形状/波段/数值不合法、像素超限 | `{"error":"具体原因"}` |
| 413 | multipart 请求体超过配置上限 | `{"error":"Upload exceeds configured size limit"}` |
| 503 | 同一进程已有正在执行的推理 | `{"error":"Inference is busy; retry after the current request"}` |

失败路径也会释放推理锁。工件损坏或配置不兼容发生在应用初始化阶段，不是正常 HTTP 错误响应。10 MiB 是完整请求体上限，包含 multipart 开销；MAT 解压后的大小可能远大于上传体积，像素校验发生在 MAT 解析之后。

## Java / Vue 衔接

现有 Java 地址为 `POST http://localhost:8080/api/uploadfile`，转发到 `http://localhost:5000/api/upload`，并以 `predictions.json` 附件返回。Java 当前将下游异常统一转为 500，因此 Python 的 400/413/503 不会完整透传。测试和诊断时可直接访问 Python 接口。

Vue 的文件选择器还允许 `.tif`，但 Python 没有 TIFF 解码器；当前请选择 `.mat`。旧页面的进度百分比来自前端定时器，不能视为模型推理进度。接口示例不意味着已完成 Java/Vue 的端到端验证。
