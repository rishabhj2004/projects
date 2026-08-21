import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os

# 1. Define Architecture
class FaceEmbeddingNet(nn.Module):
    def __init__(self):
        super(FaceEmbeddingNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=5, padding=2)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=5, padding=2)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool3 = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 20 * 20, 512)
        self.fc2 = nn.Linear(512, 128)
        
    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = self.pool3(F.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.normalize(x, p=2, dim=1)

if not os.path.exists('my_embedding.npy'):
    print("Error: Run register_webcam.py first to save your face!")
    exit()

# 2. Load Model and Saved Embedding
model = FaceEmbeddingNet()
model.load_state_dict(torch.load("face_embedder.pth", map_location='cpu'))
model.eval()

transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

saved_embedding = np.load('my_embedding.npy')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

# THRESHOLD - Adjust this based on how strict you want it to be (lower is stricter)
THRESHOLD = 0.85

print("Starting live Face ID check... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret: break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        face_crop = frame[y:y+h, x:x+w]
        
        # --- APPLY HISTOGRAM EQUALIZATION TO THE Y (LUMINANCE) CHANNEL ---
        img_yuv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        face_rgb = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        
        pil_img = Image.fromarray(face_rgb)
        img_tensor = transform(pil_img).unsqueeze(0)
        
        with torch.no_grad():
            live_embedding = model(img_tensor).numpy()
            
        distance = np.linalg.norm(saved_embedding - live_embedding)
        
        if distance < THRESHOLD:
            color = (0, 255, 0) # Green for match
            label = f"Match! ({distance:.2f})"
        else:
            color = (0, 0, 255) # Red for unknown
            label = f"Unknown ({distance:.2f})"
            
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
    cv2.imshow('Face ID Login Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
