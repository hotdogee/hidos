# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:55:18 2016

@author: Aaron.Lin
"""

import cv2
import scipy
import pymorph as m
from skimage import feature, color, morphology, measure
from skimage import img_as_ubyte
import numpy as np
import json
#import time
#from os import listdir


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

def findIsolatedPoint(img):
    # structuring elements to search for endpoint pixels
    seA1 = np.array([[False,False,False],
                  [False,True,False],
                  [False,False,False]], dtype=bool)

    seB1 = np.array([[True,True,True],
                  [True,False,True],
                  [True,True,True]], dtype=bool)

    # hit or miss templates from these SEs
    hmt1 = m.se2hmt(seA1, seB1)
    # locate endpoint regions
    b1=m.supcanon(img,hmt1)

    return b1



def findExtremities(img):
    # structuring elements to search for endpoint pixels
    seA1 = np.array([[False,False,False],
                  [False,True,False],
                  [False,True,False]], dtype=bool)

    seB1 = np.array([[True,True,True],
                  [True,False,True],
                  [True,False,True]], dtype=bool)

    seA2 = np.array([[False,False,False],
                  [False,True,False],
                  [True,False,False]], dtype=bool)

    seB2 = np.array([[True,True,True],
                  [False,False,True],
                  [False,True,True]], dtype=bool)

    seA3 = np.array([[True,False,False],
                  [False,True,False],
                  [False,False,False]], dtype=bool)

    seB3 = np.array([[False,True,True],
                  [False,False,True],
                  [True,True,True]], dtype=bool)

    # hit or miss templates from these SEs
    hmt1 = m.se2hmt(seA1, seB1)
    hmt2 = m.se2hmt(seA2, seB2)
    hmt3 = m.se2hmt(seA3, seB3)
    # locate endpoint regions
    b1 = m.union(m.supcanon(img, hmt1), m.supcanon(img, hmt2), m.supcanon(img, hmt3))

    return b1

def findJunctions(img):
    # structuring elements to search for 3-connected pixels
    seA1 = np.array([[False,True,False],
                  [False,True,False],
                  [True,False,True]], dtype=bool)

    seB1 = np.array([[False,False,False],
                  [True,False,True],
                  [False,True,False]], dtype=bool)

    seA2 = np.array([[False,True,False],
                  [True,True,True],
                  [False,False,False]], dtype=bool)

    seB2 = np.array([[True,False,True],
                  [False,False,False],
                  [False,True,False]], dtype=bool)

    seA3 = np.array([[False,False,True],
                  [True,True,False],
                  [False,True,False]], dtype=bool)

    seB3 = np.array([[False,True,False],
                  [False,False,True],
                  [False,False,False]], dtype=bool)

    # hit or miss templates from these SEs
    hmt1 = m.se2hmt(seA1, seB1)
    hmt2 = m.se2hmt(seA2, seB2)
    hmt3 = m.se2hmt(seA3, seB3)

    # locate 3-connected regions
    b1 = m.union(m.supcanon(img, hmt1), m.supcanon(img, hmt2), m.supcanon(img, hmt3))

    return b1

#def deleteBranch(img,extremityMap,junctionMap,len_thresh,disk_size):
def deleteBranch(img,extremityMap,junctionMap,len_thresh):

    #if (disk_size>0):#避免切不斷
    kernel=np.array([[0,1,0],[1,1,1],[0,1,0]],np.ubyte)
    j2=cv2.dilate(np.uint8(junctionMap),kernel)
    img_segmentation=img>j2
    #else:
    #    img_segmentation=img^junctionMap
    ret, img_label = cv2.connectedComponents(np.uint8(img_segmentation))
    region=measure.regionprops(img_label)
    img_result=np.zeros_like(img)
    for i in region:
        if (i.area<len_thresh):
            for j in range(i.coords.shape[0]):
                if (extremityMap[i.coords[j,0],i.coords[j,1]]):
                    img_result+=(img_label==i.label)
                    break

    return img_result

def detectAllBranch(img,extremityMap,junctionMap):

    #避免切不斷
    kernel=np.array([[0,1,0],[1,1,1],[0,1,0]],np.ubyte)
    j2=cv2.dilate(np.uint8(junctionMap),kernel)
    img_segmentation=img>j2
    ret, img_label = cv2.connectedComponents(np.uint8(img_segmentation))
    region=measure.regionprops(img_label)
    img_result=np.zeros_like(img)

    max_len=0
    for i in region:
        if (i.area>max_len):
            max_len=i.area

    for i in region:
        if (i.area<=max_len):
            for j in range(i.coords.shape[0]):
                if (extremityMap[i.coords[j,0],i.coords[j,1]]):
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
#        if (i==0):
#            small_branch=deleteBranch(img_skeleton,extremityMap,junctionMap,20,2)
#        else:
#            small_branch=deleteBranch(img_skeleton,extremityMap,junctionMap,20,0)
#
        small_branch=deleteBranch(img_skeleton,extremityMap,junctionMap,20)

        img_remove_small_branch=img_skeleton^small_branch
        img_label=measure.label(img_remove_small_branch)
        img_skeleton=removeSmallObject(img_label,10)
        extremityMap=findExtremities(img_skeleton)
        junctionMap=findJunctions(img_skeleton)
        #outputimage = m.overlay(img_skeleton,blue=extremityMap, red=junctionMap)
    img_pruneTree=img_skeleton
    return img_pruneTree


def cellAngiogenesis(image_input_path, image_output_path, json_path, add_boarder=False):

#    tStart=time.time()

    img_ori=cv2.imread(image_input_path)
    img_ori_resize=img_resize(img_ori,1600)  #resize

    #如果先resize再取gray~效果會比較差
    img_gray=cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)
    img_gray=img_resize(img_gray,1600)  #resize
#    plt.figure()
#    io.imshow(img_gray)
#    io.show()

#    img_prewitt=filters.prewitt(img_gray)
#    img_prewitt*=255
#    img_prewitt=np.uint8(img_prewitt)
##    plt.figure()
##    io.imshow(img_prewitt)
##    io.show()
#
#    if (add_boarder):
#        img_prewitt[0:1,:]=img_prewitt.max()
#        img_prewitt[-1:-2,:]=img_prewitt.max()
#        img_prewitt[:,0:1]=img_prewitt.max()
#        img_prewitt[:,-1:-2]=img_prewitt.max()
#
#    thresh, img_thresh= cv2.threshold(img_prewitt,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

#    plt.figure()
#    io.imshow(img_thresh)
#    io.show()

    img_thresh=feature.canny(img_gray) #bool output
    img_thresh=np.uint8(img_thresh)

    if (max(img_thresh.shape)>1000):
        kernel=np.array(m.sedisk(7),np.ubyte)
    elif (max(img_thresh.shape)>500):
        kernel=np.array(m.sedisk(6),np.ubyte)
    else:
        kernel=np.array(m.sedisk(5),np.ubyte)
    img_dilation = np.array(cv2.dilate(img_thresh,kernel),np.bool)
#    plt.figure()
#    io.imshow(img_dilation)
#    io.show()

    img_skeleton=morphology.skeletonize(img_dilation)
#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()

    if (add_boarder):
        img_skeleton[0:1,:]=img_skeleton.max()
        img_skeleton[-1:-2,:]=img_skeleton.max()
        img_skeleton[:,0:1]=img_skeleton.max()
        img_skeleton[:,-1:-2]=img_skeleton.max()


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

    img_region=np.uint8(img_region)
    img_region = cv2.erode(img_region,np.uint8(m.sedisk(1)))
#    plt.figure()
#    io.imshow(img_region)
#    io.show()

    ret, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_region)
    hole_size=stats[1:,4].copy()
    hole_size.sort()

    gap=0
    index=0

#    for i in range(np.size(hole_size)):
#        print(hole_size[i])

    if float(hole_size[-1])/img_fill_holes.size<0.005: #the area of maximum hole still too small, therefore remove all holes
        size_thresh=hole_size[-1]+1000
    else:
        area_thresh=(img_ori_resize.shape[0]/30)*(img_ori_resize.shape[1]/30)
        for i in range(np.size(hole_size)-2):
            #if (round(float(hole_size[i+1])/hole_size[i])>gap and (hole_size[i+1]-hole_size[i])>100):
            if ((float(hole_size[i+1])-hole_size[i])/hole_size[i]>gap and hole_size[i+1]>area_thresh):
                gap=(float(hole_size[i+1])-hole_size[i])/hole_size[i]
                index=i+1
                if (gap>0.2):
                    break
        if(index<(np.size(hole_size)-3) and hole_size[index]>area_thresh):
            size_thresh=hole_size[index]
        else:
            size_thresh=area_thresh
#    print(size_thresh,index,numpy.size(hole_size))
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

    for i in range(1):
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
#        if (i==0):
#            small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,30,2)
#        else:
#            small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,30,0)

        small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,30)

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

    kernel=np.array(m.sedisk(7),np.ubyte)

    img_final = cv2.dilate(np.uint8(img_skeleton),kernel)

#    img_final=m.dilate(img_skeleton, m.sedisk(7))
#    plt.figure()
#    io.imshow(img_final)
#    io.show()

    img_final=morphology.skeletonize(img_final)


    img_remove_small_hole=morphology.remove_small_holes(img_final,min_size=size_thresh)
    img_final=morphology.skeletonize(img_remove_small_hole) #remove small hole by skeleton


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
#    tot_branch_len=round(float(allBranch.sum())/img_final.size,6)
#    tot_seg_len=round(float(img_final.sum())/img_final.size,6)
#    tot_len=round(tot_branch_len+tot_seg_len,6)
    tot_branch_len=allBranch.sum()
    tot_seg_len=img_final.sum()
    tot_len=tot_branch_len+tot_seg_len
    ###############################

    img_fill_holes = scipy.ndimage.binary_fill_holes(img_final)
    img_region=img_fill_holes^img_final
    #reduce the region size in order to seperate each region by ersoion

    img_region=cv2.erode(np.uint8(img_region),np.uint8(m.sedisk(1)))
    ret, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_region)

#    plt.figure()
#    io.imshow(img_region)
#    io.show()

    #img_region=m.erode(img_region, m.sedisk(1))
    #img_label=measure.label(img_region)
    #img_dist=mahotas.distance(img_label)
    #img_edge=((img_dist>=25)^(img_dist>=64))
#    plt.figure()
#    io.imshow(img_edge)
#    io.show()

    img_label_color=color.label2rgb(img_label,bg_label=0)
    img_label_color=img_as_ubyte(img_label_color)

    mask=np.where(img_label_color>0)
    t0=np.zeros(len(mask[0]),np.ubyte)
    t1=np.ones(len(mask[1]),np.ubyte)
    t2=t1+t1
    mask0=[mask[0],mask[1],t0]
    mask1=[mask[0],mask[1],t1]
    mask2=[mask[0],mask[1],t2]
    img_ori_resize=np.array(img_ori_resize,float)
    img_ori_resize[mask0]=(img_ori_resize[mask0]*0.7)+(img_label_color[mask0]*0.3)
    img_ori_resize[mask1]=(img_ori_resize[mask1]*0.7)+(img_label_color[mask1]*0.3)
    img_ori_resize[mask2]=(img_ori_resize[mask2]*0.7)+(img_label_color[mask2]*0.3)
    img_ori_resize=np.uint8(img_ori_resize)
#    plt.figure()
#    io.imshow(img_ori_resize)
#    io.show()

    img_final = cv2.dilate(np.uint8(img_final),np.uint8(m.sedisk(1)))
    mask=np.where(img_final>0)
    img_ori_resize[mask]=[0,0,255]

    allBranch = cv2.dilate(np.uint8(allBranch),np.uint8(m.sedisk(1)))
    mask=np.where(allBranch>0)
    img_ori_resize[mask]=[255,255,0]

    # dilate to merge nearby hits
    junctionMap = cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(7)))
    # locate centroids
    junctionMap = m.blob(m.label(junctionMap), 'centroid')
    junctionMap = cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(5)))
    mask=np.where(junctionMap>0)
    img_ori_resize[mask]=[255,255,255]

    extremityMap = cv2.dilate(np.uint8(extremityMap), np.uint8(m.sedisk(5)))
    mask=np.where(extremityMap>0)
    img_ori_resize[mask]=[0,255,255]

    ret_extremity, img_label= cv2.connectedComponents(extremityMap)
    num_extremity=ret_extremity-1
    ret_junction, img_label= cv2.connectedComponents(junctionMap)
    num_junction=ret_junction-1

    num_mesh=0
    tot_mesh_area=0
    font =cv2.FONT_HERSHEY_SIMPLEX
    for i in range(1,ret):
        cv2.putText(img_ori_resize,str(i),(int(centroids[i,0]),int(centroids[i,1])), font,1,(255,0,0),2)
        num_mesh+=1
        tot_mesh_area+=stats[i,4]

#    tot_mesh_area=round(float(tot_mesh_area)/img_final.size,6)
    img_ori_resize = cv2.resize(img_ori_resize,(img_ori.shape[1],img_ori.shape[0]))
    cv2.imwrite(image_output_path,img_ori_resize)

    out_file = open(json_path,"w")
    # angiogenesis_result = {'#Extremity':num_extremity,'#Junction':num_junction,'Tot. branch length':tot_branch_len, 'Tot. segment length':tot_seg_len, 'Tot. network length':tot_len, '#Mesh':num_mesh,'Tot. mesh area':tot_mesh_area}


    angiogenesis_result = {'extremity': num_extremity, 'junction': num_junction, 'total_branch_length': tot_branch_len,
                           'total_segment_length': tot_seg_len, 'total_network_length': tot_len, 'mesh': num_mesh,
                           'total_mesh_area': tot_mesh_area}

    json.dump(angiogenesis_result,out_file)
    out_file.close()

#    tEnd=time.time()
#
#    print ("It costs %f sec",tEnd-tStart)

    return


#img_input_path=u'D:\Aaron workspace\Aaron\CellAngiogenesis_Project\Image data\\CellQA_images_all'
#img_output_path=u'D:\Aaron workspace\Aaron\CellAngiogenesis_Project\Image data\out_4'
#file_list = listdir(img_input_path)
#for filename in file_list:
#    if (filename[0]!='.'):
#        print('Cell angiogenesis analyzing for %s'%filename)
#        Img_filename=img_input_path+'\\'+filename
#        Img_output_filename=img_output_path+'\\'+filename
#        inx=Img_output_filename.rfind('.')
#        json_filename=Img_output_filename[0:inx]+'.json'
#        cellAngiogenesis(Img_filename,Img_output_filename,json_filename,add_boarder=False)

#image_path = u"C:\\Users\\Aaron.Lin\\Desktop\\demo image\\fsCDIumSZA.png"
#image_output_path = u"D:\Aaron workspace\Aaron\CellAngiogenesis_Project\output_test\\result.jpg"
#json_path = u"D:\Aaron workspace\Aaron\CellAngiogenesis_Project\output_test\\result.json"
#cellAngiogenesis(image_path,image_output_path,json_path)















