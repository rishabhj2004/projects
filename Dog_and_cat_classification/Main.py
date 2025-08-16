import pandas as pd
import numpy as np
import matplotlib .pyplot as plt
import warnings
import os
import random
from keras.preprocessing.image import load_img

warnings.filterwarnings('ignore')

input_path=[]
label=[]
for Class in os.listdir("PetImages"):
    for path in os.listdir("PetImages/"+Class):
        if Class=='Cat':
            label.append(0)
        else:
            label.append(1)
        input_path.append(os.path.join("PetImages/",Class,path))
print(input_path[9302],label[9302])

df=pd.DataFrame()
df['images']=input_path
df['label']=label
df['label']=df['label'].astype('str')
df = df.sample(frac=1, random_state=42).reset_index(drop=True) #shuffle the data
df.head()

plt.figure(figsize=(25,25))
dog=df[df['label']=='1']['images']
cat=df[df['label']=='0']['images']
start=random.randint(0,len(dog)-25)
files=dog[start:start+25]
for index,file in enumerate(files):
    plt.subplot(5,5,index+1)
    img=load_img(file)
    img=np.array(img)
    plt.imshow(img)
    plt.title(index+1)
    plt.axis('off')
    
plt.figure(figsize=(25,25))
start=random.randint(0,len(cat)-25)
files=cat[start:start+25]
for index,file in enumerate(files):
    plt.subplot(5,5,index+1)
    img=load_img(file)
    img=np.array(img)
    plt.imshow(img)
    plt.title(index+1)
    plt.axis('off')

from sklearn.model_selection import train_test_split
train,test=train_test_split(df,test_size=0.2,random_state=42)

from tensorflow.keras.preprocessing.image import ImageDataGenerator
train_generator=ImageDataGenerator(
    rescale=1./255, #for normalizing the image
    rotation_range=40, #data augmentation
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_generator=ImageDataGenerator(rescale=1./255)

train_iterator=train_generator.flow_from_dataframe(train,x_col='images',y_col='label',target_size=(128,128),batch_size=64,class_mode='binary')

val_iterator=val_generator.flow_from_dataframe(test,x_col='images',y_col='label',target_size=(128,128),batch_size=64,class_mode='binary')

from keras import Sequential
from keras.layers import Conv2D,MaxPool2D,Flatten,Dense
model=Sequential([
    Conv2D(16,(3,3),activation='relu',input_shape=(128,128,3)),
    MaxPool2D((2,2)),
    Conv2D(32,(3,3),activation='relu'),
    MaxPool2D((2,2)),
    Conv2D(64,(3,3),activation='relu'),
    MaxPool2D((2,2)),
    Flatten(),
    Dense(512,activation='relu'),
    Dense(1,activation='sigmoid')
])

model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])
model.summary()

history=model.fit(train_iterator,epochs=50,validation_data=val_iterator)

acc=history.history['accuracy']
val_acc=history.history['val_accuracy']
epochs=range(len(acc))

plt.plot(epochs,acc,'b',label='training accuracy')
plt.plot(epochs,val_acc,'r',label='testing accuracy')
plt.title('accuracy graph')
plt.legend()
plt.figure()

loss=history.history['loss']
val_loss=history.history['val_loss']

plt.plot(epochs,loss,'b',label='training loss')
plt.plot(epochs,val_loss,'r',label='testing loss')
plt.title('loss graph')
plt.legend()
plt.figure()
plt.show()
print('final training accuracy = ',acc[len(acc)-1])
print('final validation accuracy = ',val_acc[len(val_acc)-1])
print('final training loss = ',loss[len(loss)-1])
print('final validation loss = ',val_loss[len(val_loss)-1])

#predict the image
from PIL import Image
img=Image.open("PetImages/Dog/6.jpg")
img=img.resize((128,128))
img_arr=np.array(img)
img_array = img_arr / 255.0 #normalize
img_arr = np.expand_dims(img_arr, axis=0) #expand so that it is of the same format as batch
predict=model.predict(img_arr)
plt.imshow(img)
print('prediction:')
if(predict>0.5):
    print('dog')
else:
    print('cat')
