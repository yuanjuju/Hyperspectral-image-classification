import io
import torch
import numpy as np
import scipy.io as sio
import json
from flask import Flask, request, jsonify, Response
from src.model import HybridSN
from src.data_processing import applyPCA, createImageCubes
from flask_cors import CORS

# 设置超参数
class_num = 16
windowSize = 25
K = 30
rate = 16
pca_components = 30

device = torch.device("cpu")

def load_labels():
    label_data = sio.loadmat('data/Indian_pines_gt.mat')
    return label_data['indian_pines_gt']

# 中文标签映射
label_mapping = {
    1: '大豆',
    2: '玉米',
    3: '小麦',
    4: '大麦',
    5: '水稻',
    6: '甘蔗',
    7: '棉花',
    8: '柑橘',
    9: '葡萄',
    10: '草坪',
    11: '树林',
    12: '建筑物',
    13: '道路',
    14: '水域',
    15: '裸露土壤',
    16: '其他'
}

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 加载训练好的模型
model_path = 'output/20241109-111322/model.pth'
state_dict = torch.load(model_path, map_location=device, weights_only=True)
net = HybridSN(windowSize=windowSize, K=K, rate=rate, class_num=class_num).to(device)
net.load_state_dict(state_dict)
net.eval()

# 预测函数
def predict(input_data):
    input_data = input_data.unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = net(input_data)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

@app.route('/api/upload', methods=['POST'])
def predict_api():
    try:
        print("Received request")
        if 'file' not in request.files:
            print("No file part in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            print("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        # 输出文件名和文件内容的大小
        print(f"File received: {file.filename}, size: {len(file.read())} bytes")

        # 将上传的文件内容读取为字节流，并加载为 MATLAB 文件
        file.seek(0)  # 重新将文件指针移回开始
        file_content = io.BytesIO(file.read())  # 将文件内容转换为字节流
        data = sio.loadmat(file_content)  # 解析为 .mat 数据结构
        X = data.get('indian_pines_corrected')  # 根据实际数据键名修改
        if X is None:
            return jsonify({'error': 'Invalid file format, "indian_pines_corrected" not found'}), 400

        # 加载固定标签
        y = load_labels()

        # 数据预处理：PCA 降维
        X_pca = applyPCA(X, numComponents=pca_components)

        # 创建数据立方体
        X_pca, y = createImageCubes(X_pca, y, windowSize=windowSize)

        # 数据形状调整
        X_pca = X_pca.reshape(-1, windowSize, windowSize, pca_components, 1)
        X_pca = X_pca.transpose(0, 4, 3, 1, 2)
        X_pca = torch.FloatTensor(X_pca)

        # 进行预测
        predictions = []
        for sample_index in range(X_pca.shape[0]):
            sample = X_pca[sample_index]
            prediction = predict(sample)
            # 将预测结果的数字标签转换为中文名称，并格式化为 "数据x：大豆"
            predictions.append(f"数据{sample_index + 1}：{label_mapping.get(prediction + 1, '未知')}")  # +1 因为标签是从 1 开始

        # 使用json.dumps自定义JSON序列化，避免Unicode转义
        response_data = json.dumps({'predictions': predictions}, ensure_ascii=False)

        # 返回包含预测结果的 JSON 数据，并确保编码为 UTF-8
        response = Response(response_data, mimetype='application/json; charset=utf-8')
        return response

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制为 10MB
