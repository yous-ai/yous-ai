"""
Deep Q-Network (DQN) architecture for Atari Pong
Uses Convolutional Neural Network (Nature CNN) for visual input
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class DQN(nn.Module):
    def __init__(self, input_shape, action_dim):
        """
        Initialize the CNN-based DQN.
        
        Args:
            input_shape: Shape of input observation (C, H, W) e.g., (4, 84, 84)
            action_dim: Number of actions
        """
        super(DQN, self).__init__()
        
        channels, height, width = input_shape
        
        # Nature CNN Architecture
        # Conv 1: 32 filters, 8x8 kernel, stride 4
        self.conv1 = nn.Conv2d(channels, 32, kernel_size=8, stride=4)
        
        # Conv 2: 64 filters, 4x4 kernel, stride 2
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        
        # Conv 3: 64 filters, 3x3 kernel, stride 1
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1)
        
        # Calculate output size of convolutions
        def conv2d_size_out(size, kernel_size, stride):
            return (size - (kernel_size - 1) - 1) // stride + 1
        
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(width, 8, 4), 4, 2), 3, 1)
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(height, 8, 4), 4, 2), 3, 1)
        linear_input_size = convw * convh * 64
        
        # Fully Connected Layers
        self.fc1 = nn.Linear(linear_input_size, 512)
        self.head = nn.Linear(512, action_dim)
        
    def forward(self, x):
        """
        Forward pass of the network.
        
        Args:
            x: Input tensor (batch, C, H, W)
        """
        # Normalization usually handled by environment (if uint8) 
        # but good practice to ensure float
        if x.dtype == torch.uint8:
            x = x.float() / 255.0
            
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        
        # Flatten
        x = x.reshape(x.size(0), -1)
        
        x = F.relu(self.fc1(x))
        return self.head(x)
