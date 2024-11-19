import torch
import torch.nn as nn
import torch.nn.functional as F

class HybridSN(nn.Module):
    def __init__(self,windowSize,K,rate,class_num):
        super(HybridSN, self).__init__()
        self.S = windowSize
        self.L = K #光谱通道数，即高光谱图像的光谱维度
        self.rate=rate #一个缩放因子，用于控制注意力机制的通道数量。
        self.class_num = class_num
        #3D卷积层
        self.conv1 = nn.Conv3d(in_channels=1, out_channels=8, kernel_size=(7, 3, 3))
        self.conv2 = nn.Conv3d(in_channels=8, out_channels=16, kernel_size=(5, 3, 3))
        self.conv3 = nn.Conv3d(in_channels=16, out_channels=32, kernel_size=(3, 3, 3))
        #2D卷积层
        inputX = self.get2Dinput()
        inputConv4 = inputX.shape[1] * inputX.shape[2]
        self.conv4 = nn.Conv2d(inputConv4, 64, kernel_size=(3, 3))
        #注意力机制
        self.sa1 = nn.Conv2d(64, 64 // rate, kernel_size=1)
        self.sa2 = nn.Conv2d(64 // rate, 64, kernel_size=1)
        #全连接层
        self.dense1 = nn.Linear(18496, 256)
        self.dense2 = nn.Linear(256, 128)
        self.dense3 = nn.Linear(128, class_num)

        self.drop = nn.Dropout(p=0.43)
        self.soft = nn.Softmax(dim=1)

    def get2Dinput(self):
        with torch.no_grad():
            x = torch.zeros((1, 1, self.L, self.S, self.S))
            x = self.conv1(x)
            x = self.conv2(x)
            x = self.conv3(x)
        return x

    def forward(self, x):
        out = F.relu(self.conv1(x))
        out = F.relu(self.conv2(out))
        out = F.relu(self.conv3(out))

        out = out.view(-1, out.shape[1] * out.shape[2], out.shape[3], out.shape[4])
        out = F.relu(self.conv4(out))

        weight = F.avg_pool2d(out, out.size(2))
        weight = F.relu(self.sa1(weight))
        weight = F.sigmoid(self.sa2(weight))
        out = out * weight

        out = out.view(out.size(0), -1)
        out = F.relu(self.dense1(out))
        out = self.drop(out)
        out = F.relu(self.dense2(out))
        out = self.drop(out)
        out = self.dense3(out)

        return out




