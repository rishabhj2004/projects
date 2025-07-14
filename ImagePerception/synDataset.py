import cv2
import numpy as np
import os
from random import randint, choice

# Directory structure
base_dir = "synthetic_dataset"
aligned_dir = os.path.join(base_dir, "train/aligned")
misaligned_dir = os.path.join(base_dir, "train/misaligned")

# Create directories if they don't exist
os.makedirs(aligned_dir, exist_ok=True)
os.makedirs(misaligned_dir, exist_ok=True)

# Function to create a simple aligned image with a shape
def create_aligned_image(image_id):
    img = np.ones((224, 224, 3), dtype=np.uint8) * 255  # white background
    color = (0, 0, 255)  # Red color for shapes

    # Draw a random shape: circle, rectangle, or triangle
    shape_type = choice(['circle', 'rectangle', 'triangle'])
    
    if shape_type == 'circle':
        center = (112, 112)
        radius = 50
        cv2.circle(img, center, radius, color, -1)
    elif shape_type == 'rectangle':
        top_left = (72, 72)
        bottom_right = (152, 152)
        cv2.rectangle(img, top_left, bottom_right, color, -1)
    elif shape_type == 'triangle':
        pts = np.array([[112, 50], [72, 152], [152, 152]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(img, [pts], color)

    # Save the aligned image
    aligned_path = os.path.join(aligned_dir, f"image_{image_id:03d}.jpg")
    cv2.imwrite(aligned_path, img)
    return img

# Function to create a misaligned version of an image
def create_misaligned_image(image, image_id):
    # Apply random transformations
    angle = randint(-15, 15)  # Rotation angle
    shear_factor = randint(-10, 10) / 100.0  # Shear factor
    crop_size = randint(160, 200)  # Random crop between 160x160 and 200x200

    # Rotate image
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
    rotated_img = cv2.warpAffine(image, rotation_matrix, (width, height))

    # Shear image
    shear_matrix = np.float32([[1, shear_factor, 0], [0, 1, 0]])
    sheared_img = cv2.warpAffine(rotated_img, shear_matrix, (width, height))

    # Crop image
    start_x = randint(0, width - crop_size)
    start_y = randint(0, height - crop_size)
    cropped_img = sheared_img[start_y:start_y + crop_size, start_x:start_x + crop_size]

    # Resize cropped image back to original size
    misaligned_img = cv2.resize(cropped_img, (224, 224))

    # Save the misaligned image
    misaligned_path = os.path.join(misaligned_dir, f"image_{image_id:03d}_misaligned.jpg")
    cv2.imwrite(misaligned_path, misaligned_img)

# Generate a dataset of 100 aligned and misaligned image pairs
for i in range(100):
    aligned_image = create_aligned_image(i)
    create_misaligned_image(aligned_image, i)

print("Synthetic dataset created successfully.")

