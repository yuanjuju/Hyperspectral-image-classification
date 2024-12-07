import io
import torch
import numpy as np
import scipy.io as sio
from flask import Flask, request, jsonify
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

@app.route('/api/111', methods=['GET'])
def tx():
    print("csacsa")
    return("cfasfasfa")

@app.route('/api/upload', methods=['POST'])
def predict_api():
    print("casca");
    try:

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 将上传的文件内容读取为字节流，并加载为 MATLAB 文件
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


        predictions = []
        for sample_index in range(X_pca.shape[0]):
            sample = X_pca[sample_index]
            prediction = predict(sample)
            predictions.append(prediction)

        return jsonify({'predictions': predictions})

    except Exception as e:
        return jsonify({'error': str(e)}), 400



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

