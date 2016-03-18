"""Preprocessing script.
This script walks over the directories and dump the frames into a csv file
"""
import os
import csv
import sys
import random
import scipy
import numpy as np
import skimage.io
from skimage import io, transform
import mxnet as mx
import argparse
import json
csize = 64

parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--output')
args = parser.parse_args()

INPUT_PATH = args.input
OUTPUT_PATH = args.output


def mkdir(fname):
   try:
       os.mkdir(fname)
   except:
       pass

def get_images_format(root_path):
   """Get path to all the frame in view SAX and contain complete frames"""
   ret = []
   for root, _, files in os.walk(root_path):
       root=root.replace('\\','/')
       files=[s for s in files if ".jpg" in s]
       if len(files) == 0:
           continue
       prefix = files[0].rsplit('-', 1)[0]
       fileset = set(files)
       expected = []
       for i in range(len(fileset)+10):
          expected.append("p%02d.jpg"%(i))
       for i in range(len(fileset)+10):
          expected.append("n%02d.jpg"%(i))
       for x in expected:
           if x in fileset:
              ret.append(root + "/" + x)
   # sort for reproduciblity
   return ret

def get_images(root_path):
   """Get path to all the frame in view SAX and contain complete frames"""
   ret = []
   for root, _, files in os.walk(root_path):
       root=root.replace('\\','/')
       files=[s for s in files if "Crop" in s and str(csize)+"x"+str(csize) not in s]
       
       if len(files) == 0:
           continue
       fileset = set(files)
       for x in fileset:
              ret.append(root + "/" + x)
 # sort for reproduciblity
   return ret

def get_label_map(fname):
   labelmap = {}
   fi = open(fname)
   fi.readline()
   for line in fi:

       arr = line.split(',')
       labelmap[(arr[0])] = line
   return labelmap


def write_label_csv(fname, frames, label_map):
   fo = open(fname, "w")
   for lst in frames:
       index = (lst.split("/")[2])
       if label_map != None:
           fo.write(label_map[index])
       else:
           fo.write("%d,0,0\n" % index)
   fo.close()


def get_data(lst,preproc):
   data = []
   result = []
   for path in lst:

       f = skimage.io.imread(path)
       img = preproc(f.astype(float) / np.max(f))
       dst_path = path.rsplit(".", 1)[0] + "."+str(csize)+"x"+str(csize)+".jpg"
       scipy.misc.imsave(dst_path, img)
       result.append(dst_path)
       data.append(img)


   data = np.array(data, dtype=np.uint8)
   col_num = data.size/len(data)
   data = data.reshape(len(data), col_num)
   data = np.array(data,dtype=np.str_)
   data = data.reshape(len(data), col_num)
   return [data,result]


def write_data_csv(fname, frames, preproc):
   """Write data to csv file"""
   fdata = open(fname, "w")
   #dr = Parallel()(delayed(get_data)(lst,preproc) for lst in frames)
   dr = get_data(frames,preproc)

   data = dr[0]
   result = dr[1]
   #data,result = zip(*dr)
   for entry in data:
      fdata.write(','.join(entry)+'\r\n')
   print("All finished, %d slices in total" % len(data))
   fdata.close()
   result = np.ravel(result)
   return result


def crop_resize(img, size):
   """crop center and resize"""
   if img.shape[0] < img.shape[1]:
       img = img.T
   # we crop image from center
   short_egde = min(img.shape[:2])
   yy = int((img.shape[0] - short_egde) / 2)
   xx = int((img.shape[1] - short_egde) / 2)
   crop_img = img[yy : yy + short_egde, xx : xx + short_egde]
   # resize to 64, 64
   resized_img = transform.resize(crop_img, (size, size))
   resized_img *= 255
   return resized_img.astype("uint8")


def local_split(train_index):
   random.seed(0)
   train_index = set(train_index)
   all_index = sorted(train_index)
   num_test = int(len(all_index) / 3)
   random.shuffle(all_index)
   train_set = set(all_index[num_test:])
   test_set = set(all_index[:num_test])
   return train_set, test_set


def split_csv(src_csv, split_to_train, train_csv, test_csv):
   ftrain = open(train_csv, "w")
   ftest = open(test_csv, "w")
   cnt = 0
   for l in open(src_csv):
       if split_to_train[cnt]:
           ftrain.write(l)
       else:
           ftest.write(l)
       cnt = cnt + 1
   ftrain.close()
   ftest.close()

# Load the list of all the training frames, and shuffle them
# Shuffle the training frames
random.seed(10)

FILE_PATH = '/' + '/'.join(INPUT_PATH.split('/')[:-1])
FILE_PATH = '/' + INPUT_PATH
print(FILE_PATH)
train_frames = get_images(FILE_PATH)

print(train_frames)


# Dump the data of each frame into a CSV file, apply crop to 64 preprocessor
train_lst = write_data_csv(FILE_PATH + "/test-"+str(csize)+"x"+str(csize)+"-data.csv", train_frames, lambda x: crop_resize(x, csize))


bs = len(train_frames) # SET HERE

data_val = mx.io.CSVIter(data_csv= FILE_PATH + "/test-"+str(csize)+"x"+str(csize)+"-data.csv", data_shape=(3, csize, csize),batch_size = bs)

prefix = '/local_work/IVFProject/hidos/icsi/bin/Mymodel_March'
iteration = 100


Pmodel = mx.model.FeedForward.load(prefix, iteration, ctx=mx.gpu(0))
Ein_prob = Pmodel.predict(data_val)


result = dict()
for i in range(0,len(train_frames)):
   result[train_frames[i].split('/')[-1]] = str(Ein_prob[i,0])

with open(FILE_PATH + "/" + 'predict_result.json', 'w') as f:
   json.dump(result,f)

print(result)



