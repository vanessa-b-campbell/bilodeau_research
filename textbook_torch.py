import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

import matplotlib.pyplot as plt

# using Pytorch to train a deep learning multi-class classifier on the dataset MNIST and
#  test how the trained model performs on the test sample

# define the model architecture (convolutional layers, dropout layers, and linear/fully connected layers)

class ConvNet(nn.Module):
    def __init__(self):  
        #_init_ function defines the core architecture of the model
        # which actually means this function defines all the layers 
        # and the number of neurons in each layer
        # takes in input self
        super(ConvNet, self).__init__()
        #       the convolutional layers

        self.cn1 = nn.Conv2d(1, 16, 3, 1)
        # 1-channel input:  (the grayscale images that will be fed to the model)

        # 16 channel output: (usually higher or equal to the num of input- each channel is a 
        #                       feature map that detects 16 different kinds of information from the 
        #                       input image) each feature map has a dedicated kernel extracting
        #                       features for them

        # kernel size 3: (3x3 usually odd num so input images are symmetrically distributed around cental pixel)
        #                   kernel is the section the nn is looking at. 1 central pixel and then viewing it's 
        #                   neighboring pixels

        # stride size 1:  (a small stride will keep the kernel from skipping many pixels in the image)
        #                   stride size is directly proportional to the kernel size 
        #                   (kernel size: 100 = stride size: 10)

        self.cn2 = nn.Conv2d(16, 32, 3, 1)
        # convolutional layer 2 also has a 3x3 kernel size 
        # more layers with smaller kernels is better than 1 layer with larger kernels
        # 32 channel outputs:  to extract more kinds of feature from the image
        #                      this second CNN is deepening the number of kinds of features- 
        #                      the second layer going deeper is common practice

        #       the dropout layers
        self.dp1 = nn.Dropout2d(0.10)
        self.dp2 = nn.Dropout2d(0.25)
        #       the fully connected layers
        self.fc1 = nn.Linear(4608, 64) # 4608 is basically 12 X 12 X 32
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        # forward function does a forward pass in the network
        # therfore has all the activation functions (x?) at each layer 
        # and any pooling or dropout used after any layer
        #   returns: op ---the final layer output (the prediction model)
        x = self.cn1(x)
        x = F.relu(x)
        x = self.cn2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dp1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dp2(x)
        x = self.fc2(x)
        op = F.log_softmax(x, dim=1)
        # output (op) will have the same dimensions as the target output (the ground truth?)
        return op



def train(model, device, train_dataloader, optim, epoch):
    # function train will 
    # 1. iterate through the dataset in batches
    # 2. make a copy of the dataset on the given device
    # 3. make forward pass with the retrieved data on the neural network model
    # 4. compute the loss between the model prediction and the ground truth
    # 5. use the given optimizer to tune model weights, 
    # 6. print the training logs every 10 bathches
    # one run thorugh (when entire dataset has been read once) is equal to 1 epoch 
    model.train()
    for b_i, (X, y) in enumerate(train_dataloader):
        X, y = X.to(device), y.to(device)
        optim.zero_grad()
        pred_prob = model(X)
        loss = F.nll_loss(pred_prob, y) # nll is the negative likelihood loss
        loss.backward()
        optim.step()
        if b_i % 10 == 0:
            print('epoch: {} [{}/{} ({:.0f}%)]\t training loss: {:.6f}'.format(
                epoch, b_i * len(X), len(train_dataloader.dataset),
                100. * b_i / len(train_dataloader), loss.item()))

def test(model, device, test_dataloader):
    # test function evaluates the model performance on the test set
    model.eval()
    loss = 0
    success = 0
    with torch.no_grad():
        for X, y in test_dataloader:
            X, y = X.to(device), y.to(device)
            pred_prob = model(X)
            loss += F.nll_loss(pred_prob, y, reduction='sum').item() # loss summed across the batch
            # in the test function the loss is used to compute the overall test error across the entire test batch
            pred = pred_prob.argmax(dim=1, keepdim=True)  # us argmax to get the most likely prediction
            success += pred.eq(y.view_as(pred)).sum().item()

    loss /= len(test_dataloader.dataset)

    print('\nTest dataset: Overall Loss: {:.4f}, Overall Accuracy: {}/{} ({:.0f}%)\n'.format(
        loss, success, len(test_dataloader.dataset),
        100. * success / len(test_dataloader.dataset)))
    

# the mean and standard deviation values are calculated as the mean of all the pixel 
# values of all images in the training data set
train_dataloader = torch.utils.data.DataLoader(
    datasets.MNIST('../data', train=True, download=True,
                    transform=transforms.Compose([
                        transforms.ToTensor(),
                        transforms.Normalize((0.1302,), (0.3069,))])), # train_X.mean()/256. and train_X.std()/256.
    batch_size=32, shuffle=True)
# batch size is 32 (a common choice)
# small batch means a slow training because it's calculating the gradient over and over
# large batches means slow training because the time to calculate the gradient is long
# better to make frequent and less precise gradients 

# shuffle = True : randomly shuffle training data intances to ensure a uniform distribution with a specified mean and standard deviation

# normalize the dataset to a normal distribution with a specified mean ans standard deviation

test_dataloader = torch.utils.data.DataLoader(
    datasets.MNIST('../data', train=False, 
                    transform=transforms.Compose([
                        transforms.ToTensor(),
                        transforms.Normalize((0.1302,), (0.3069,)) 
                    ])),
    batch_size=500, shuffle=False)


torch.manual_seed(0)
    # 'set a seed' to avoid randomness and enure repeatablity 
device = torch.device("cpu")
    # device is the cpu 



model = ConvNet()
optimizer = optim.Adadelta(model.parameters(), lr=0.5)
# Adadelta needs the decaying rate as a parameter


# AdaDelta as the optimiser for this exercise with a learning rate of 0.5
# ^ is a good choice for sparse data, because not all pixels in the image are informative 
# another optimization choice is Adam 

for epoch in range(1, 3):
    train(model, device, train_dataloader, optimizer, epoch)
    test(model, device, test_dataloader)
# should be output here


# everything above is training the model, with a reasonable test set performance, now 
# manually chack whether the model inference on a sample image is correct
test_samples = enumerate(test_dataloader)
b_i, (sample_data, sample_targets) = next(test_samples)

plt.imshow(sample_data[0][0], cmap='gray', interpolation= 'none')
plt.show()

# # should be output here


print(f"Model prediction is : {model(sample_data).data.max(1)[1][0]}")
print(f"Ground truth is : {sample_targets[0]}")

