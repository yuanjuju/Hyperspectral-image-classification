import torch
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
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

# 加载训练好的模型
model_path = 'output/20241111-212418/model.pth'
state_dict = torch.load(model_path, map_location=device, weights_only=True)
net = HybridSN(windowSize=windowSize, K=K, rate=rate, class_num=class_num).to(device)
net.load_state_dict(state_dict)
net.eval()  # 设置模型为评估模式


# 预测函数
def predict(input_data):
    input_data = input_data.unsqueeze(0).to(device)  # 添加 batch 维度
    with torch.no_grad():
        outputs = net(input_data)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()


# 处理用户输入的 .mat 文件
def process_input_mat(input_file, label_file):
    # 加载 .mat 文件
    mat_data = sio.loadmat(input_file)

    X = mat_data['indian_pines_corrected']  # 载入数据

    # 加载标签数据
    label_data = sio.loadmat(label_file)
    y = label_data['indian_pines_gt']  # 载入标签数据

    # 数据预处理：PCA 降维
    X_pca = applyPCA(X, numComponents=pca_components)

    # 创建数据立方体
    X_pca, y = createImageCubes(X_pca, y, windowSize=windowSize)

    # 数据形状调整与转化为 Tensor
    X_pca = X_pca.reshape(-1, windowSize, windowSize, pca_components, 1)
    X_pca = X_pca.transpose(0, 4, 3, 1, 2)
    X_pca = torch.FloatTensor(X_pca)

    return X_pca, y


# 获取用户输入的 .mat 文件路径
def get_user_input_file():
    # 获取用户输入的文件路径
    mat_file_path = 'data/Indian_pines_corrected.mat'
    return mat_file_path


# 获取标签数据文件路径
def get_label_file():
    # 获取标签数据文件路径
    label_file_path = 'data/Indian_pines_gt.mat'
    return label_file_path


# 用户输入与预测
def classify_user_input():
    mat_file_path = get_user_input_file()
    label_file_path = get_label_file()
    X_pca, y = process_input_mat(mat_file_path, label_file_path)

    # 随意找一个样本进行预测
    sample_index =60
    sample = X_pca[sample_index]
    prediction = predict(sample)

    print(f'输入图像样本的预测类别为: {prediction}')

    # 生成伪彩色图像
    # 假设我们使用第一个样本的第1、2、3个PCA分量作为RGB通道
    rgb_image = np.stack((
        X_pca[sample_index][0, :, :, 0].cpu().numpy(),  # R 通道
        X_pca[sample_index][0, :, :, 1].cpu().numpy(),  # G 通道
        X_pca[sample_index][0, :, :, 2].cpu().numpy()  # B 通道
    ), axis=2)

    # 将图像像素归一化到 [0, 1] 范围，便于显示
    rgb_image -= rgb_image.min()
    rgb_image /= rgb_image.max()

    plt.imshow(rgb_image)
    plt.title(f'Predicted Class: {prediction}')
    plt.show()

# 主函数
if __name__ == '__main__':
    classify_user_input()
