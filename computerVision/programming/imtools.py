import os
import numpy as np
from PIL import Image

def get_imlist(path):
    ''' Returns a list of filenames for
        all jpg images in a directory. '''
    return [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.jpeg')]
    
def resize(imgarray,size):
    img=Image.fromarray(imgarray)
    return np.array(img.resize(size))
    
def histeq(im,nbr_bins=256):
    imhist,bins=np.histogram(im.flatten(),nbr_bins,density=True)
    cdf = imhist.cumsum()
    cdf = 255 * cdf / cdf[-1] 
    im2 = np.interp(im.flatten(),bins[:-1],cdf) #interpolation
    return im2.reshape(im.shape), cdf    
    

