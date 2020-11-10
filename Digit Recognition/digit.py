#!/usr/bin/env python
# coding: utf-8

# <center><h1>Digit recognition</h1></center>

# our goal is to correctly identify digits from a dataset of tens of thousands of handwritten images. We’ve curated a set of tutorial-style kernels which cover everything from regression to neural networks. We encourage you to experiment with different algorithms to learn first-hand what works well and how techniques compare.

# ## kaggle Config

# In[1]:


get_ipython().system(' pip install -q kaggle')


# In[2]:


from google.colab import files 


# In[3]:


files.upload()


# In[4]:


get_ipython().system(' mkdir ~/.kaggle ')


# In[5]:


get_ipython().system(' cp kaggle.json ~/.kaggle/')


# In[6]:


get_ipython().system(' chmod 600 ~/.kaggle/kaggle.json')


# In[7]:


get_ipython().system(' kaggle datasets list')


# In[9]:


get_ipython().system('kaggle competitions download -c digit-recognizer')


# In[10]:


get_ipython().system(' mkdir train')


# In[12]:


get_ipython().system(' unzip train.csv.zip -d train')


# In[13]:


get_ipython().system('mkdir test')


# In[14]:


get_ipython().system(' unzip test.csv.zip -d test')


# ## Importing Essential Libraries

# In[17]:


# Basic Torch
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torchvision
from torch.utils.data import TensorDataset
from torch.optim import Adam, SGD

# Basic Numeric Computation
import numpy as np
import pandas as pd

# Look at data
from matplotlib import pyplot

# Easy way to split train data
from sklearn.model_selection import train_test_split

# # Looking at directory
# import os
# base_dir = "../input"
# print(os.listdir(base_dir))

device = torch.device("cpu")# if torch.cuda.is_available() else torch.device("cpu")
device
epochs=12


# In[19]:


train = pd.read_csv('/content/train/train.csv')
test = pd.read_csv('/content/test/test.csv')


# In[20]:


train.head()


# ## 2. transforming Data

# In[21]:


# Convert Dataframe into format ready for training
def createImageData(raw: pd.DataFrame):
    y = raw['label'].values
    y.resize(y.shape[0],1)
    x = raw[[i for i in raw.columns if i != 'label']].values
    x = x.reshape([-1,1, 28, 28])
    y = y.astype(int).reshape(-1)
    x = x.astype(float)
    return x, y

## Convert to One Hot Encoding
def one_hot_embedding(labels, num_classes=10):
    y = torch.eye(num_classes) 
    return y[labels] 


# In[22]:


x_train, y_train = createImageData(train)
#x_train, x_val, y_train, y_val = train_test_split(x,y, test_size=0.02)

#x_train.shape, y_train.shape, x_val.shape, y_val.shape
x_train.shape, y_train.shape


# In[23]:


# Normalization
mean = x_train.mean()
std = x_train.std()
x_train = (x_train-mean)/std
#x_val = (x_val-mean)/std

# Numpy to Torch Tensor
x_train = torch.from_numpy(np.float32(x_train)).to(device)
y_train = torch.from_numpy(y_train.astype(np.long)).to(device)
y_train = one_hot_embedding(y_train)
#x_val = torch.from_numpy(np.float32(x_val))
#y_val = torch.from_numpy(y_val.astype(np.long))


# # 3. Loading Dataset

# In[24]:


# Convert into Torch Dataset
train_ds = TensorDataset(x_train, y_train)
#val_ds = TensorDataset(x_val,y_val)


# In[25]:


# Make Data Loader
train_dl = DataLoader(train_ds, batch_size=64)


# ## 4. EDA

# In[26]:


index = 1
pyplot.imshow(x_train.cpu()[index].reshape((28, 28)), cmap="gray")
print(y_train[index])


# ## 5. Model

# In[27]:


# Helper Functions

## Initialize weight with xavier_uniform
def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.xavier_uniform(m.weight)
        m.bias.data.fill_(0.01)

## Flatten Later
class Flatten(nn.Module):
    def forward(self, input):
        return input.view(input.size(0), -1)

# Train the network and print accuracy and loss overtime
def fit(train_dl, model, loss, optim, epochs=10):
    model = model.to(device)
    print('Epoch\tAccuracy\tLoss')
    accuracy_overtime = []
    loss_overtime = []
    for epoch in range(epochs):
        avg_loss = 0
        correct = 0
        total=0
        for x, y in train_dl: # Iterate over Data Loder
    
            # Forward pass
            yhat = model(x) 
            l = loss(y, yhat)
            
            #Metrics
            avg_loss+=l.item()
            
            # Backward pass
            optim.zero_grad()
            l.backward()
            optim.step()
            
            # Metrics
            _, original =  torch.max(y, 1)
            _, predicted = torch.max(yhat.data, 1)
            total += y.size(0)
            correct = correct + (original == predicted).sum().item()
            
        accuracy_overtime.append(correct/total)
        loss_overtime.append(avg_loss/len(train_dl))
        print(epoch,accuracy_overtime[-1], loss_overtime[-1], sep='\t')
    return accuracy_overtime, loss_overtime

# Plot Accuracy and Loss of Model
def plot_accuracy_loss(accuracy, loss):
    f = pyplot.figure(figsize=(15,5))
    ax1 = f.add_subplot(121)
    ax2 = f.add_subplot(122)
    ax1.title.set_text("Accuracy over epochs")
    ax2.title.set_text("Loss over epochs")
    ax1.plot(accuracy)
    ax2.plot(loss, 'r:')

