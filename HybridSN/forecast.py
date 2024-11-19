import torch
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from src.model import HybridSN
from src.data_processing import applyPCA, createImageCubes

# 设置超参数
class_num = 16  # 分类数，根据数据集修改
windowSize = 25  # 滑动窗口大小
pca_components = 30  # PCA降维后的波段数
rate = 16  # 通道增长率
device = torch.device("cpu")  # 使用CPU或GPU

class_mapping = {
    0: "Undefined",         # 无效区域
    1: "Alfalfa",           # 苜蓿
    2: "Corn-notill",       # 玉米-免耕
    3: "Corn-mintill",      # 玉米-少耕
    4: "Corn",              # 玉米
    5: "Grass-pasture",     # 草地-牧场
    6: "Grass-trees",       # 草地-林地
    7: "Grass-pasture-mowed", # 草地-修剪牧场
    8: "Hay-windrowed",     # 干草-风枕
    9: "Oats",              # 燕麦
    10: "Soybean-notill",   # 大豆-免耕
    11: "Soybean-mintill",  # 大豆-少耕
    12: "Soybean-clean",    # 大豆-精耕
    13: "Wheat",            # 小麦
    14: "Woods",            # 森林
    15: "Buildings-Grass-Trees-Drives", # 建筑-草地-树木-车道
    16: "Stone-Steel-Towers" # 石材-钢塔
}



# 加载训练好的模型
model_path = 'output/20241111-212418/model.pth'
state_dict = torch.load(model_path, map_location=device)
net = HybridSN(windowSize=windowSize, K=pca_components, rate=rate, class_num=class_num).to(device)
net.load_state_dict(state_dict)
net.eval()  # 设置模型为评估模式

# 预测函数
def predict(input_data):
    """
    对单个样本进行预测
    """
    input_data = input_data.unsqueeze(0).to(device)  # 添加 batch 维度
    with torch.no_grad():
        outputs = net(input_data)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

# 数据处理函数
def process_input_mat(input_file, label_file=None):
    """
    加载并处理输入的 .mat 文件，支持动态调整窗口和标签。
    """
    mat_data = sio.loadmat(input_file)
    X = mat_data[list(mat_data.keys())[-1]]  # 动态提取数据部分

    # 数据预处理：PCA 降维
    X_pca = applyPCA(X, numComponents=pca_components)

    if label_file:
        label_data = sio.loadmat(label_file)
        y = label_data[list(label_data.keys())[-1]]  # 动态提取标签部分

        # 创建数据立方体
        X_pca, y = createImageCubes(X_pca, y, windowSize=windowSize)
    else:
        y = None

    # 数据形状调整与转化为 Tensor
    X_pca = X_pca.reshape(-1, windowSize, windowSize, pca_components, 1)
    X_pca = X_pca.transpose(0, 4, 3, 1, 2)
    X_pca = torch.FloatTensor(X_pca)

    return X_pca, y

# 用户输入与预测
def classify_user_input():
    """
    对用户输入的图像文件进行分类，并生成伪彩色图像和原始图像。
    """
    # 加载数据文件路径
    mat_file_path = 'data/Indian_pines_corrected.mat'
    label_file_path = 'data/Indian_pines_gt.mat'
    X_pca, y = process_input_mat(mat_file_path, label_file_path)

    # 随机选择一个样本进行预测
    sample_index = 14
    sample = X_pca[sample_index]
    prediction = predict(sample)


    if y is not None:
        actual_class = y[sample_index].item()
        actual_class_name = class_mapping.get(actual_class, "未知类别")
    else:
        actual_class_name = "标签数据不可用"

    # 映射预测类别到类别名称
    predicted_class_name = class_mapping.get(prediction, "未知类别")

    print(f'输入图像样本的预测类别为: {predicted_class_name}')
    print(f'输入图像样本的实际类别为: {actual_class_name}')
    # 原始图像显示
    raw_mat_data = sio.loadmat(mat_file_path)
    original_data = raw_mat_data[list(raw_mat_data.keys())[-1]]  # 提取原始数据
    original_sample = original_data[:, :, :3].astype(np.float32)  # 转换为浮点类型
    original_sample -= original_sample.min()
    original_sample /= original_sample.max()

    plt.figure(figsize=(10, 5))

    # 原始图像
    plt.subplot(1, 2, 1)
    plt.imshow(original_sample)
    plt.title(f'Original Image (Index: {sample_index})')
    plt.axis('off')

    # 伪彩色图像显示
    rgb_image = np.stack((
        X_pca[sample_index][0, :, :, 0].cpu().numpy(),  # R 通道
        X_pca[sample_index][0, :, :, 1].cpu().numpy(),  # G 通道
        X_pca[sample_index][0, :, :, 2].cpu().numpy()  # B 通道
    ), axis=2)

    rgb_image -= rgb_image.min()
    rgb_image /= rgb_image.max()

    plt.subplot(1, 2, 2)
    plt.imshow(rgb_image)
    plt.title(f'Processed Image\nPredicted: {predicted_class_name} | Actual: {actual_class_name}')
    plt.axis('off')

    plt.tight_layout()
    plt.show()


# 主函数
if __name__ == '__main__':
    classify_user_input()
