import torch.optim as optim
import os
import random
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as F

class FaceEmbeddingNet(nn.Module):
    def __init__(self):
        super(FaceEmbeddingNet,self).__init__()
        self.conv1=nn.Conv2d(3,32,kernel_size=5,padding=2)
        self.pool1=nn.MaxPool2d(2,2)
        self.conv2=nn.Conv2d(32,64,kernel_size=5,padding=2)
        self.pool2=nn.MaxPool2d(2,2)
        self.conv3=nn.Conv2d(64,128,kernel_size=3,padding=1)
        self.pool3=nn.MaxPool2d(2,2)
        self.fc1=nn.Linear(128*20*20,512)
        self.fc2=nn.Linear(512,128)
    def forward(self,x):
        x=self.pool1(F.relu(self.conv1(x)))
        x=self.pool2(F.relu(self.conv2(x)))
        x=self.pool3(F.relu(self.conv3(x)))
        x=x.view(x.size(0),-1) #Flatten the image
        x=F.relu(self.fc1(x))
        x=self.fc2(x)
        return F.normalize(x,p=2,dim=1)

class SiameseNetwork(nn.Module):
    def __init__(self,embedding_net):
        super(SiameseNetwork,self).__init__()
        self.embedding_net=embedding_net
    def forward(self,anchor,positive,negative):
        output_anchor=self.embedding_net(anchor)
        output_positive=self.embedding_net(positive)
        output_negative=self.embedding_net(negative)
        return output_anchor,output_positive,output_negative
    def get_embedding(self,x):
        return self.embedding_net(x)

#loss and optimizer
featureExtractor=FaceEmbeddingNet()
siamese_model=SiameseNetwork(featureExtractor)
criterion=nn.TripletMarginLoss(margin=0.2,p=2)
optimizer=optim.Adam(siamese_model.parameters(),lr=0.0005)

#Dataset construction
class LFWTripletDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        
        # Map every person to their list of images
        self.classes = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
        self.class_to_images = {}
        self.classes_with_multiple = []
        
        for cls in self.classes:
            cls_path = os.path.join(self.root_dir, cls)
            images = [os.path.join(cls_path, img) for img in os.listdir(cls_path) if img.endswith('.jpg')]
            self.class_to_images[cls] = images
            
            # We can only use people with >= 2 images for the Anchor/Positive pair
            if len(images) >= 2:
                self.classes_with_multiple.append(cls)

    def __len__(self):
        # Since we sample randomly, the length is arbitrary. 
        # We'll define an epoch as seeing a number of triplets equal to our usable classes * 10.
        return len(self.classes_with_multiple) * 10

    def __getitem__(self, idx):
        # 1. Select the Anchor class (must have at least 2 images)
        anchor_class = random.choice(self.classes_with_multiple)
        
        # 2. Select two distinct images for Anchor and Positive
        anchor_path, positive_path = random.sample(self.class_to_images[anchor_class], 2)
        
        # 3. Select a Negative class (must be a different person)
        negative_class = random.choice(self.classes)
        while negative_class == anchor_class:
            negative_class = random.choice(self.classes)
            
        negative_path = random.choice(self.class_to_images[negative_class])
        
        # 4. Load the images
        anchor_img = Image.open(anchor_path).convert('RGB')
        positive_img = Image.open(positive_path).convert('RGB')
        negative_img = Image.open(negative_path).convert('RGB')
        
        # 5. Apply PyTorch tensor transformations
        if self.transform:
            anchor_img = self.transform(anchor_img)
            positive_img = self.transform(positive_img)
            negative_img = self.transform(negative_img)
            
        return anchor_img, positive_img, negative_img

data_transforms = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.RandomHorizontalFlip(), # Light augmentation for robustness
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

lfw_dataset = LFWTripletDataset(root_dir='./lfw', transform=data_transforms)

# Initialize the DataLoader
# batch_size=32 means the model processes 32 triplets (96 images total) per step
triplet_dataloader = DataLoader(lfw_dataset, batch_size=32, shuffle=True, num_workers=4)

def training(model,dataloader,epochs=10):
    model.train()
    for epoch in range(epochs):
        total_loss=0.0
        for anchor_img,positive_img,negative_img in dataloader:
            optimizer.zero_grad()
            anchor_out,positive_out,negative_out=model(anchor_img,positive_img,negative_img)
            loss=criterion(anchor_out,positive_out,negative_out)
            loss.backward()
            optimizer.step()
            total_loss+=loss.item()

        print(f"Epoch {epoch+1}, Loss: {total_loss/len(dataloader)}")
        torch.save(model.embedding_net.state_dict(),"face_emberdder.pth")

training(siamese_model,triplet_dataloader,10)
