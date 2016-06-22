# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:30:31 2016

@author: Aaron.Lin
"""

#get_ipython().magic(u'matplotlib qt')
#import time
import cv2
import numpy as np
from skimage.morphology import remove_small_objects
import mahotas
import json

###############################################################################
def img_resize(img,max_size):
    len1 = img.shape[0]
    len2 = img.shape[1]
    
    if(len1<max_size and len2<max_size):
        return img
    
    if (len1>=len2):
        factor = float(max_size)/len1
        img_out = cv2.resize(img,(int(factor*len2),max_size))
    else:
        factor =float(max_size)/len2
        img_out = cv2.resize(img,(max_size,int(factor*len1)))
    return img_out
###############################################################################

def cellCount_singleTask(image_input_path, image_output_path, json_path):
   
    #tStart=time.time()   
       
    img_ori=cv2.imread(image_input_path)
    #img_ori=cv2.cvtColor(img_ori, cv2.COLOR_BGR2RGB)    #BGR->RGB
    
    img_ori_resize=img_resize(img_ori,1024)  #resize
    
    #automatically determine using which layer to analyze
    otsu_all=np.empty_like(img_ori_resize)
    ret_all = np.array([0,0,0])
    tmp_sum = np.array([0,0,0])
    for i in range(3):
        ret_all[i], otsu_all[:,:,i]= cv2.threshold(img_ori_resize[:,:,i],0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        tmp_sum[i]=otsu_all[:,:,i].sum()
    
    tmp_sum/=(tmp_sum.max()/10) #size如果差10倍以上,就不需考慮
    if (np.logical_and(ret_all>20,tmp_sum>0).sum()==0):
        inx=0
    else:
        inx=(tmp_sum==tmp_sum[np.logical_and(ret_all>20,tmp_sum>0)].min()).argmax() #二值化門檻值須>20且size需相差10倍以內,滿足這些條件下,選擇size較小的layer
    color_text = np.array([[0,255,255],[255,0,255],[255,255,0]])
    color_edge = np.array([[0,0,255],[255,0,0],[0,255,0]])
    ############################
    
    #cv2.imshow('image',img_gray)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    img_thresh=otsu_all[:,:,inx]
        
    kernel = np.ones((2,2),np.uint8)
    img_thresh=np.uint8(img_thresh)
    img_opening = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, kernel)  #remove salt 
        
    ret, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_opening)
    #stats 1:leftmost coordinate
    #stats 2:topmost coordinate
    #stats 3:horizontal size
    #stats 4:vertical size
    #stats 5:area    
    
    area_list=stats[1:,4].copy()
    area_list.sort()
    area_mean=round(np.mean(area_list[int(len(area_list)*0.1):int(len(area_list)*0.9)]))
    
    #remove small object          
    img_prepro2=remove_small_objects(np.bool_(img_opening),area_mean/3)
    img_prepro2=np.uint8(img_prepro2)
    ret, img_label2, stats2, centroids2 = cv2.connectedComponentsWithStats(img_prepro2)
    
    img_dist=mahotas.distance(img_label2)
    img_edge=img_dist==1
    
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (img_edge[i,j]):
                img_ori_resize[i,j,:]=color_edge[inx,:]
                    
    area_list2=stats2[1:,4].copy()
    area_list2.sort()
    area_mean2=round(np.mean(area_list2[int(len(area_list2)*0):int(len(area_list2)*0.9)]))
              
    cellCount=0
    out_file = open(json_path,"w")
    #exception
    font =cv2.FONT_HERSHEY_SIMPLEX
    if (np.isnan(area_mean2) or area_mean2<=0):
        cellCount_result = {'count': -1}
        cv2.putText(img_ori_resize,'This image can not be analyzed.',(40,80), font, 1,(255,255,255),2)    
    else:
        for i in range(1,ret):
            tmpCount=(stats2[i,4]/area_mean2)
            if (tmpCount>=0.3 and tmpCount<1):
                cellCount +=1
                cv2.putText(img_ori_resize,'1',(int(centroids2[i,0]),int(centroids2[i,1])), font, 1,color_text[inx,:],1) 
            elif (np.floor(tmpCount)):
                cellCount +=np.floor(tmpCount)
                cv2.putText(img_ori_resize,str(int(np.floor(tmpCount))),(int(centroids2[i,0]),int(centroids2[i,1])), font, 1,color_text[inx,:],1)
        cv2.putText(img_ori_resize,'counts='+str(int(cellCount)),(40,80), font, 2,(255,255,255),3) 
        cellCount_result = {'count': int(cellCount)}       
    
    img_ori_resize = cv2.resize(img_ori_resize,(img_ori.shape[1],img_ori.shape[0]))
    cv2.imwrite(image_output_path,img_ori_resize)
    json.dump(cellCount_result,out_file)
    out_file.close()
    
    #tEnd=time.time() 
    
    #print ("It costs %f sec",tEnd-tStart)    
    
    return

###############################################################################
#image_path = "C:\\Users\\Aaron.Lin\\Desktop\\cellC1_issue_image\\da7d2b9334ef3282b0d75fc03122ee86_uploaded.tiff"
#image_output_path = "D:\Aaron workspace\Aaron\CellCount_Project\\tiff\\result.jpg"
#json_path = "D:\Aaron workspace\Aaron\CellCount_Project\\tiff\\result.json"
#cellCount_singleTask(image_path,image_output_path,json_path)
            
            
            
            
            
            