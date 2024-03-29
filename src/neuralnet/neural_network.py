import torch
import torch.nn as nn
import torch.nn.functional as F

class NeuralNetwork(nn.Module):
    def __init__(
        self,
        hidden_dimension=256,
        input_dimension=3,
        res_blocks=5,
        game_size=9,
        legal_moves=9,
    ):
        super().__init__()
        self.hidden_dimension = hidden_dimension
        self.input_dimension = input_dimension
        self.res_blocks = res_blocks

        self.initial = nn.Sequential(
            nn.Conv2d(
                self.input_dimension,
                self.hidden_dimension,
                kernel_size=3,
                stride=1,
                padding=1,
            ),  # Convolution matrix
            nn.BatchNorm2d(self.hidden_dimension),  # Batch normalization
            nn.ReLU(),  # Activation function
        )

        # [1, 9, 2, 3..]
        self.block = nn.Sequential(
            nn.Conv2d(
                self.hidden_dimension,
                self.hidden_dimension,
                kernel_size=3,
                stride=1,
                padding=1,
            ),  # Convolution matrix
            nn.BatchNorm2d(self.hidden_dimension),  # Batch normalization
            nn.ReLU(),  # Activation function
            nn.Conv2d(
                self.hidden_dimension,
                self.hidden_dimension,
                kernel_size=3,
                stride=1,
                padding=1,
            ),  # Convolution matrix
            nn.BatchNorm2d(self.hidden_dimension),  # Batch normalization
        )

        self.policy = nn.Sequential(
            nn.Conv2d(self.hidden_dimension, 2, kernel_size=1, stride=1),
            nn.BatchNorm2d(2),
            nn.ReLU(),  # shape (1, 2, 3, 3)
            nn.Flatten(),  # shape (1)
            nn.Linear(2 * game_size, legal_moves),
        )

        self.value = nn.Sequential(
            nn.Conv2d(self.hidden_dimension, 1, kernel_size=1, stride=1),
            nn.BatchNorm2d(1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(1 * game_size, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Tanh(),
        )

    def forward(self, x) -> tuple[torch.Tensor, torch.Tensor]:
        x = self.initial(x)
        for _ in range(self.res_blocks):
            x = self.block(x) + x
            x = F.relu(x)
        policy = self.policy(x)
        value = self.value(x)
        return policy, value
    
    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)
    
