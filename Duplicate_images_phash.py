from PIL import Image
import six
import os
from time import time
import numpy as np
import multiprocessing as mp
from glob import glob
import csv

#Helper function to convert the binary array to Hexadecimal
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

#The main phash function which takes in a PIL Image and converts it into a hash. 
def phash(filepath, hash_size=8, highfreq_factor=4):
	#Image is opened
    image = Image.open(filepath)
	if hash_size < 0:
	    raise ValueError("Hash size must be positive")

	import scipy.fftpack
    img_size = hash_size * highfreq_factor
    #Rescaling image to smaller dimension to remove the finer details of the image
	image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
	pixels = np.array(image.getdata(), dtype=np.float).reshape((img_size, img_size))
    #Using Discete Cosine Transform to convert the images to grayscale
	dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
	dctlowfreq = dct[:hash_size, :hash_size]
    #Calculating the median 
	med = np.median(dctlowfreq)
    #Converting image to a grayscale
	diff = dctlowfreq > med
    #Convert the binary image array to corresponding hexadecimal/hash
	hash = binary_array_to_hex(diff.flatten())
	return hash

#Extract the images from the folder
folders = os.path.join('/home/admin/Documents/test/Original','train', '*')

#Extract all files from the path given.No matter what the depth of the subdirectories are.
filepaths = []
for folder in glob(folders):
	filepaths.append(glob(os.path.join(folder, '*')))

#Filepath flattened from 2D to a 1D array
filepaths = [item for sublist in filepaths for item in sublist] 
print len(filepaths)

#Note the time to calculate the time taken by the multiprocessing function to calculate the phashes of all images
start_time = time()

#Catch the number of processors in the working box
workers = mp.cpu_count()
pool = mp.Pool(workers)

#The main function that calculates the phash of all images with multiprocessing
hash_list = pool.imap(phash, filepaths)
pool.close()
pool.join()

#Create a dictionary which has all unique hash as keys and all the paths correspoding to each hash as values
hash_dict = {}
for i,j in enumerate(hash_list):
    hash_dict[j] = hash_dict.get(j, []) + [filepaths[i]]
    
end_time = time()
time_taken = time() - start_time
print time_taken

#This saves the dictionary in a csv. you can filter the results you want to save by tweaking if statement
with open('dict_csv.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in hash_dict.items():
        length = len(value)
        #Stores all duplicates into the csv file
        if length>2:
            writer.writerow([key, length, value])
        else:
            break

#Displays all the results with duplicates more than 5
for hash, path in hash_dict.items():
    if len(path)>5:
        print " "
        print len(path)
        print ", ".join(path)
        print "\n"