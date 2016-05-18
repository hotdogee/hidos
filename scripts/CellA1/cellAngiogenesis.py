# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:55:18 2016

@author: Aaron.Lin
"""
import numpy
from numpy import array
import pymorph as m
from skimage import io, color, filters, morphology, measure
import scipy
import mahotas
from PIL import Image,ImageDraw,ImageFont
from skimage import img_as_ubyte
from skimage.transform import resize   
from os import listdir
import matplotlib.pyplot as plt
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
    img_out=img_as_ubyte(img_out)
    return img_out

def findIsolatedPoint(img):
    # structuring elements to search for endpoint pixels
    seA1 = array([[False,False,False],
                  [False,True,False],
                  [False,False,False]], dtype=bool)

    seB1 = array([[True,True,True],
                  [True,False,True],
                  [True,True,True]], dtype=bool)

    # hit or miss templates from these SEs
    hmt1 = m.se2hmt(seA1, seB1)
    # locate endpoint regions
    b1=m.supcanon(img,hmt1)

    # dilate to merge nearby hits
    #b2 = m.dilate(b1, m.sedisk(10))

    # locate centroids
    #b6 = m.blob(m.label(b5), 'centroid')

    #outputimage = m.overlay(img,green=m.dilate(b1,m.sedisk(1)))
    #io.imshow(outputimage)    
    
    return b1



def findExtremities(img):
    # structuring elements to search for endpoint pixels
    seA1 = array([[False,False,False],
                  [False,True,False],
                  [False,True,False]], dtype=bool)

    seB1 = array([[True,True,True],
                  [True,False,True],
                  [True,False,True]], dtype=bool)
                  
    seA2 = array([[False,False,False],
                  [True,True,False],
                  [True,False,False]], dtype=bool)

    seB2 = array([[True,True,True],
                  [False,False,True],
                  [False,True,True]], dtype=bool)

    # hit or miss templates from these SEs
    hmt1 = m.se2hmt(seA1, seB1)
    hmt2 = m.se2hmt(seA2, seB2)
    # locate endpoint regions
    b1 = m.union(m.supcanon(img, hmt1), m.supcanon(img, hmt2))

    # dilate to merge nearby hits
    #b2 = m.dilate(b1, m.sedisk(10))

    # locate centroids
    #b6 = m.blob(m.label(b5), 'centroid')

    #outputimage = m.overlay(img,blue=m.dilate(b1,m.sedisk(1)))
    #io.imshow(outputimage)    
    
    return b1
    
def findJunctions(img):
    # structuring elements to search for 3-connected pixels
    seA1 = array([[False,True,False],
                  [False,True,False],
                  [True,False,True]], dtype=bool)

    seB1 = array([[False,False,False],
                  [True,False,True],
                  [False,True,False]], dtype=bool)

    seA2 = array([[False,True,False],
                  [True,True,True],
                  [False,False,False]], dtype=bool)

    seB2 = array([[True,False,True],
                  [False,False,False],
                  [False,True,False]], dtype=bool)
    
    seA3 = array([[False,False,True],
                  [True,True,False],
                  [False,True,False]], dtype=bool)

    seB3 = array([[True,True,False],
                  [False,False,True],
                  [False,False,False]], dtype=bool)              

    # hit or miss templates from these SEs
    hmt1 = m.se2hmt(seA1, seB1)
    hmt2 = m.se2hmt(seA2, seB2)
    hmt3 = m.se2hmt(seA3, seB3)

    # locate 3-connected regions
    b1 = m.union(m.supcanon(img, hmt1), m.supcanon(img, hmt2), m.supcanon(img, hmt3))
    #b1 = m.union(m.supcanon(img, hmt1), m.supcanon(img, hmt2))
      
    # dilate to merge nearby hits
    #b2 = m.dilate(b1, m.sedisk(2))

    # locate centroids
    #b3 = m.blob(m.label(b2), 'centroid')

    #outputimage = m.overlay(img, m.dilate(b3,m.sedisk(2)))
    #outputimage = m.overlay(img, b1)    
    #io.imshow(outputimage)
        
    return b1

def deleteBranch(img,extremityMap,junctionMap,len_thresh,disk_size):
    
    if (disk_size>0):    
        j2=m.dilate(junctionMap,m.sedisk(disk_size))  #避免切不斷
        img_segmentation=img>j2
    else:
        img_segmentation=img^junctionMap
    img_label=measure.label(img_segmentation)
    region=measure.regionprops(img_label)
    img_result=numpy.zeros_like(img)
    #extremityMap=img_as_uint(extremityMap)
    #extremityMap/=65535
    for i in region:
        for j in range(i.coords.shape[0]):
            if (extremityMap[i.coords[j,0],i.coords[j,1]] and i.area<len_thresh):
                #extremityMap[i.coords[j,0],i.coords[j,1]]=i.area
                img_result+=(img_label==i.label)
                break
            
    return img_result
    
def detectAllBranch(img,extremityMap,junctionMap):
    
    j2=m.dilate(junctionMap,m.sedisk(2))  #避免切不斷
    img_segmentation=img>j2
    img_label=measure.label(img_segmentation)
    region=measure.regionprops(img_label)
    img_result=numpy.zeros_like(img)
    
    max_len=0
    for i in region:
        if (i.area>max_len):
            max_len=i.area
            
    for i in region:
        for j in range(i.coords.shape[0]):
            if (extremityMap[i.coords[j,0],i.coords[j,1]] and i.area<max_len):
                #extremityMap[i.coords[j,0],i.coords[j,1]]=i.area
                img_result+=(img_label==i.label)
                break
            
    return img_result
 
def removeSmallObject(img_label,min_size):
    
    label_region=measure.regionprops(img_label)    
    for i in label_region:
        if (i.area<min_size):
            for j in range(i.coords.shape[0]):
                img_label[i.coords[j,0],i.coords[j,1]]=0
    
    img_remove_small_object=img_label>0            
    
    return img_remove_small_object

def pruneTree(img_skeleton,extremityMap,junctionMap,iter_num):
    
    for i in range(iter_num):
        if (i==0):           
            small_branch=deleteBranch(img_skeleton,extremityMap,junctionMap,20,2)
        else:
            small_branch=deleteBranch(img_skeleton,extremityMap,junctionMap,20,0)
        img_remove_small_branch=img_skeleton^small_branch
        img_label=measure.label(img_remove_small_branch)
        img_skeleton=removeSmallObject(img_label,10)
        extremityMap=findExtremities(img_skeleton)
        junctionMap=findJunctions(img_skeleton)
        #outputimage = m.overlay(img_skeleton,blue=extremityMap, red=junctionMap)
    img_pruneTree=img_skeleton
    return img_pruneTree
   

def cellAngiogenesis(image_input_path, image_output_path, json_path):
    img_ori=io.imread(image_input_path)
    
    if(img_ori.shape[0]>2048 or img_ori.shape[1]>2048):
        img_ori_resize=img_resize(img_ori,2048)  #resize
    else:
        img_ori_resize=img_ori
    
#    plt.figure()
#    io.imshow(img_ori)
#    io.show()
    
    img_gray=color.rgb2gray(img_ori_resize)  #rgb2gray
#    plt.figure()
#    io.imshow(img_gray)
#    io.show()    
    
    
    #img_gray=color.rgb2gray(img_ori)
    img_prewitt=filters.prewitt(img_gray)
#    plt.figure()
#    io.imshow(img_prewitt)
#    io.show()

    
    thresh=filters.threshold_otsu(img_prewitt[img_prewitt.shape[0]/4:img_prewitt.shape[0]*3/4,img_prewitt.shape[0]/4:img_prewitt.shape[1]*3/4])
    img_thresh=img_prewitt>=thresh
#    plt.figure()
#    io.imshow(img_thresh)
#    io.show()
    
    #img_dilation=morphology.binary_dilation(img_thresh)
    #img_dilation=morphology.binary_dilation(img_dilation)
    img_dilation = m.dilate(img_thresh, m.sedisk(5))
#    plt.figure()
#    io.imshow(img_dilation)
#    io.show()
    
    img_skeleton=morphology.skeletonize(img_dilation)
#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()
    
    
    
    ######################################################################
    #find threshold for small hole
    img_fill_holes = scipy.ndimage.binary_fill_holes(img_skeleton)
#    plt.figure()
#    io.imshow(img_fill_holes)
#    io.show()
    
    img_region=img_fill_holes^img_skeleton
#    plt.figure()
#    io.imshow(img_region)
#    io.show()    
    
    img_region=m.erode(img_region, m.sedisk(1))
#    plt.figure()
#    io.imshow(img_region)
#    io.show()    
    
    img_label=measure.label(img_region)
    label_region=measure.regionprops(img_label)    
    hole_size=[]
    for i in label_region:
        hole_size.append(i.area)
    hole_size.sort()
    
    gap=0
    index=0
    if float(hole_size[-1])/img_fill_holes.size<0.005: #the area of maximum hole still too small, therefore remove all holes  
        size_thresh=hole_size[-1]+1000
    else:
        area_thresh=(img_ori_resize.shape[0]/40)*(img_ori_resize.shape[1]/40)
        for i in range(numpy.size(hole_size)-2):
            #print(hole_size[i])
            #if (round(float(hole_size[i+1])/hole_size[i])>gap and (hole_size[i+1]-hole_size[i])>100):
            if ((float(hole_size[i+1])-hole_size[i])/hole_size[i]>gap and hole_size[i+1]>area_thresh):
                gap=(float(hole_size[i+1])-hole_size[i])/hole_size[i]
                index=i+1
                if (round(gap)):
                    break
        if(index<(numpy.size(hole_size)-3)):
            size_thresh=hole_size[index]
        else:
            size_thresh=area_thresh
    #print(size_thresh,index,numpy.size(hole_size))
    ####################################################################
        
    
    img_remove_small_hole=morphology.remove_small_holes(img_skeleton,min_size=size_thresh)
#    plt.figure()
#    io.imshow(img_remove_small_hole)
#    io.show()    
    
    #io.imshow(img_remove_small_hole)
    img_skeleton=morphology.skeletonize(img_remove_small_hole) #remove small hole by skeleton
#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()
    
    #怪怪的~只是把所有的branch縮短15pixel(正確做法應該是砍掉<15的branch)   
    #img_remove_small_branch = m.thin(img_skeleton2, m.endpoints('homotopic'), 15) # prune small branches, may need tuning
    
    #isolatedPoints=findIsolatedPoint(img_skeleton)
    #img_remove_isolatedPoints = img_skeleton^isolatedPoints
    
    #extremityMap=findExtremities(img_remove_isolatedPoints)
    #junctionMap=findJunctions(img_remove_isolatedPoints)
    
    #outputimage = m.overlay(img_remove_isolatedPoints,blue=m.dilate(extremityMap,m.sedisk(1)), red=m.dilate(junctionMap,m.sedisk(1)))
    #io.imshow(outputimage)
        
    
#    small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,20)
#    img_remove_small_branch=img_remove_isolatedPoints^small_branch
#    
#    img_label=measure.label(img_remove_small_branch)
#    img_remove_small_object=removeSmallObject(img_label,10)
#    
#    extremityMap=findExtremities(img_remove_small_object)
#    junctionMap=findJunctions(img_remove_small_object)
#    outputimage = m.overlay(img_remove_small_object,blue=extremityMap, red=junctionMap)
#    io.imshow(outputimage)
    
    #img_remove_small_object=pruneTree(img_remove_isolatedPoints,extremityMap,junctionMap,3)
    
    
    for i in range(2):
        isolatedPoints=findIsolatedPoint(img_skeleton)
#        plt.figure()
#        io.imshow(m.dilate(isolatedPoints, m.sedisk(2)))
#        io.show()
        
        img_remove_isolatedPoints = img_skeleton^isolatedPoints
        
        extremityMap=findExtremities(img_remove_isolatedPoints)
#        plt.figure()
#        io.imshow(m.dilate(extremityMap, m.sedisk(2)))
#        io.show()
        
        junctionMap=findJunctions(img_remove_isolatedPoints)
#        plt.figure()
#        io.imshow(m.dilate(junctionMap, m.sedisk(2)))
#        io.show()
        
        if (i==0):           
            small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,30,2)
        else:
            small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,30,0)
        img_remove_small_branch=img_remove_isolatedPoints^small_branch
#        plt.figure()
#        io.imshow(img_remove_small_branch)
#        io.show()        
        
        img_label=measure.label(img_remove_small_branch)
        img_remove_small_object=removeSmallObject(img_label,10)
#        plt.figure()
#        io.imshow(img_remove_small_object)
#        io.show()      
        
        img_skeleton = m.thin(img_remove_small_object, m.endpoints('homotopic'),1)

#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()
    img_final=m.dilate(img_skeleton, m.sedisk(7))
#    plt.figure()
#    io.imshow(img_final)
#    io.show()  
    
    img_final=morphology.skeletonize(img_final)
#    plt.figure()
#    io.imshow(img_final)
#    io.show()     
    
#    img_final=morphology.remove_small_holes(img_final,min_size=size_thresh)
#    img_final=morphology.skeletonize(img_final) #remove small hole by skeleton    
    
    isolatedPoints=findIsolatedPoint(img_final)
#    plt.figure()
#    io.imshow(m.dilate(isolatedPoints, m.sedisk(2)))
#    io.show()
    
    img_final = img_final^isolatedPoints
    extremityMap=findExtremities(img_final)
#    plt.figure()
#    io.imshow(m.dilate(extremityMap, m.sedisk(2)))
#    io.show()
    
    junctionMap=findJunctions(img_final)
#    plt.figure()
#    io.imshow(m.dilate(junctionMap, m.sedisk(2)))
#    io.show()
    
    #outputimage = m.overlay(img_final,blue=extremityMap, red=junctionMap)
    #io.imshow(outputimage)
    
    allBranch=detectAllBranch(img_final,extremityMap,junctionMap)
#    plt.figure()
#    io.imshow(m.dilate(allBranch, m.sedisk(2)))
#    io.show()    
    
    img_final^=allBranch
#    plt.figure()
#    io.imshow(m.dilate(img_final, m.sedisk(2)))
#    io.show()
     
    #measurement
    num_extremity=extremityMap.sum()
    num_junction=junctionMap.sum()
    tot_branch_len=round(float(allBranch.sum())/img_final.size,6)
    tot_seg_len=round(float(img_final.sum())/img_final.size,6)
    tot_len=tot_branch_len+tot_seg_len
    ###############################
     
    
    img_fill_holes = scipy.ndimage.binary_fill_holes(img_final)    
    img_region=img_fill_holes^img_final
    #reduce the region size in order to seperate each region by ersoion
    #img_region=morphology.binary_erosion(img_region)
    img_region=m.erode(img_region, m.sedisk(1)) 
    img_label=measure.label(img_region)
    img_dist=mahotas.distance(img_label)
    img_edge=((img_dist>=25)^(img_dist>=64))
#    plt.figure()
#    io.imshow(img_edge)
#    io.show() 
    
    #img_edge=m.dilate(img_edge, m.sedisk(2)) 
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (img_edge[i,j]):
                img_ori_resize[i,j,0]=0
                img_ori_resize[i,j,1]=255
                img_ori_resize[i,j,2]=0
    
    img_final=m.dilate(img_final, m.sedisk(2))  
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (img_final[i,j]):
                img_ori_resize[i,j,0]=255
                img_ori_resize[i,j,1]=0
                img_ori_resize[i,j,2]=0
                 
    # dilate to merge nearby hits
    junctionMap = m.dilate(junctionMap, m.sedisk(7))
    # locate centroids
    junctionMap = m.blob(m.label(junctionMap), 'centroid')
    junctionMap = m.dilate(junctionMap, m.sedisk(5))
    
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (junctionMap[i,j]):
                img_ori_resize[i,j,0]=255
                img_ori_resize[i,j,1]=255
                img_ori_resize[i,j,2]=255
            
    allBranch=m.dilate(allBranch, m.sedisk(2))              
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (allBranch[i,j]):
                img_ori_resize[i,j,0]=0
                img_ori_resize[i,j,1]=255
                img_ori_resize[i,j,2]=255
    
    extremityMap = m.dilate(extremityMap, m.sedisk(5))    
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (extremityMap[i,j]):
                img_ori_resize[i,j,0]=255
                img_ori_resize[i,j,1]=255
                img_ori_resize[i,j,2]=0    
    
    regions=measure.regionprops(img_label)
    image_ori_resize=Image.fromarray(img_ori_resize)
    draw=ImageDraw.Draw(image_ori_resize)
    font = ImageFont.truetype("DejaVuSerif-Italic.ttf", 25)  
    
    num_mesh=0
    tot_mesh_area=0
    for i in regions:
        draw.text((int(i.centroid[1]),int(i.centroid[0])),str(i.label),(0,0,255),font=font)
        num_mesh+=1
        tot_mesh_area+=i.area
    
    tot_mesh_area=round(float(tot_mesh_area)/img_final.size,6)
    
    image_ori=image_ori_resize.resize((img_ori.shape[1],img_ori.shape[0]))
    image_ori.save(image_output_path)
    #Image.Image.show(image_ori)
    #io.imshow(img_ori)
     
    out_file = open(json_path,"w")
    angiogenesis_result = {'#Extremity':num_extremity,'#Junction':num_junction,'Tot. branch length':tot_branch_len, 'Tot. segment legnth':tot_seg_len, 'Tot. network legth':tot_len, '#Mesh':num_mesh,'Tot.mesh area':tot_mesh_area}
    json.dump(angiogenesis_result,out_file)
    out_file.close()     
     
    return


# img_input_path=u'D:\Aaron workspace\Aaron\CellAngiogenesis_Project\Image data\CellQA_images_all'
# img_output_path=u'D:\Aaron workspace\Aaron\CellAngiogenesis_Project\Image data\out'
# file_list = listdir(img_input_path)
# for filename in file_list:  
#     if (filename[0]!='.'):
#         print('Cell angiogenesis analyzing for %s'%filename)
#         Img_filename=img_input_path+'\\'+filename
#         Img_output_filename=img_output_path+'\\'+filename
#         inx=Img_output_filename.rfind('.')
#         json_filename=Img_output_filename[0:inx]+'.json'
#         cellAngiogenesis(Img_filename,Img_output_filename,json_filename)
          
    