# Take an array and show what model predicts 
def predict_for_index(array, model, index):
    testing = array[index].view(1,28,28)
    pyplot.imshow(x_train[index].reshape((28, 28)), cmap="gray")
    print(x_train[index].shape)
    a = model(testing.float())
    print('Prediction',torch.argmax(a,1))


# In[28]:


# Define the model

ff_model = nn.Sequential(
    Flatten(),
    nn.Linear(28*28, 100),
    nn.ReLU(),
    nn.Linear(100, 10),
    nn.Softmax(1),
).to(device)


# In[29]:


# Initialize model with xavier initialization which is recommended for ReLu
ff_model.apply(init_weights)


# In[30]:


optim = Adam(ff_model.parameters())
loss = nn.MSELoss()
output = fit(train_dl, ff_model, loss, optim, epochs)
plot_accuracy_loss(*output)


# In[31]:


index = 4
predict_for_index(x_train, ff_model, index)


# In[32]:


# A too simple NN taken from pytorch.org/tutorials
class Mnist_CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(16, 16, kernel_size=3, stride=2, padding=1)
        self.conv3 = nn.Conv2d(16, 10, kernel_size=3, stride=2, padding=1)

    def forward(self, xb):
        xb = xb.view(-1, 1, 28, 28)
        xb = F.relu(self.conv1(xb))
        xb = F.relu(self.conv2(xb))
        xb = F.relu(self.conv3(xb))
        xb = F.avg_pool2d(xb, 4)
        return xb.view(-1, xb.size(1))

class LeNet5(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, stride=1)
        self.average1 = nn.AvgPool2d(2, stride=2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5, stride=1)
        self.average2 = nn.AvgPool2d(2, stride=2)
        self.conv3 = nn.Conv2d(16, 120, kernel_size=4, stride=1)
        
        self.flatten = Flatten()
        
        self.fc1 = nn.Linear(120, 82)
        self.fc2 = nn.Linear(82,10)

    def forward(self, xb):
        xb = xb.view(-1, 1, 28, 28)
        xb = F.tanh(self.conv1(xb))
        xb = self.average1(xb)
        xb = F.tanh(self.conv2(xb))
        xb = self.average2(xb)
        xb = F.tanh(self.conv3(xb))
        xb = xb.view(-1, xb.shape[1])
        xb = F.relu(self.fc1(xb))
        xb = F.relu(self.fc2(xb))
        return xb


# In[33]:


conv_model = LeNet5()
conv_model.apply(init_weights)
loss = nn.MSELoss()
optim = SGD(conv_model.parameters(), lr=0.1, momentum=0.9)
plot_accuracy_loss(*fit(train_dl, conv_model,loss,optim,epochs))


# ## Working on test data

# ### Normalization

# In[34]:


x_test = test.values
x_test = x_test.reshape([-1, 28, 28]).astype(float)
x_test = (x_test-mean)/std
x_test = torch.from_numpy(np.float32(x_test))
x_test.shape


# #### Prediction

# In[35]:


index = 7
predict_for_index(x_test, ff_model, index)
predict_for_index(x_test, conv_model, index)


# In[36]:


# Export data to CSV in format of submission
def export_csv(model_name, predictions, commit_no):
    df = pd.DataFrame(prediction.tolist(), columns=['Label'])
    df['ImageId'] = df.index + 1
    file_name = f'submission_{model_name}_v{commit_no}.csv'
    print('Saving ',file_name)
    df[['ImageId','Label']].to_csv(file_name, index = False)


# In[37]:


test.head()


# In[38]:


# just to make output easier to read
commit_no = 17


# In[39]:


ff_test_yhat = ff_model(x_test.float())
prediction = torch.argmax(ff_test_yhat,1)
print('Prediction',prediction)
export_csv('ff_model',prediction, commit_no=commit_no)


# In[40]:


cn_train_yhat = conv_model(x_test)
prediction = torch.argmax(cn_train_yhat,1)
yo = torch.argmax(y_train,1)
export_csv('lenet_model',prediction, commit_no=commit_no)


# ### Ensembling

# In[41]:


models = []
optims = []
loss = nn.MSELoss()
ensembles = 15
import sys
for i in range(ensembles):
    sys.stdout.write(f'Ensemble No {i+1}\n')
    model = LeNet5()
    model.apply(init_weights)
    #optim = Adam(model.parameters())
    optim = SGD(model.parameters(), lr=0.1, momentum=0.9)

    accuracy, _ = fit(train_dl, model,loss,optim,epochs)
    if accuracy[-1] > 95:
        models.append(model)
        optims.append(optim)


# In[43]:


ensemble = cn_train_yhat

for model in models:
    ensemble+=model(x_test)

ensemble_one_hot = torch.argmax(ensemble,1) # Find argmax
export_csv(f'ensemble_{ensembles}_LeNets',ensemble_one_hot, commit_no=commit_no)


# In[44]:


ensemble_one_hot


# In[46]:


ensemble = ff_test_yhat + cn_train_yhat # Add probabilities of individual predictions
ensemble_one_hot = torch.argmax(y_train,1) # Find argmax
export_csv('ensemble',ensemble_one_hot, commit_no=commit_no)


# <h4> Final Accuracy Achieved 98.94%</h4>

# Thanks
