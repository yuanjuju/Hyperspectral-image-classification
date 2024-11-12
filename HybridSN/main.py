import os
import torch
import time
import scipy.io as sio
from torch import nn, optim
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from src.model import HybridSN
from src.data_processing import applyPCA, createImageCubes, splitTrainTestSet

# 超参数设置
class_num = 16
windowSize = 25
K = 30
rate = 16
test_ratio = 0.90
pca_components = 30

# 数据加载
X = sio.loadmat('data/Indian_pines_corrected.mat')['indian_pines_corrected']
y = sio.loadmat('data/Indian_pines_gt.mat')['indian_pines_gt']

# 数据预处理:pca降维
X_pca = applyPCA(X, numComponents=pca_components)


 # 创建数据立方体
X_pca, y = createImageCubes(X_pca, y, windowSize=windowSize)
# print('数据立方体 X 的形状: ', X_pca.shape)
# print('数据立方体 y 的形状: ', y.shape)

# 划分训练集和测试集
Xtrain, Xtest, ytrain, ytest = splitTrainTestSet(X_pca, y, test_ratio)
# print('训练集 X 的形状: ', Xtrain.shape)
# print('测试集 X 的形状: ', Xtest.shape)

# 数据形状调整
Xtrain = Xtrain.reshape(-1, windowSize, windowSize, pca_components, 1)
Xtest = Xtest.reshape(-1, windowSize, windowSize, pca_components, 1)

# 转置数据以适应 PyTorch 格式
Xtrain = Xtrain.transpose(0, 4, 3, 1, 2)
Xtest = Xtest.transpose(0, 4, 3, 1, 2)


# 创建数据集类
class TrainDS(torch.utils.data.Dataset):
    def __init__(self):
        self.len = Xtrain.shape[0]
        self.x_data = torch.FloatTensor(Xtrain)
        self.y_data = torch.LongTensor(ytrain)

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len


class TestDS(torch.utils.data.Dataset):
    def __init__(self):
        self.len = Xtest.shape[0]
        self.x_data = torch.FloatTensor(Xtest)
        self.y_data = torch.LongTensor(ytest)

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len


# 创建输出文件夹
def create_output_dir():
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 使用时间戳创建唯一的子文件夹
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    current_output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(current_output_dir)

    return current_output_dir


# 准确率计算函数
def accuracy(predictions, labels):
    _, predicted = torch.max(predictions, 1)
    correct = (predicted == labels).sum().item()
    total = labels.size(0)
    acc = 100 * correct / total
    return acc


# 训练和评估函数
def train_model():
    trainset = TrainDS()
    testset = TestDS()
    train_loader = DataLoader(dataset=trainset, batch_size=128, shuffle=True, num_workers=2)
    test_loader = DataLoader(dataset=testset, batch_size=128, shuffle=False, num_workers=2)

    # 使用 GPU 训练
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = HybridSN(windowSize=windowSize, K=K, rate=rate, class_num=class_num).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(net.parameters(), lr=0.00037)

    # 创建输出目录
    current_output_dir = create_output_dir()
    train_losses = []
    test_accuracies = []


    net.train()
    total_loss = 0

    for epoch in range(40):
        epoch_loss = 0
        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = net(inputs)

            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        train_losses.append(epoch_loss / len(train_loader))

        # 每个 epoch 结束后计算训练集和测试集准确率
        net.eval()
        with torch.no_grad():
            train_acc = 0
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = net(inputs)
                train_acc += accuracy(outputs, labels)
            train_acc /= len(train_loader)

            test_acc = 0
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = net(inputs)
                test_acc += accuracy(outputs, labels)
            test_acc /= len(test_loader)

        test_accuracies.append(test_acc)

        print(f'[Epoch: {epoch + 1}] [Train Loss: {epoch_loss / len(train_loader):.4f}] '
              f'[Train Accuracy: {train_acc:.2f}%] [Test Accuracy: {test_acc:.2f}%]')

    print('训练完成')

    # 保存模型
    model_path = os.path.join(current_output_dir, 'model.pth')
    torch.save(net.state_dict(), model_path)
    print(f'模型已保存到 {model_path}')

    # 绘制损失和准确率曲线
    plot_metrics(train_losses, test_accuracies, current_output_dir)


# 绘制损失和准确率曲线
def plot_metrics(train_losses, test_accuracies, output_dir):
    epochs = range(1, len(train_losses) + 1)

    plt.figure()
    plt.plot(epochs, train_losses, label='Train Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Train Loss Curve')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'train_loss.png'))
    plt.close()

    plt.figure()
    plt.plot(epochs, test_accuracies, label='Test Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.title('Test Accuracy Curve')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'test_accuracy.png'))
    plt.close()



if __name__ == '__main__':
    train_model()


# import torch
# print("CUDA是否可用:", torch.cuda.is_available())
# print("GPU数量:", torch.cuda.device_count())
# print("GPU名称:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "无")
# print(hel)
