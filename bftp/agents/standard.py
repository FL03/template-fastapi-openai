import torch

from torch import nn


device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
print(f"Using device: {device}")


# Define model
class NeuralNetwork(nn.Module):
    linear_relu_stack: nn.Sequential

    def __init__(self, d_input=784, d_hidden=512, d_output=10):
        super().__init__()
        # initialize a flatten layer
        self.flatten = nn.Flatten()
        # setup a sequential, linear relu stack
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(d_input, d_hidden),
            nn.ReLU(),
            nn.Linear(d_hidden, d_hidden),
            nn.ReLU(),
            nn.Linear(d_hidden, d_output),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if batch % 100 == 0:
            loss, current = loss.item(), (batch + 1) * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


def run_model(dim_in = 28):
    print("Initializing the model...")
    model = NeuralNetwork(d_input=dim_in * dim_in).to(device)
    sample_data = torch.rand(1, dim_in, dim_in, device=device)
    logits = model(sample_data)
    pred_probab = nn.Softmax(dim=1)(logits)
    y_pred = pred_probab.argmax(1)
    print(f"Predictions:\n{y_pred}")


if __name__ == "__main__":
    run_model()
