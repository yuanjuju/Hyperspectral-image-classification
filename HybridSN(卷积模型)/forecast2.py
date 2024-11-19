import torch
import scipy.io as sio
from src.model import HybridSN
from src.data_processing import applyPCA, createImageCubes

# 设置超参数
class_num = 16
windowSize = 25
K = 30
rate = 16
pca_components = 30

# 强制使用 CPU 设备
device = torch.device("cpu")

# 加载数据
X = sio.loadmat('data/Indian_pines_corrected.mat')['indian_pines_corrected']
y = sio.loadmat('data/Indian_pines_gt.mat')['indian_pines_gt']


# 数据预处理：PCA 降维
X_pca = applyPCA(X, numComponents=pca_components)

# 创建数据立方体
X_pca, y = createImageCubes(X_pca, y, windowSize=windowSize)

# 数据形状调整
X_pca = X_pca.reshape(-1, windowSize, windowSize, pca_components, 1)
X_pca = X_pca.transpose(0, 4, 3, 1, 2)
X_pca = torch.FloatTensor(X_pca)

# 加载训练好的模型
# 加载训练好的模型权重
model_path = 'output/20241111-212418/model.pth'  # 请修改为实际的模型路径
state_dict = torch.load(model_path, map_location=device, weights_only=True)
net = HybridSN(windowSize=windowSize, K=K, rate=rate, class_num=class_num).to(device)
net.load_state_dict(state_dict)


# 设置模型为评估模式
net.eval()

# 预测函数
def predict(input_data):
    input_data = input_data.unsqueeze(0).to(device)  # 添加 batch 维度
    with torch.no_grad():
        outputs = net(input_data)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

# 对测试集样本预测
sample_index = 100  # 测试集中一个样本索引
sample = X_pca[sample_index]
prediction = predict(sample)

print(sample)
print(f'样本索引 {sample_index} 的预测类别为: {prediction}')
