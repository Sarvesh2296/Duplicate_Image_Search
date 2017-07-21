
from PIL import Image
import six
import os
from time import time
import numpy as np
import multiprocessing as mp
import csv
from glob import glob
import redis
from os import listdir
from os.path import join, isfile

#Make a redis instance on the default host 
r = redis.Redis(host='localhost', port=6379, db=0)

#The directory from where to take the images
imgdir = "/mnt/data/customer_content/Electronics"
hash_temp = []
hash_list = []
hash_dict = {}
start_time = time()

#Helper function to convert binary image array to hexadecimal 
def binary_array_to_hex(arr):
   
    h = 0
    s = []
    for i, v in enumerate(arr.flatten()):
        if v: 
            h += 2**(i % 8)
        if (i % 8) == 7:
            s.append(hex(h)[2:].rjust(2, '0'))
            h = 0
    return "".join(s)

#Main function to calculate the hashes
def phash(filepath, hash_size=8, highfreq_factor=4):
    try:
        os.stat(filepath)
    except OSError, e:
        if e.errno == errno.ENOENT:
            print "path %s is a broken symlink"%filepath
        else:
            raise e
    #Open the image
    image = Image.open(filepath)
    if hash_size < 0:
        raise ValueError("Hash size must be positive")
    import scipy.fftpack
    img_size = hash_size * highfreq_factor
    #Resize the image to a smaller dimension to remove the finer details
    image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
    pixels = np.array(image.getdata(), dtype=np.float).reshape((img_size, img_size))
    #Function to calculate the Discrete Cosine Transform
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    #Convert the binary image array to hexadecimal/hash
    hash = binary_array_to_hex(diff.flatten())
    #Push the hash to the redis database
    if r.exists(hash):
        r.append(hash, " ," + filepath)
    else:
        r.append(hash, filepath)
    return hash

#Count the number of processors in the working box 
workers = mp.cpu_count()
pool = mp.Pool(workers)

#Create the filepaths list 
filepaths = []
for path, subdirs, files in os.walk(imgdir):
    for name in files:
        name = os.path.join(path, name)
        filepaths.append(name)

#Main multiprocessing function to calculate the phash of all the images and store it in hash_list
hash_list = pool.imap(phash, filepaths)
    
pool.close()
pool.join()

#Print the total time taken to calculate all the hashes
end_time = time()
time_taken = time() - start_time
print time_taken

