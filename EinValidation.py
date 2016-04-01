"""Training script, this is converted from a ipython notebook
"""

import os
import csv
import sys
import numpy as np
import mxnet as mx
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# In[2]:


def CRPS(label, pred):
    """ Custom evaluation metric on CRPS.
    """
    
    #print("label:"+str(label))
    #print("pred:"+str(pred))
   
    return np.sqrt(np.sum(np.square(label - pred)) / label.size)


bs = 3 # SET HERE 

data_val = mx.io.CSVIter(data_csv="./EinVal-64x64-data.csv", data_shape=(3, 64, 64),batch_size = bs)

#print(data_val.getdata().size())  



prefix = 'Mymodel_March'
iteration = 100


Pmodel = mx.model.FeedForward.load(prefix, iteration, ctx=mx.gpu(0))
Ein_prob = Pmodel.predict(data_val)

'''
label_str = []
for line in open("./EinVal-encode-label.csv",'r'):
    line = line.strip()
    label_temp = line.split(',')[0]

    label_str.append(float(label_temp))



print(len(label_str))
print(len(Ein_prob))

file_out = open("./Ein_predict_results.csv",'w')

for i in range(0,len(Ein_prob)):
    #print>>file_out,(str(i)+','+str(label_str[i])+',%4f'%(Ein_prob[i,0]))
    print>>file_out,(str(i)+'|'+str(label_str[i])+'|%.4f,%.4f'%(Ein_prob[i,0],Ein_prob[i,1]))

#Ein_prob = model_loaded.predict(data_val)

'''
