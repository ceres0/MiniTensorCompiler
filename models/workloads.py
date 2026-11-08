"""Small static-shape FP32 models used to exercise the ONNX importer."""

import torch
from torch import nn


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.w1 = nn.Parameter(torch.randn(128, 256) * 0.05)
        self.b1 = nn.Parameter(torch.randn(256) * 0.05)
        self.w2 = nn.Parameter(torch.randn(256, 64) * 0.05)
        self.b2 = nn.Parameter(torch.randn(64) * 0.05)

    def forward(self, x):
        return torch.relu(x @ self.w1 + self.b1) @ self.w2 + self.b2


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.weight = nn.Parameter(torch.randn(8 * 16 * 16, 64) * 0.05)
        self.bias = nn.Parameter(torch.randn(64) * 0.05)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv(x)))
        return torch.flatten(x, 1) @ self.weight + self.bias


class QKV(nn.Module):
    def __init__(self):
        super().__init__()
        self.wq = nn.Parameter(torch.randn(256, 256) * 0.05)
        self.wk = nn.Parameter(torch.randn(256, 256) * 0.05)
        self.wv = nn.Parameter(torch.randn(256, 256) * 0.05)

    def forward(self, x):
        return x @ self.wq, x @ self.wk, x @ self.wv
