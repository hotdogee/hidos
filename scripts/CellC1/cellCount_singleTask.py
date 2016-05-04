# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:30:31 2016

@author: Aaron.Lin
"""

#get_ipython().magic(u'matplotlib qt')
from skimage import io
#from skimage import color
from skimage import filters
from skimage.transform import resize
from skimage import morphology
#from skimage.morphology import disk
from skimage import measure
#from os import listdir
from PIL import Image,ImageDraw,ImageFont
import numpy
import mahotas
from skimage.util import img_as_ubyte
from skimage.morphology import disk
import json


def img_resize(img,max_size):
    len1 = img.shape[0]
    len2 = img.shape[1]
    if (len1>=len2):
        factor = float(max_size)/len1
        img_out = resize(img,(max_size,int(factor*len2)))
    else:
        factor =float(max_size)/len2
        img_out = resize(img,(int(factor*len1),max_size))
    return img_out
###############################################################################




def cellCount_singleTask(image_input_path, image_output_path, json_path):
    
    img_ori=io.imread(image_input_path)
    if(img_ori.shape[0]>1024 or img_ori.shape[1]>1024):
        img_ori_resize=img_resize(img_ori,1024)  #resize
    else:
        img_ori_resize=img_ori
    img_ori_resize=img_as_ubyte(img_ori_resize)
    img_gray=img_ori_resize[:,:,2] #only using blue layer
    #img_enhance=filters.rank.enhance_contrast(img_gray,disk(5))
    #thresh=filters.threshold_otsu(img_enhance)
    thresh=filters.threshold_otsu(img_gray)            
    #if (thresh>50):
    #    thresh -= 10;
    thresh = round(thresh*0.7)            
    img_thresh=img_gray>thresh
    img_opening=morphology.binary_opening(img_thresh)   #remove salt
    img_label=measure.label(img_opening)
    region=measure.regionprops(img_label)
    area_list=[]
    for i in region:
        area_list.append(i.area)
    area_list.sort
    area_mean=round(numpy.mean(area_list[int(len(area_list)*0.1):int(len(area_list)*0.9)]))
    #remove small object (area<(area_mean/2)            
    img_prepro2=morphology.remove_small_objects(img_opening,area_mean/3)
    img_label2=measure.label(img_prepro2)
    img_dist=mahotas.distance(img_label2)
    img_edge=img_dist==1
    ###################################
    #watershed test            
    #img_rmax=mahotas.regmax(img_dist)
    #img_seed=measure.label(img_rmax,connectivity=1)
    #img_watershed=morphology.watershed(-img_dist,img_seed,mask=img_label2)
    #img_watershed_dist=mahotas.distance(img_watershed)
    #img_edge=img_watershed_dist==1       
    ###################################
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (img_edge[i,j]):
                img_ori_resize[i,j,0]=255
    region2=measure.regionprops(img_label2)
    area_list2=[]
    for i in region2:
        area_list2.append(i.area)
    area_list2.sort
    area_mean2=round(numpy.mean(area_list2[int(len(area_list2)*0):int(len(area_list2)*0.9)]))
              
    
    image_ori_resize=Image.fromarray(img_ori_resize)
    draw=ImageDraw.Draw(image_ori_resize)
    font = ImageFont.truetype("arial.ttf", 20)  
    cellCount=0
    for i in region2:
        if (round(i.area/area_mean2)):
            cellCount +=round(i.area/area_mean2)
            draw.text((int(i.centroid[1]),int(i.centroid[0])),str(int(round((i.area/area_mean2)))),(0,255,0),font=font)
        elif (i.area/area_mean2>=0.3 and i.area/area_mean2<0.5):
            cellCount +=1
            draw.text((int(i.centroid[1]),int(i.centroid[0])),'1',(0,255,0),font=font)
    font = ImageFont.truetype("arial.ttf", image_ori_resize.size[0]/20)  
    draw.text((40,40),'counts='+str(int(cellCount)),(255,255,255),font=font)
    #Image.Image.show(image_ori_resize)
    #image_ori=resize(image_ori_resize,(img_ori.shape[0],img_ori.shape[1])) 
    image_ori=image_ori_resize.resize((img_ori.shape[1],img_ori.shape[0]))            
    io.imsave(image_output_path,image_ori)
    
    out_file = open(json_path,"w")
    cellCount_result = {'count': int(cellCount)}    
    json.dump(cellCount_result,out_file)
    out_file.close()
    
    return

###############################################################################
#image_path = "D:\Aaron workspace\Aaron\CellCount_Project\Image data\\CellC_One_t2.png"
#image_output_path = "D:\Aaron workspace\Aaron\CellCount_Project\output_single\\result.jpg"
#json_path = "D:\Aaron workspace\Aaron\CellCount_Project\output_single\\result.json"
#cellCount_singleTask(image_path,image_output_path,json_path)
            
            
            
            
            
            