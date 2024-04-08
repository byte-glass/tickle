# m.py

import torch
from torch import nn
import torch.utils.data as tud

import c as t

## dataset

class D(tud.Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __len__(self):
        return len(self.y)
    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

## model

class M(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(5, 8),
            nn.ReLU(),
            nn.Linear(8, 8),
            nn.ReLU(),
            nn.Linear(8, 3),
        )
    def forward(self, x):
        return self.linear_relu_stack(x)

## device

device = "cpu"

## train and test

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    model.train()
    for batch, (x, y) in enumerate(dataloader):
        x, y = x.to(device), y.to(device)
        # Compute prediction error
        pred = model(x)
        loss = loss_fn(pred, y)
        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        this_loss, current = loss.item(), (batch + 1) * len(x)
        print(f"this_loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for x, y in dataloader:
            x, y = x.to(device), y.to(device)
            pred = model(x)
            test_loss += loss_fn(pred, y).item()
    test_loss /= num_batches
    print(f"Avg loss: {test_loss:>8f}")

##

### this is where the model meets pytorch, lots of `t. ..` -- hmmm??
def soft_sample(model, mu):
    def choice(h):
        z = [(i, a) for (i, a) in enumerate(t.Action) if a in t.actions(h)]
        r = torch.exp(mu * model(torch.tensor(t.rho(h))))[[i for (i, _) in z]]
        return [a for (_, a) in z][torch.multinomial(r / sum(r), 1)]
    return choice

def sigma(mu, x):
    r = torch.exp(mu * x)
    return r / sum(r)


## dataloader

def make_dataloader(model, mu, size, batch):
    model.eval()
    s = {'player1': soft_sample(model, mu), 'player2': soft_sample(model, mu)}
    x, y = t.batch(s, size)
    x = torch.tensor(x)
    y = torch.tensor(y)
    data = D(x, y)
    return tud.DataLoader(data, batch_size = batch, shuffle = True)

## model, loss and optimizer

model = M().to(device)
loss_fn = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-2, weight_decay=0.05)

mu = 0.0
train_data = make_dataloader(model, mu, 64, 16)
test_data = make_dataloader(model, mu, 16, 16)

train(train_data, model, loss_fn, optimizer)
test(test_data, model, loss_fn)

for _ in range(5): 
    for _ in range(1): train(dataloader, model, loss_fn, optimizer)
    test(dataloader, model, loss_fn)



#     ## "test" soft_sample
# 
#     mu = 0.0001
#     s = {'player1': soft_sample(model, mu), 'player2': soft_sample(model, mu)}
#     t.batch(s, 4)
# 
#     soft_sample(model, mu)(t.deal())
# 
#     soft_sample(model, mu)(t.act_bet(t.deal()))
# 
# 
#     model.eval()
# 
#     model(x[1])


### end
