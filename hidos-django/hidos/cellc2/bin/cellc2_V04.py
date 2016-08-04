# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 16:02:34 2016

@author: Aaron.Lin
"""

#get_ipython().magic(u'matplotlib qt')    
import cv2
import numpy as np
from skimage import filters, morphology
import json
import time
from os import listdir
import matplotlib.pyplot as plt
from skimage import io
    
version = '0.4'    
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

###############################################################################
def cellC2_validation(image_input_path):
    
    img_ori=cv2.imread(image_input_path)
    img_gray=np.zeros_like(img_ori[:,:,0])    
    mask=np.where(img_ori[:,:,0]>200)
    img_gray[mask]=1
    confluence = 100*float(img_gray.sum())/img_gray.size
    
    return confluence

###############################################################################

def cellConfluence_singleTask(image_input_path, image_output_path, json_path):
    
#    tStart = time.time()
    
    img_ori=cv2.imread(image_input_path)    
    img_ori_resize=img_resize(img_ori,1024)  #resize
     
    #20160804處理全白的scale bar
    mask0=np.where(img_ori[:,:,0]>200)
    mask1=np.where(img_ori[:,:,1]>200)
    mask2=np.where(img_ori[:,:,2]>200)
    tmp0=np.zeros_like(img_ori[:,:,0])
    tmp1=np.zeros_like(img_ori[:,:,0])
    tmp2=np.zeros_like(img_ori[:,:,0])
    tmp0[mask0]=1
    tmp1[mask1]=1
    tmp2[mask2]=1
    tmp0=np.logical_and(tmp0,tmp1)
    tmp0=np.logical_and(tmp0,tmp2)
    mask=np.where(tmp0>0)
    img_ori[:,:,0][mask]=np.mean(img_ori[:,:,0])
    img_ori[:,:,1][mask]=np.mean(img_ori[:,:,1])
    img_ori[:,:,2][mask]=np.mean(img_ori[:,:,2])
    ###################################
     
    #如果先resize再取gray~效果會比較差
    img_gray=cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)
    img_gray=img_resize(img_gray,1024)  #resize    
     
#    plt.figure()
#    io.imshow(img_gray)
#    io.show() 
    
    img_prewitt=filters.prewitt(img_gray)    #detect edge
#    plt.figure()
#    io.imshow(img_prewitt)
#    io.show()    
    #enhance
    img_enhance=filters.rank.enhance_contrast(img_prewitt,np.array([[1,1,1],[1,1,1],[1,1,1]],np.ubyte))
    #binarization
    img_enhance = cv2.GaussianBlur(img_enhance,(5,5),0)
    thresh,img_thresh=cv2.threshold(img_enhance,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_thresh=img_enhance>=thresh
    img_thresh=np.uint8(img_thresh) 
    
#    plt.figure()
#    io.imshow(img_thresh)
#    io.show()  
    
    #print thresh
    if (thresh<5):
        kernel = np.ones((2,2),np.uint8)
        img_thresh = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, kernel)  #remove salt 
    
    kernel=np.array([[1,1,1],[1,1,1],[1,1,1]],np.ubyte)    
    img_dilation=cv2.dilate(img_thresh,kernel,iterations=4) 
#    plt.figure()
#    io.imshow(img_dilation)
#    io.show()  
    img_erosion=cv2.erode(img_dilation,kernel,iterations=2)    
    img_opening = cv2.morphologyEx(img_erosion, cv2.MORPH_OPEN, kernel)  #remove salt 
        
#    for i in range(img_opening.shape[0]):
#        for j in range(img_opening.shape[1]):
#            if (img_opening[i,j]):
#                img_ori_resize[i,j,2]=200
 
    if (max(img_opening.shape)>=1024):   
        if (float(img_opening.sum())/img_opening.size<0.6):
            img_opening=morphology.remove_small_holes(img_opening,min_size=20*20)
        else:
            img_opening=morphology.remove_small_holes(img_opening,min_size=35*35)

               
    mask=np.where(img_opening>0)
    img_ori_resize[:,:,2][mask]=200

    #compute confluence
    confluence = 100*float(img_opening.sum())/img_opening.size
#    ratio=confluence
    confluence = '%.2f' % confluence 
    ### embed result to image
    font =cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_ori_resize,str(confluence+'%'),(40,80), font, 2,(255,0,0),3)  
    
    img_ori_resize = cv2.resize(img_ori_resize,(img_ori.shape[1],img_ori.shape[0]))
    cv2.imwrite(image_output_path,img_ori_resize)
    
    out_file = open(json_path,"w")
    confluence_result = {'confluence': confluence}    
    
    json.dump(confluence_result,out_file)
    out_file.close()    
    
#    tEnd = time.time()
#    print ("It costs %f sec",tEnd-tStart)    
    
    return #ratio
###############################################################################
#
#image_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\CellC MSC Images\P3173817.JPG"
#image_output_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\output_test\\result.jpg"
#json_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\output_test\\result.json"
##
##file_list = listdir(image_path)
##filename = file_list[7]
##filename=image_path +'\\'+filename         
#cellConfluence_singleTask(image_path,image_output_path,json_path)

#img_input_path=u'D:\Aaron workspace\Aaron\CellConfluence_Project\CellC MSC Images'
#img_input_path=u'C:\\Users\\Aaron.Lin\\Desktop\\cellC2_issue'
#img_input_path=u'C:\\Users\\Aaron.Lin\\Desktop\\demo image\\cellC2'
#img_input_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\Cell C2\\melanoma'
##img_output_path=u'D:\Aaron workspace\Aaron\CellConfluence_Project\output_test'
#img_output_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\Cell C2\\cellc2_result'
#file_list = listdir(img_input_path)
#for filename in file_list:  
#    if (filename[0]!='.'):
#        print('Cell confluence analyzing for %s'%filename)
#        Img_filename=img_input_path+'\\'+filename
#        Img_output_filename=img_output_path+'\\'+filename
#        inx=Img_output_filename.rfind('.')
#        json_filename=Img_output_filename[0:inx]+'.json'
#        cellConfluence_singleTask(Img_filename,Img_output_filename,json_filename)
        
        
        
#################BBBC for validation
#from scipy import stats
##img_input_path=u'D:\Aaron workspace\Aaron\CellConfluence_Project\CellC MSC Images'
#img_input_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\Cell C2\\melanoma'
#img_input_path2=u'D:\\Aaron workspace\\Aaron\\Benchmark\\Cell C2\\melanoma_verified'
#img_output_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\Cell C2\\cellc2_result2'
#file_list = listdir(img_input_path)
#result=np.empty([1,2])
#for filename in file_list:  
#    if (filename[0]!='.'):
#        print('Cell confluence analyzing for %s'%filename)
#        Img_filename=img_input_path+'\\'+filename
#        Img_filename2=img_input_path2+'\\'+filename
#        Img_output_filename=img_output_path+'\\'+filename
#        inx=Img_output_filename.rfind('.')
#        json_filename=Img_output_filename[0:inx]+'.json'
#        
#        inx=Img_filename2.rfind('.')
#        Img_filename2=Img_filename2[0:inx]+'.png' 
#        
#        
#        ratio=cellConfluence_singleTask(Img_filename,Img_output_filename,json_filename) 
#        ground_truth=cellC2_validation(Img_filename2)
#        result=np.append(result,[[ground_truth,ratio]],axis=0)
#        
#slope, intercept, r_value, p_value, std_err = stats.linregress(result[:,1],result[:,0])
#plt.figure()
#plt.scatter(result[1:,1],result[1:,0],color='blue')
#x=np.array(range(1,101),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
#plt.xlim([0,100])
#plt.ylim([0,100])
#plt.xlabel('CellC2',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(5, 80,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(5,72,'correlation coefficient=%f'%r_value,fontsize=14)           

        
##########################################


        