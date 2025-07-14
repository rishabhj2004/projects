import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Configurations
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
DATA_DIR = "synthetic_dataset"

# 1. Data Loading and Preprocessing Functions
def load_images(misaligned_dir, aligned_dir, size=IMAGE_SIZE):
    images = []
    labels = []
    
    aligned_files = {file.replace("_misaligned", ""): file for file in os.listdir(aligned_dir)}
    misaligned_files = os.listdir(misaligned_dir)
    
    for misaligned_filename in misaligned_files:
        aligned_filename = aligned_files.get(misaligned_filename.replace("_misaligned", ""))
        
        if aligned_filename:
            aligned_img_path = os.path.join(aligned_dir, aligned_filename)
            misaligned_img_path = os.path.join(misaligned_dir, misaligned_filename)

            aligned_img = cv2.imread(aligned_img_path)
            misaligned_img = cv2.imread(misaligned_img_path)

            if aligned_img is None or misaligned_img is None:
                print(f"Error loading image pair: {misaligned_filename}, {aligned_filename}")
                continue

            aligned_img = cv2.resize(aligned_img, size)
            misaligned_img = cv2.resize(misaligned_img, size)

            aligned_img = preprocess_image(aligned_img)
            misaligned_img = preprocess_image(misaligned_img)

            x_offset, y_offset = compute_offsets(aligned_img, misaligned_img)

            images.append(misaligned_img)
            labels.append([x_offset, y_offset])
        
    images_array = np.array(images) / 255.0
    labels_array = np.array(labels)

    print(f"Loaded {len(images_array)} images with shape {images_array.shape}")
    print(f"Loaded {len(labels_array)} labels with shape {labels_array.shape}")
    
    return images_array, labels_array

def preprocess_image(image):
    return cv2.resize(image, IMAGE_SIZE)

def compute_offsets(aligned_img, misaligned_img):
    aligned_gray = cv2.cvtColor(aligned_img, cv2.COLOR_BGR2GRAY)
    misaligned_gray = cv2.cvtColor(misaligned_img, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(misaligned_gray, aligned_gray, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    x_offset, y_offset = max_loc
    return x_offset, y_offset

# 2. Model Definition
def build_model(input_shape=(*IMAGE_SIZE, 3)):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    base_model.trainable = False
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(1024, activation='relu'),
        layers.Dense(2, activation='linear')
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model

# 3. Image Alignment Function with Debugging
def align_image(image, model):
    if image is None:
        print("Error: The input image could not be loaded.")
        return None
    
    img = cv2.resize(image, IMAGE_SIZE)
    img = preprocess_image(img)
    img = np.expand_dims(img, axis=0)
    offsets = model.predict(img)
    x_offset, y_offset = offsets[0]
    
    rows, cols = image.shape[:2]
    translation_matrix = np.float32([[1, 0, x_offset], [0, 1, y_offset]])
    
    aligned_image = cv2.warpAffine(image, translation_matrix, (cols, rows))
    
    assert isinstance(aligned_image, np.ndarray), "aligned_image is not a valid numpy array."
    assert aligned_image.shape == image.shape, "aligned_image shape mismatch with input image shape."
    
    return aligned_image

# 4. Performance Evaluation Metrics
def evaluate_model(model, test_images, test_labels):
    predictions = model.predict(test_images)
    mse = mean_squared_error(test_labels, predictions)
    mae = mean_absolute_error(test_labels, predictions)
    print(f"Mean Squared Error: {mse}")
    print(f"Mean Absolute Error: {mae}")
    return mse, mae

# Main Program
if __name__ == "__main__":
    # Load and preprocess data
    train_images, train_labels = load_images(
        os.path.join(DATA_DIR, 'train/misaligned'),
        os.path.join(DATA_DIR, 'train/aligned')
    )
    
    test_images, test_labels = load_images(
        os.path.join(DATA_DIR, 'test/misaligned'),
        os.path.join(DATA_DIR, 'test/aligned')
    )

    # Build the model
    model = build_model()

    # Define a checkpoint callback to save the best model weights
    checkpoint_callback = ModelCheckpoint('model_weights.keras', 
                                          save_best_only=True,
                                          monitor='val_loss',
                                          mode='min',
                                          verbose=1)

    # Train the model
    model.fit(train_images, train_labels, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_data=(test_images, test_labels), callbacks=[checkpoint_callback])
    
    # Evaluate model on test data
    evaluate_model(model, test_images, test_labels)
    
    # Example of aligning a new image
    sample_image_path = os.path.join(DATA_DIR, "test/misaligned/image_026_misaligned.jpg")
    sample_image = cv2.imread(sample_image_path)

    if sample_image is None:
        print(f"Error: Could not load sample image at path: {sample_image_path}")
    else:
        aligned_image = align_image(sample_image, model)
        if aligned_image is not None:
            cv2.imshow("Original Image", sample_image)
            cv2.imshow("Aligned Image", aligned_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

