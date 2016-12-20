# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:55:18 2016

@author: Aaron.Lin
"""

import cv2
import scipy
import pymorph as m
from skimage import feature, color, morphology, measure, filters
from skimage import img_as_ubyte
import numpy as np
import json
#import time
from os import listdir
import matplotlib.pyplot as plt
from skimage import io
import mahotas
from skimage import exposure

import scipy.ndimage.morphology as scipy_m


version = '0.3'

###############################################################################
def contrast_saturated(img):
    # imageJ auto contrast
    v_min, v_max = np.percentile(img, (1, 99))
    better_contrast = exposure.rescale_intensity(img, in_range=(v_min, v_max))
    return better_contrast
###############################################################################

###############################################################################
def img_resize(img,max_size):
    len1 = img.shape[0]
    len2 = img.shape[1]
    factor=1.0
#    if(len1<max_size and len2<max_size):
#        return img,factor

    if (len1>=len2):
        factor = float(max_size)/len1
        img_out = cv2.resize(img,(int(factor*len2),max_size))
    else:
        factor =float(max_size)/len2
        img_out = cv2.resize(img,(max_size,int(factor*len1)))
    return img_out,factor
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
#    if (iter_num==0):
    kernel=np.array([[0,1,0],[1,1,1],[0,1,0]],np.ubyte)
    j2=cv2.dilate(np.uint8(junctionMap),kernel)
    img_segmentation=img>j2
#    else:
#        img_segmentation=img^junctionMap

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

    total_num_of_branch=0
    for i in region:
        if (i.area<=max_len):
            for j in range(i.coords.shape[0]):
                if (extremityMap[i.coords[j,0],i.coords[j,1]]):
                    img_result+=(img_label==i.label)
                    total_num_of_branch+=1
                    break

    return img_result,total_num_of_branch

def cellAngiogenesis(image_input_path, image_output_path, json_path, add_boarder=True):

#    tStart=time.time()

    img_ori=cv2.imread(image_input_path)
    img_ori_resize,factor=img_resize(img_ori,1024)  #resize

#    plt.figure()
#    io.imshow(img_ori_resize)
#    io.show()

    #如果先resize再取gray~效果會比較差
    img_gray=cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

    #######################for validation
#    mask1= np.where(img_ori[:,:,0]>200)
#    mask2= np.where(img_ori[:,:,1]<50)
#    img_gray1=np.zeros_like(img_ori[:,:,0])
#    img_gray2=np.zeros_like(img_ori[:,:,0])
#    img_gray1[mask1]=1
#    img_gray2[mask2]=1
#    img_gray=np.logical_and(img_gray1,img_gray2)
#    img_gray = cv2.erode(np.uint8(img_gray),np.uint8(m.sedisk(1)))
##    plt.figure()
##    io.imshow(img_gray)
##    io.show()
#    img_gray=np.uint8(img_gray)
#    img_gray*=255

    ###################################

    img_gray,factor=img_resize(img_gray,1024)  #resize

    #20161101
    img_gray=contrast_saturated(img_gray)
#    img_gray = cv2.GaussianBlur(img_gray,(5,5),0)

#    img_gray_mean=np.mean(img_gray)
#    img_gray_var=np.var(img_gray)
#    print np.mean(img_gray)
#    print np.var(img_gray)
#
#    img_gray=np.uint32(img_gray)
#
#    img_gray=150+np.sqrt(6000.0/img_gray_var)*(img_gray-img_gray_mean)
#
#    mask1=np.where(img_gray>255)
#    mask2=np.where(img_gray<0)
#    img_gray[mask1]=255
#    img_gray[mask2]=0
#    img_gray=np.uint8(img_gray)
#
#    plt.figure()
#    io.imshow(img_gray)
#    io.show()
#
#    print np.mean(img_gray)
#    print np.var(img_gray)

#    img_thresh=feature.canny(img_gray) #bool output
#    img_thresh=np.uint8(img_thresh)
#
#    plt.figure()
#    io.imshow(img_thresh*255)
#    io.show()


    #####################################################
    img_prewitt=filters.prewitt(img_gray)    #detect edge
    img_enhance=img_as_ubyte(img_prewitt)
    img_enhance = cv2.GaussianBlur(img_enhance,(5,5),0)
    thresh,img_thresh=cv2.threshold(img_enhance,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_thresh_1=img_enhance>=thresh

    img_sobel=filters.sobel(img_gray)    #detect edge
    img_enhance=img_as_ubyte(img_sobel)
    img_enhance = cv2.GaussianBlur(img_enhance,(5,5),0)
    thresh,img_thresh=cv2.threshold(img_enhance,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_thresh_2=img_enhance>=thresh

    img_roberts=filters.roberts(img_gray)    #detect edge
    img_enhance=img_as_ubyte(img_roberts)
    img_enhance = cv2.GaussianBlur(img_enhance,(5,5),0)
    thresh,img_thresh=cv2.threshold(img_enhance,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_thresh_3=img_enhance>=thresh

    img_thresh_4=feature.canny(img_gray,sigma=2)

    img_thresh=np.uint8(np.logical_or(img_thresh_1,img_thresh_2))
    img_thresh=np.uint8(np.logical_or(img_thresh,img_thresh_3))
    img_thresh=np.uint8(np.logical_or(img_thresh,img_thresh_4))

    img_thresh_ori=np.copy(img_thresh)

#    plt.figure()
#    io.imshow(img_thresh_ori*255)
#    io.show()

    img_thresh=np.uint8(morphology.skeletonize(img_thresh))

    element=np.array([[0,1,0],[1,1,1],[0,1,0]],np.ubyte)
    img_thresh = cv2.morphologyEx(img_thresh, cv2.MORPH_CLOSE, element, iterations=10)
    kernel=np.array([[0,0,0],[0,1,0],[0,0,0]],np.ubyte)
    img_thresh = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, kernel, iterations=1)

#    plt.figure()
#    io.imshow(img_thresh*255)
#    io.show()
    ######################################################

    if (min(img_thresh.shape)>1000):
        kernel=np.array(m.sedisk(7),np.ubyte)
    elif (min(img_thresh.shape)>500):
        kernel=np.array(m.sedisk(6),np.ubyte)
    else:
        kernel=np.array(m.sedisk(5),np.ubyte)
    img_dilation = np.array(cv2.dilate(img_thresh,kernel),np.bool)

    if (min(img_thresh.shape)>500):
        kernel=np.array([[1,1,1],[1,1,1],[1,1,1]],np.ubyte)
    else:
        kernel=np.array([[0,0,0],[0,1,0],[0,0,0]],np.ubyte)

    img_dilation = cv2.morphologyEx(np.uint8(img_dilation), cv2.MORPH_OPEN, kernel,iterations=3)
    img_dilation = cv2.morphologyEx(np.uint8(img_dilation), cv2.MORPH_CLOSE, kernel,iterations=3)

    img_dilation = np.array(cv2.erode(img_dilation,kernel),np.bool)

    if (add_boarder):
        board_value=img_dilation.max()
        img_dilation[0,:]=board_value
        img_dilation[-1,:]=board_value
        img_dilation[:,0]=board_value
        img_dilation[:,-1]=board_value

#    plt.figure()
#    io.imshow(img_dilation)
#    io.show()

    img_skeleton=morphology.skeletonize(img_dilation)
#
#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()

    size_thresh=2500
    ######################################################################
    for i in range(2):
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
#        plt.figure()
#        io.imshow(img_region*255)
#        io.show()

        #######################remove extra loop
        if (np.sum(img_region)):
            extra_loop=np.zeros_like(img_region)
            ret, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_region)
            for i in range(1,ret):
                mask=np.where(img_label==i)
#                if float(np.sum(img_dilation[mask]))/len(mask[0])>0.8:
                if float(np.sum(img_thresh_ori[mask]))/len(mask[0])>0.5:
                    extra_loop[mask]=1
            extra_loop = cv2.dilate(extra_loop,np.uint8(m.sedisk(1)))
            img_skeleton=np.logical_or(img_skeleton,extra_loop)
#            plt.figure()
#            io.imshow(img_skeleton)
#            io.show()
            img_skeleton=morphology.skeletonize(img_skeleton)
            if (ret>50 or (np.mean(stats[1:,4])/img_region.size)<0.02):
                size_thresh=1600
#        plt.figure()
#        io.imshow(img_skeleton)
#        io.show()
    #################auto find a small hole size for eliminate
#    if (np.sum(img_region)):
#        ret, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_region)
#        hole_size=stats[1:,4].copy()
#        hole_size.sort()
#
#        gap=0
#        index=0
#
#        if float(hole_size[-1])/img_fill_holes.size<0.005: #the area of maximum hole still too small, therefore remove all holes
#            size_thresh=hole_size[-1]+1000
#        else:
#            #20160805 add area threshold upper bound and lower bound
#            area_thresh_lowbound=(img_ori_resize.shape[0]/30)*(img_ori_resize.shape[1]/30)
#            area_thresh_upbound=(img_ori_resize.shape[0]/15)*(img_ori_resize.shape[1]/15)
#
#            for i in range(np.size(hole_size)-2):
#                 if ((float(hole_size[i+1])-hole_size[i])/hole_size[i]>gap and hole_size[i+1]>area_thresh_lowbound and hole_size[i+1]<area_thresh_upbound):
#                    gap=(float(hole_size[i+1])-hole_size[i])/hole_size[i]
#                    index=i+1
#                    if (gap>0.2):
#                        break
#            if(index<(np.size(hole_size)-3) and hole_size[i+1]>area_thresh_lowbound and hole_size[i+1]<area_thresh_upbound):
#                size_thresh=hole_size[index]
#            else:
#                size_thresh=area_thresh_lowbound
#        print(size_thresh,index,np.size(hole_size))
#        for i in range(len(hole_size)):
#            print hole_size[i]

    ####################################################################
#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()

    img_remove_small_hole=morphology.remove_small_holes(img_skeleton,min_size=size_thresh)
#    plt.figure()
#    io.imshow(img_remove_small_hole)
#    io.show()

    img_skeleton=morphology.skeletonize(img_remove_small_hole) #remove small hole by skeleton
#    plt.figure()
#    io.imshow(img_skeleton)
#    io.show()

    for i in range(2):
        isolatedPoints=findIsolatedPoint(img_skeleton)
        img_remove_isolatedPoints = img_skeleton^isolatedPoints
        extremityMap=findExtremities(img_remove_isolatedPoints)
        junctionMap=findJunctions(img_remove_isolatedPoints)
        small_branch=deleteBranch(img_remove_isolatedPoints,extremityMap,junctionMap,20)
        img_remove_small_branch=img_remove_isolatedPoints^small_branch
#        plt.figure()
#        io.imshow(img_remove_small_branch)
#        io.show()
        ret,img_label=cv2.connectedComponents(np.uint8(img_remove_small_branch))
        img_remove_small_object=morphology.remove_small_objects(img_label,min_size=10)
        img_remove_small_object=img_remove_small_object>0
#        plt.figure()
#        io.imshow(img_remove_small_object)
#        io.show()
        img_skeleton = m.thin(img_remove_small_object, m.endpoints('homotopic'),1)
#    plt.figure()
#    io.imshow(np.copy(img_skeleton))
#    io.show()
#
#    kernel=np.array(m.sedisk(7),np.ubyte)
    if (min(img_thresh.shape)>1000):
        kernel=np.array(m.sedisk(7),np.ubyte)
    elif (min(img_thresh.shape)>500):
        kernel=np.array(m.sedisk(6),np.ubyte)
    else:
        kernel=np.array(m.sedisk(5),np.ubyte)
    img_final = cv2.dilate(np.uint8(img_skeleton),kernel)
    img_final=morphology.skeletonize(img_final)
#    plt.figure()
#    io.imshow(np.copy(img_final))
#    io.show()

    img_remove_small_hole=morphology.remove_small_holes(img_final,min_size=size_thresh)
    img_final=morphology.skeletonize(img_remove_small_hole) #remove small hole by skeleton

#    plt.figure()
#    io.imshow(np.copy(img_final))
#    io.show()

    isolatedPoints=findIsolatedPoint(img_final)
    img_final = img_final^isolatedPoints
    extremityMap=findExtremities(img_final)
    junctionMap=findJunctions(img_final)

    ###################################connect broken line
    allBranch,total_num_of_branch=detectAllBranch(img_final,extremityMap,junctionMap)
    ret, img_label, stats, centroids =cv2.connectedComponentsWithStats(np.uint8(allBranch))
    mask=np.where(extremityMap>0)
    extremityMap2=np.zeros_like(extremityMap)
    for i in range(len(mask[0])):
        for j in range(i):
            if (stats[img_label[mask[0][i],mask[1][i]],4]>30 and stats[img_label[mask[0][j],mask[1][j]],4]>30):
                if np.sqrt(np.power((mask[0][i]-mask[0][j]),2)+np.power((mask[1][i]-mask[1][j]),2))<50:
                    if  (img_label[mask[0][i],mask[1][i]] != img_label[mask[0][j],mask[1][j]]): #不是同一個label,沒有連結在一起
                        inx1=np.where(img_label==img_label[mask[0][i],mask[1][i]])
                        endpoint_inx1=np.where(inx1[0]-mask[0][i]==3)
                        if np.size(endpoint_inx1)==0:
                            endpoint_inx1=np.where(inx1[0]-mask[0][i]==-3)
                        if np.size(endpoint_inx1)==0:
                            endpoint_inx1=np.where(inx1[1]-mask[1][i]==3)
                        if np.size(endpoint_inx1)==0:
                            endpoint_inx1=np.where(inx1[1]-mask[1][i]==-3)

                        inx2=np.where(img_label==img_label[mask[0][j],mask[1][j]])
                        endpoint_inx2=np.where(inx2[0]-mask[0][j]==3)
                        if np.size(endpoint_inx2)==0:
                            endpoint_inx2=np.where(inx2[0]-mask[0][j]==-3)
                        if np.size(endpoint_inx2)==0:
                            endpoint_inx2=np.where(inx2[1]-mask[1][j]==3)
                        if np.size(endpoint_inx2)==0:
                            endpoint_inx2=np.where(inx2[1]-mask[1][j]==-3)

                        if (np.size(endpoint_inx1)==0 or np.size(endpoint_inx2)==0):
                            continue

                        startpoint1=[mask[0][i],mask[1][i]]
                        endpoint1=[inx1[0][endpoint_inx1[0][0]],inx1[1][endpoint_inx1[0][0]]]
                        startpoint2=[mask[0][j],mask[1][j]]
                        endpoint2=[inx2[0][endpoint_inx2[0][0]],inx2[1][endpoint_inx2[0][0]]]
                        v1=[endpoint1[0]-startpoint1[0],endpoint1[1]-startpoint1[1]]
                        v2=[endpoint2[0]-startpoint2[0],endpoint2[1]-startpoint2[1]]
                        v3=[startpoint1[0]-startpoint2[0],startpoint1[1]-startpoint2[1]]
                        theta_1=np.arccos(np.dot(v1,v2)/(np.sqrt(np.dot(v1,v1))*np.sqrt(np.dot(v2,v2))))*180/np.pi
                        theta_2=np.arccos(np.dot(v1,v3)/(np.sqrt(np.dot(v1,v1))*np.sqrt(np.dot(v3,v3))))*180/np.pi
#                        print (theta_1,theta_2)
                        if (theta_1>90 and theta_2<90):
                            a=float((mask[1][i]-mask[1][j]))/(mask[0][i]-mask[0][j])
                            if (mask[0][j]!=mask[0][i]):
                                for t in range(mask[0][i],mask[0][j],np.sign(mask[0][j]-mask[0][i])):
                                    x=t-mask[0][i]
                                    y=int(a*x+mask[1][i])
                                    img_final[t,y]=1
                                    extremityMap2[t,y]=1
                            else:
                                img_final[mask[0][i],range(mask[1][i],mask[1][j],np.sign(mask[1][j]-mask[1][i]))]=1
                            img_final[mask[0][i],mask[1][i]]=1
                            extremityMap2[mask[0][i],mask[1][i]]=1

#    plt.figure()
#    io.imshow(allBranch+m.dilate(extremityMap, m.sedisk(2))+m.dilate(extremityMap2, m.sedisk(3)))
#    io.show()

#    plt.figure()
#    io.imshow(np.copy(img_final+m.dilate(extremityMap2, m.sedisk(4))))
#    io.show()

    img_final = cv2.dilate(np.uint8(img_final),kernel)
    img_final=morphology.skeletonize(img_final)

    img_remove_small_hole=morphology.remove_small_holes(img_final,min_size=size_thresh)
    img_final=morphology.skeletonize(img_remove_small_hole)

    extremityMap=findExtremities(img_final)
    junctionMap=findJunctions(img_final)
    ###########################################

#    plt.figure()
#    io.imshow(m.dilate(img_final, m.sedisk(2)))
#    io.show()
#    plt.figure()
#    io.imshow(m.dilate(extremityMap, m.sedisk(2)))
#    io.show()
#    plt.figure()
#    io.imshow(np.logical_or(img_final,cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(3)))))
#    io.show()
    #################prune tree
    small_branch=deleteBranch(img_final,extremityMap,junctionMap,20)
#    tmp_count=0
    while(np.sum(small_branch)>0):
#        tmp_count+=1
#        print tmp_count
        img_final=img_final^small_branch
        img_final = m.thin(img_final, m.endpoints('homotopic'),1)
        isolatedPoints=findIsolatedPoint(img_final)
        img_final = img_final^isolatedPoints
        extremityMap=findExtremities(img_final)
        junctionMap=findJunctions(img_final)
        small_branch=deleteBranch(img_final,extremityMap,junctionMap,20)
#        plt.figure()
#        io.imshow(np.copy(img_final))
#        io.show()
    img_final = m.thin(img_final, m.endpoints('homotopic'),5)
    ##################################
    ret, img_label, stats, centroids =cv2.connectedComponentsWithStats(np.uint8(img_final))
    for i in range(1,ret):
        if stats[i,4]<100:  #對於小於門檻值的object就remove
            mask=np.where(img_label==i)
            img_final[mask]=0

#    plt.figure()
#    io.imshow(np.copy(img_final))
#    io.show()

    extremityMap=findExtremities(img_final)
#    plt.figure()
#    io.imshow(m.dilate(extremityMap, m.sedisk(2)))
#    io.show()
    junctionMap=findJunctions(img_final)
    allBranch,total_num_of_branch=detectAllBranch(img_final,extremityMap,junctionMap)

#    plt.figure()
#    io.imshow(allBranch+m.dilate(extremityMap, m.sedisk(2)))
#    io.show()

    # dilate to merge nearby hits
    junctionMap = cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(10)))
    # locate centroids
    junctionMap = m.blob(m.label(junctionMap), 'centroid')
    ret_junction, img_label= cv2.connectedComponents(np.uint8(junctionMap))
    num_junction=ret_junction-1
    junctionMap = cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(5)))

    img_final^=allBranch
    allSegment=img_final>junctionMap
    ##############################################remove board segment
    if (add_boarder):
#        ret_seg, img_label_seg, stats_seg, centroids_seg = cv2.connectedComponentsWithStats(np.uint8(allSegment))
#        e1=(np.unique(img_label_seg[3,:]))
#        e2=(np.unique(img_label_seg[-4,:]))
#        e3=(np.unique(img_label_seg[:,3]))
#        e4=(np.unique(img_label_seg[:,-4]))
#        board_label=np.unique(np.concatenate((e1,e2,e3,e4)))
#        for i in board_label:
#            mask=np.where(img_label_seg==i)
#            allSegment[mask]=0
        allSegment[0:10,:]=0
        allSegment[-10:,:]=0
        allSegment[:,0:10]=0
        allSegment[:,-10:]=0
    ###############################################

    img_fill_holes = scipy.ndimage.binary_fill_holes(img_final)
    img_region=img_fill_holes^img_final
    #reduce the region size in order to seperate each region by ersoion
    img_region=cv2.erode(np.uint8(img_region),np.uint8(m.sedisk(1)))
#    plt.figure()
#    io.imshow(img_region)
#    io.show()
    ##################################
    img_fill_holes_tmp=np.zeros_like(img_region,np.uint8)
    if (add_boarder):
        ret_mesh, img_label_mesh, stats_mesh, centroids_mesh = cv2.connectedComponentsWithStats(img_region)
        e1=(np.unique(img_label_mesh[10,10:-10]))
        e2=(np.unique(img_label_mesh[-10,10:-10]))
        e3=(np.unique(img_label_mesh[10:-10,10]))
        e4=(np.unique(img_label_mesh[10:-10,-10]))
        board_label=np.unique(np.concatenate((e1,e2,e3,e4)))
        inter_label=range(1,ret_mesh)
        inter_label=np.setdiff1d(inter_label,board_label)
        #################################################
        if(len(inter_label)>0):
            mean_inter_label_area=np.mean(stats_mesh[inter_label,4])
            inter_label_tmp=np.copy(inter_label)
            for i in inter_label_tmp:
                if (stats_mesh[i,4])<mean_inter_label_area/20:
                    inter_label=np.setdiff1d(inter_label,i)
                    mask=np.where(img_label_mesh==i)
                    img_region[mask]=0
                    img_fill_holes_tmp[mask]=1
        #################################################
        if(len(inter_label)>0):
            mean_inter_label_area=np.mean(stats_mesh[inter_label,4])
            max_inter_label_area=np.max(stats_mesh[inter_label,4])
            min_inter_label_area=np.min(stats_mesh[inter_label,4])
        else:
            mean_inter_label_area=0
            max_inter_label_area=0
            min_inter_label_area=0

    #    print inter_label
    #    print max_inter_label_area
        ###################################
#        img_region_tmp=np.copy(img_region)
#        for i in board_label:
#            if (i!=0):
#                mask=np.where(img_label_mesh==i)
#                img_region_tmp[mask]=128
#        for i in inter_label:
#            if (i!=0):
#                mask=np.where(img_label_mesh==i)
#                img_region_tmp[mask]=255
#        plt.figure()
#        io.imshow(img_region_tmp)
#        io.show()
        ###################################
        area_factor=2
        if float(max_inter_label_area)/img_region.size>0.1:
            area_factor=1.5
#        print float(max_inter_label_area)/img_region.size
        for i in board_label:
            if i>0: #remove太大或太小的邊緣loop
#                if (stats_mesh[i,4]>mean_inter_label_area*2 or stats_mesh[i,4]<mean_inter_label_area/2):
#                if (stats_mesh[i,4]>max_inter_label_area*1.5 or stats_mesh[i,4]<min_inter_label_area):
                if (stats_mesh[i,4]>max_inter_label_area*area_factor and float(stats_mesh[i,4])/img_region.size>0.15):
                    mask=np.where(img_label_mesh==i)
                    img_region[mask]=0
    else:
        ret_mesh, img_label_mesh, stats_mesh, centroids_mesh = cv2.connectedComponentsWithStats(img_region)
        if(ret_mesh>1):
            mean_inter_label_area=np.mean(stats_mesh[1:,4])
            for i in range(1,ret_mesh):
                if (stats_mesh[i,4])<mean_inter_label_area/20:
                    mask=np.where(img_label_mesh==i)
                    img_region[mask]=0
                    img_fill_holes_tmp[mask]=1
    ##################################
    img_fill_holes_tmp=cv2.dilate(img_fill_holes_tmp,np.uint8(m.sedisk(1)))

    ret_mesh, img_label_mesh, stats_mesh, centroids_mesh = cv2.connectedComponentsWithStats(img_region)
    num_mesh=ret_mesh-1
    tot_mesh_area=np.sum(stats_mesh[1:,4])
    if (num_mesh):
        mean_mesh_area=float(tot_mesh_area)/num_mesh
        std_mesh_area=np.std(stats_mesh[1:,4])
    else:
        mean_mesh_area=0
        std_mesh_area=0
#    plt.figure()
#    io.imshow(img_region*255)
#    io.show()

    img_dist=mahotas.distance(img_label_mesh)
    img_perimeter=(img_dist==1)
    ret_perimeter, img_label_perimeter, stats_perimeter, centroids_perimeter = cv2.connectedComponentsWithStats(np.uint8(img_perimeter))
    tot_mesh_perimeter=np.sum(stats_perimeter[1:,4])
    if (num_mesh):
        mean_mesh_perimeter=float(tot_mesh_perimeter)/num_mesh
        std_mesh_perimeter=np.std(stats_perimeter[1:,4])
    else:
        mean_mesh_perimeter=0
        std_mesh_perimeter=0
#    plt.figure()
#    io.imshow(img_perimeter)
#    io.show()

    img_label_color=color.label2rgb(img_label_mesh,bg_label=0)
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

    ret_branch, img_label_branch, stats_branch, centroids_branch = cv2.connectedComponentsWithStats(np.uint8(allBranch))
    for i in range(1,ret_branch):
        if stats_branch[i,4]<50:  #對於小於門檻值的object就remove
            mask=np.where(img_label_branch==i)
            allBranch[mask]=0

    img_final2=allSegment+allBranch+junctionMap+extremityMap+img_fill_holes_tmp
    mask=np.where(img_final2>0)
    img_final2=np.zeros_like(img_final2,np.bool)
    img_final2[mask]=1
    img_final2=morphology.skeletonize(img_final2)

    ret, img_label, stats, centroids =cv2.connectedComponentsWithStats(np.uint8(img_final2))
    for i in range(1,ret):
        if stats[i,4]<100:  #對於小於門檻值的object就remove
            mask=np.where(img_label==i)
            img_final2[mask]=0

#    plt.figure()
#    io.imshow(m.dilate(np.copy(img_final2), m.sedisk(2)))
#    io.show()

    extremityMap=findExtremities(img_final2)
    junctionMap=findJunctions(img_final2)

    small_branch=deleteBranch(img_final2,extremityMap,junctionMap,20)
    while(np.sum(small_branch)>0):
        img_final2=img_final2^small_branch
        img_final2 = m.thin(img_final2, m.endpoints('homotopic'),1)
        isolatedPoints=findIsolatedPoint(img_final2)
        img_final2 = img_final2^isolatedPoints
        extremityMap=findExtremities(img_final2)
        junctionMap=findJunctions(img_final2)
        small_branch=deleteBranch(img_final2,extremityMap,junctionMap,20)
    img_final2 = m.thin(img_final2, m.endpoints('homotopic'),5)
    extremityMap=findExtremities(img_final2)
    junctionMap=findJunctions(img_final2)

    allBranch,total_num_of_branch=detectAllBranch(img_final2,extremityMap,junctionMap)

    # dilate to merge nearby hits
    junctionMap = cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(10)))
    # locate centroids
    junctionMap = m.blob(m.label(junctionMap), 'centroid')
#        plt.figure()
#        io.imshow(m.dilate(junctionMap, m.sedisk(2)))
#        io.show()
    ret_junction, img_label= cv2.connectedComponents(np.uint8(junctionMap))
    num_junction=ret_junction-1
    junctionMap = cv2.dilate(np.uint8(junctionMap), np.uint8(m.sedisk(5)))
    img_final2^=allBranch
    allSegment=img_final2>junctionMap
    ###################################################

#        plt.figure()
#        io.imshow(m.dilate(allBranch, m.sedisk(2)))
#        io.show()

#        plt.figure()
#        io.imshow(m.dilate(allSegment, m.sedisk(2)))
#        io.show()

    ret_seg, img_label_seg, stats_seg, centroids_seg = cv2.connectedComponentsWithStats(np.uint8(allSegment))
    total_num_of_seg=ret_seg-1
    tot_seg_len=np.sum(stats_seg[1:,4])
    if (total_num_of_seg):
        mean_seg=float(tot_seg_len)/total_num_of_seg
        std_seg=np.std(stats_seg[1:,4])
    else:
        mean_seg=0
        std_seg=0

#    plt.figure()
#    io.imshow(allSegment)
#    io.show()

    #measurement
    tot_branch_len=allBranch.sum()
    ret_branch, img_label_branch, stats_branch, centroids_branch = cv2.connectedComponentsWithStats(np.uint8(allBranch))
    if (total_num_of_branch):
        mean_branch=float(tot_branch_len)/total_num_of_branch
        std_branch=np.std(stats_branch[1:,4])
    else:
        mean_branch=0
        std_branch=0

    tot_len=tot_branch_len+tot_seg_len
    #######################################################

    allSegment = cv2.dilate(np.uint8(allSegment),np.uint8(m.sedisk(1)))
    mask=np.where(allSegment>0)
    img_ori_resize[mask]=[0,0,255]

#    plt.figure()
#    io.imshow(img_final)
#    io.show()

    allBranch = cv2.dilate(np.uint8(allBranch),np.uint8(m.sedisk(1)))
    mask=np.where(allBranch>0)
    img_ori_resize[mask]=[255,255,0]

#    plt.figure()
#    io.imshow(allBranch)
#    io.show()

    mask=np.where(junctionMap>0)
    img_ori_resize[mask]=[255,255,255]

    ret_extremity, img_label= cv2.connectedComponents(np.uint8(extremityMap))
    num_extremity=ret_extremity-1
    extremityMap = cv2.dilate(np.uint8(extremityMap), np.uint8(m.sedisk(5)))
    mask=np.where(extremityMap>0)
    img_ori_resize[mask]=[0,255,255]

    font =cv2.FONT_HERSHEY_SIMPLEX
    for i in range(1,ret_mesh):
        cv2.putText(img_ori_resize,str(i),(int(centroids_mesh[i,0]),int(centroids_mesh[i,1])), font,1,(255,0,0),2)

    img_ori_resize = cv2.resize(img_ori_resize,(img_ori.shape[1],img_ori.shape[0]))
    cv2.imwrite(image_output_path,img_ori_resize)

    out_file = open(json_path,"w")
    factor=1./factor
    angiogenesis_result = {
                           '#Extremity':num_extremity,'#Junction':num_junction,
                           'Connectivity':total_num_of_seg*2+total_num_of_branch,'Tot. network length':int(tot_len*factor),
                           '#Branch':total_num_of_branch,'Tot. branch length':int(tot_branch_len*factor),'Mean branch length':round(mean_branch*factor,3),'Std. branch length':round(std_branch*factor,3),
                           '#Segment':total_num_of_seg,'Tot. segment length':int(tot_seg_len*factor),'Mean segment length':round(mean_seg*factor,3),'Std. segment length':round(std_seg*factor,3),
                           '#Mesh':num_mesh,'Tot. mesh area':int(tot_mesh_area*factor*factor),'Mean mesh area':round(mean_mesh_area*factor*factor,3),'Std. mesh area':round(std_mesh_area*factor*factor,3),
                           'Tot. mesh perimeter':int(tot_mesh_perimeter*factor),'Mean mesh perimeter':round(mean_mesh_perimeter*factor,3),'Std. mesh perimeter':round(std_mesh_perimeter*factor,3)
                           }
    json.dump(angiogenesis_result,out_file)
    out_file.close()
#
##    tEnd=time.time()
##
##    print ("It costs %f sec",tEnd-tStart)

    return #num_mesh, num_junction, total_num_of_seg*2+total_num_of_branch
###############################################################################

##img_input_path=u'C:\\Users\\Aaron.Lin\\Desktop\\demo image\\cellA'
##img_input_path=u"D:\Aaron workspace\Aaron\CellAngiogenesis_Project\Image data\\CellQA_images_all"
#img_input_path=u"D:\\Aaron workspace\\Aaron\\Benchmark\\HiDOS  validation\\Tube formation\\all"
##img_input_path=u"D:\\Aaron workspace\\Aaron\\Benchmark\\HiDOS  validation\\Tube formation\\1st\\NC"
#img_output_path=u"D:\\Aaron workspace\\Aaron\\CellAngiogenesis_Project\\output_test"
##img_input_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\CellT\\Angiogenesis\\label image'
##img_output_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\CellT\\Angiogenesis\\validation_result'
#file_list = listdir(img_input_path)
#result_1=np.zeros((36,3))
#result_2=np.zeros((36,3))
#count=0
#for filename in file_list:
#    if (filename[0]!='.'):
#        print('Cell angiogenesis analyzing for %s'%filename)
#        Img_filename=img_input_path+'\\'+filename
#        ########################
##        inx=Img_filename.rfind('_')
##        ans_tmp=Img_filename[inx+1:inx+9]
##        result_2[count,0]=int(ans_tmp[0:2])
##        result_2[count,1]=int(ans_tmp[3:5])
##        result_2[count,2]=int(ans_tmp[6:8])
#        ########################
#        Img_output_filename=img_output_path+'\\'+filename
#        inx=Img_output_filename.rfind('.')
#        json_filename=Img_output_filename[0:inx]+'.json'
#        result_1[count]=cellAngiogenesis(Img_filename,Img_output_filename,json_filename,add_boarder=True)
#
#        count+=1





#image_path = u"D:\Aaron workspace\Aaron\CellAngiogenesis_Project\Image data\\CellQA_images_all\\c4ce2e442a616056a4c3edce5f021109_uploaded.PNG"
#image_path = u"D:\\Aaron workspace\\Aaron\\Benchmark\\HiDOS  validation\\Tube formation\\all\\IMG_9873_38-43-74.JPG"
#image_output_path = u"D:\Aaron workspace\Aaron\CellAngiogenesis_Project\output_test\\result.jpg"
#json_path = u"D:\Aaron workspace\Aaron\CellAngiogenesis_Project\output_test\\result.json"
#cellAngiogenesis(image_path,image_output_path,json_path,add_boarder=True)



###################for validation##############################
#from scipy import stats
#measure='Tot. network length'
#img_input_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\CellT\\raw image_validation_result\\ind data'
#file_list = listdir(img_input_path)
#result_1=np.empty(1)
#for filename in file_list:
#    if (filename[-4:]=='json'):
#        Img_filename=img_input_path+'\\'+filename
#        with open(Img_filename) as json_file:
#            json_data = json.load(json_file)
#        result_1=np.append(result_1,[json_data.get(measure)],axis=0)
#
#img_input_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\CellT\\Angiogenesis\\validation_result\\ind data'
#file_list = listdir(img_input_path)
#result_2=np.empty(1)
#for filename in file_list:
#    if (filename[-4:]=='json'):
#        Img_filename=img_input_path+'\\'+filename
#        with open(Img_filename) as json_file:
#            json_data = json.load(json_file)
#        result_2=np.append(result_2,[json_data.get(measure)],axis=0)
#
#img_input_path=u'D:\\Aaron workspace\\Aaron\\Benchmark\\CellT\\CellT_finished\\validation_result\\ind data'
#file_list = listdir(img_input_path)
#result_3=np.empty(1)
#for filename in file_list:
#    if (filename[-4:]=='json'):
#        Img_filename=img_input_path+'\\'+filename
#        with open(Img_filename) as json_file:
#            json_data = json.load(json_file)
#        result_3=np.append(result_3,[json_data.get(measure)],axis=0)



############################################################################################################################################

#nc_inx_1st=[3,4,5]
#pc_inx_1st=[0,1,2]
#ta1_inx_1st=[6,7,8]
#ta2_inx_1st=[21,22,23]
#nc_inx_2nd=[12,13,14]
#pc_inx_2nd=[9,10,11]
#ta1_inx_2nd=[15,16,17]
#ta2_inx_2nd=[18,19,20]
#nc_inx_3rd=[27,28,29]
#pc_inx_3rd=[24,25,26]
#ta1_inx_3rd=[30,31,32]
#ta2_inx_3rd=[33,34,35]
#inx_1st=[0,1,2,3,4,5,6,7,8,21,22,23]
#inx_2nd=[12,13,14,9,10,11,15,16,17,18,19,20]
#inx_3rd=[24,25,26,27,28,29,30,31,32,33,34,35]
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_1st,0],result_2[inx_1st,0])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_1st,0],result_2[nc_inx_1st,0],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_1st,0],result_2[pc_inx_1st,0],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_1st,0],result_2[ta1_inx_1st,0],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_1st,0],result_2[ta2_inx_1st,0],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_1st,0])-1),int(max(result_1[inx_1st,0]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(-4, max(result_2[inx_1st,0])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(-4,max(result_2[inx_1st,0])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('loop for 1st trial')
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_2nd,0],result_2[inx_2nd,0])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_2nd,0],result_2[nc_inx_2nd,0],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_1st,0],result_2[pc_inx_2nd,0],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_2nd,0],result_2[ta1_inx_2nd,0],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_2nd,0],result_2[ta2_inx_2nd,0],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_2nd,0])-1),int(max(result_1[inx_2nd,0]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(-4, max(result_2[inx_2nd,0])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(-4,max(result_2[inx_2nd,0])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('loop for 2nd trial')
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_3rd,0],result_2[inx_3rd,0])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_3rd,0],result_2[nc_inx_3rd,0],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_3rd,0],result_2[pc_inx_3rd,0],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_3rd,0],result_2[ta1_inx_3rd,0],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_3rd,0],result_2[ta2_inx_3rd,0],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_3rd,0])-1),int(max(result_1[inx_3rd,0]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(-4, max(result_2[inx_3rd,0])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(-4,max(result_2[inx_3rd,0])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('loop for 3rd trial')
#
#
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_1st,1],result_2[inx_1st,1])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_1st,1],result_2[nc_inx_1st,1],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_1st,1],result_2[pc_inx_1st,1],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_1st,1],result_2[ta1_inx_1st,1],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_1st,1],result_2[ta2_inx_1st,1],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_1st,1])-1),int(max(result_1[inx_1st,1]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(1, max(result_2[inx_1st,1])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(1,max(result_2[inx_1st,1])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('node for 1st trial')
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_2nd,1],result_2[inx_2nd,1])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_2nd,1],result_2[nc_inx_2nd,1],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_1st,1],result_2[pc_inx_2nd,1],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_2nd,1],result_2[ta1_inx_2nd,1],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_2nd,1],result_2[ta2_inx_2nd,1],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_2nd,1])-1),int(max(result_1[inx_2nd,1]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(1, max(result_2[inx_2nd,1])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(1,max(result_2[inx_2nd,1])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('node for 2nd trial')
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_3rd,1],result_2[inx_3rd,1])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_3rd,1],result_2[nc_inx_3rd,1],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_3rd,1],result_2[pc_inx_3rd,1],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_3rd,1],result_2[ta1_inx_3rd,1],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_3rd,1],result_2[ta2_inx_3rd,1],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_3rd,1])-1),int(max(result_1[inx_3rd,1]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(-4, max(result_2[inx_3rd,1])*0.8,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(-4,max(result_2[inx_3rd,1])*0.75,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('node for 3rd trial')
#
#
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_1st,2],result_2[inx_1st,2])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_1st,2],result_2[nc_inx_1st,2],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_1st,2],result_2[pc_inx_1st,2],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_1st,2],result_2[ta1_inx_1st,2],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_1st,2],result_2[ta2_inx_1st,2],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_1st,2])-1),int(max(result_1[inx_1st,2]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(1, max(result_2[inx_1st,2])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(1,max(result_2[inx_1st,2])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('connectivity for 1st trial')
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_2nd,2],result_2[inx_2nd,2])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_2nd,2],result_2[nc_inx_2nd,2],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_1st,2],result_2[pc_inx_2nd,2],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_2nd,2],result_2[ta1_inx_2nd,2],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_2nd,2],result_2[ta2_inx_2nd,2],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_2nd,2])-1),int(max(result_1[inx_2nd,2]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(1, max(result_2[inx_2nd,2])*0.85,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(1,max(result_2[inx_2nd,2])*0.8,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('connectivity for 2nd trial')
#
#plt.figure()
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[inx_3rd,2],result_2[inx_3rd,2])
#print 'p_value=%f'%p_value
#NC=plt.scatter(result_1[nc_inx_3rd,2],result_2[nc_inx_3rd,2],color='blue',s=50,marker='*')
#PC=plt.scatter(result_1[pc_inx_3rd,2],result_2[pc_inx_3rd,2],color='black',s=50,marker='*')
#TA1=plt.scatter(result_1[ta1_inx_3rd,2],result_2[ta1_inx_3rd,2],color='magenta',s=50,marker='*')
#TA2=plt.scatter(result_1[ta2_inx_3rd,2],result_2[ta2_inx_3rd,2],color='green',s=50,marker='*')
#plt.legend((NC, PC, TA1, TA2),
#           ('NC', 'PC', 'TA1', 'TA2'),
#           scatterpoints=1,
#           loc='upper left',
#           fontsize=10)
##x=np.array(range(int(min([min(result_1[:,0]),min(result_2[:,0])])),int(max([max(result_1[:,0]),max(result_2[:,0])]))),float)
#x=np.array(range(int(min(result_1[inx_3rd,2])-1),int(max(result_1[inx_3rd,2]))+1),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(1, max(result_2[inx_3rd,2])*0.8,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(1,max(result_2[inx_3rd,2])*0.75,'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title('connectivity for 3rd trial')

#############################################################################################################################################


#
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_1[1:],result_3[1:])
#print 'p_value=%f'%p_value
#plt.figure()
#plt.scatter(result_1[1:],result_3[1:],color='blue')
#x=np.array(range(int(min([min(result_1[1:]),min(result_3[1:])])),int(max([max(result_1[1:]),max(result_3[1:])]))),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('CellT',fontsize=14)
#plt.ylabel('Ground truth(expert2)',fontsize=14)
#plt.text(int(max(result_1[1:])*0.05), int(max(result_3[1:])*0.9),('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(int(max(result_1[1:])*0.05),int(max(result_3[1:])*0.8),'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title(measure)
#
#slope, intercept, r_value, p_value, std_err = stats.linregress(result_2[1:],result_3[1:])
#plt.figure()
#plt.scatter(result_2[1:],result_3[1:],color='blue')
#x=np.array(range(int(min([min(result_2[1:]),min(result_3[1:])])),int(max([max(result_2[1:]),max(result_3[1:])]))),float)
#y=intercept+x*slope
#plt.plot(x,y,color='r',linewidth=3)
##plt.xlim([0,100])
##plt.ylim([0,100])
#plt.xlabel('Ground truth(expert1)',fontsize=14)
#plt.ylabel('Ground truth(expert2)',fontsize=14)
#plt.text(int(max(result_2[1:])*0.05), int(max(result_3[1:])*0.9),('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(int(max(result_2[1:])*0.05),int(max(result_3[1:])*0.8),'correlation coefficient=%f'%r_value,fontsize=14)
#plt.title(measure)








