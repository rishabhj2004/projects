import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import time

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

# 2. Load Model
print("Loading model...")
model = FaceEmbeddingNet()
model.load_state_dict(torch.load("face_embedder.pth", map_location='cpu'))
model.eval()

transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# 3. Setup OpenCV Face Detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

# State variables for multi-shot capture
capturing = False
captured_count = 0
max_captures = 10
embeddings_list = []
last_capture_time = 0

print("Press 's' to start 3-second scan, or 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret: break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Display instructions on screen
    if capturing:
        cv2.putText(frame, f"Scanning: {captured_count}/{max_captures}. Move head slightly!", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
    else:
        cv2.putText(frame, "Press 's' to start Face Scan", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    for (x, y, w, h) in faces:
        # Draw bounding box
        color = (0, 165, 255) if capturing else (255, 0, 0)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # If we are in capture mode, time to take a snapshot
        if capturing and captured_count < max_captures:
            current_time = time.time()
            
            # Wait 0.3 seconds between captures to ensure varied angles
            if current_time - last_capture_time > 0.3:
                face_crop = frame[y:y+h, x:x+w]
                
                # --- APPLY HISTOGRAM EQUALIZATION TO THE Y (LUMINANCE) CHANNEL ---
                img_yuv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2YUV)
                img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
                face_rgb = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
                
                # (Optional Debug: Show what the neural network sees)
                # cv2.imshow("Neural Network View", cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR))
                
                pil_img = Image.fromarray(face_rgb)
                img_tensor = transform(pil_img).unsqueeze(0)
                
                with torch.no_grad():
                    embedding = model(img_tensor).numpy()
                    
                embeddings_list.append(embedding)
                captured_count += 1
                last_capture_time = current_time

    cv2.imshow('Registration', frame)
    
    # Check if we have collected all 10 embeddings
    if captured_count == max_captures:
        average_embedding = np.mean(embeddings_list, axis=0)
        np.save('my_embedding.npy', average_embedding)
        print("\nSuccess! Multi-shot embedding saved to my_embedding.npy.")
        break
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s') and not capturing:
        if len(faces) > 0:
            print("Starting scan... gently move your head around!")
            capturing = True
            last_capture_time = time.time()
        else:
            print("No face detected! Look at the camera.")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
