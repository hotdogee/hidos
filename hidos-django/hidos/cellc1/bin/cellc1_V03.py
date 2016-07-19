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
#from os import listdir
#import matplotlib.pyplot as plt
#from skimage import io

version = '0.3'

###############################################################################


def img_resize(img, max_size):
    len1 = img.shape[0]
    len2 = img.shape[1]

    if(len1 < max_size and len2 < max_size):
        return img

    if (len1 >= len2):
        factor = float(max_size) / len1
        img_out = cv2.resize(img, (int(factor * len2), max_size))
    else:
        factor = float(max_size) / len2
        img_out = cv2.resize(img, (max_size, int(factor * len1)))
    return img_out
###############################################################################


def cellCount_singleTask(task_record):

    max_size = 1024
    # load image
    img_ori = cv2.imread(task_record.uploaded_image.path)
    img_ori_resize = cv2.resize(img_ori, tuple(
        [max_size * d / max(img_ori.shape[:2]) for d in img_ori.shape[1::-1]]))

    # automatically determine using which layer to analyze
    otsu_all = np.empty_like(img_ori_resize)
    ret_all = np.array([0, 0, 0])
    tmp_sum = np.array([0, 0, 0])
    for i in range(3):
        ret_all[i], otsu_all[:, :, i] = cv2.threshold(
            img_ori_resize[:, :, i], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        tmp_sum[i] = otsu_all[:, :, i].sum()

    tmp_sum /= (tmp_sum.max() / 4)  # size如果差4倍以上,就不需考慮
    if (np.logical_and(ret_all > 30, tmp_sum > 0).sum() == 0):
        inx = 0
    else:
        inx = (tmp_sum == tmp_sum[np.logical_and(ret_all > 30, tmp_sum > 0)].min(
        )).argmax()  # 二值化門檻值須>20且size需相差4倍以內,滿足這些條件下,選擇size較小的layer
    color_text = np.array([[0, 255, 255], [255, 0, 255], [255, 255, 0]])
    color_edge = np.array([[0, 0, 255], [255, 0, 0], [0, 255, 0]])
    ############################

#    print ret_all
#    print tmp_sum

#    plt.figure()
#    io.imshow(otsu_all[:,:,0])
#    io.show()
#    plt.figure()
#    io.imshow(otsu_all[:,:,1])
#    io.show()
#    plt.figure()
#    io.imshow(otsu_all[:,:,2])
#    io.show()

    # cv2.imshow('image',img_gray)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    img_thresh = otsu_all[:, :, inx]

    kernel = np.ones((2, 2), np.uint8)
    img_thresh = np.uint8(img_thresh)
    img_opening = cv2.morphologyEx(
        img_thresh, cv2.MORPH_OPEN, kernel)  # remove salt

    ret, img_label, stats, centroids = cv2.connectedComponentsWithStats(
        img_opening)
    # stats 1:leftmost coordinate
    # stats 2:topmost coordinate
    # stats 3:horizontal size
    # stats 4:vertical size
    # stats 5:area

    area_list = stats[1:, 4].copy()
    area_list.sort()
    area_mean = round(
        np.mean(area_list[int(len(area_list) * 0.1):int(len(area_list) * 0.9) + 1]))

    # remove small object
    img_prepro2 = remove_small_objects(np.bool_(img_opening), area_mean / 5)
    img_prepro2 = np.uint8(img_prepro2)
    ret, img_label2, stats2, centroids2 = cv2.connectedComponentsWithStats(
        img_prepro2)

    img_dist = mahotas.distance(img_label2)
    img_edge = img_dist == 1

    # TODO: convert this for loop to numpy functions
    for i in range(img_ori_resize.shape[0]):
        for j in range(img_ori_resize.shape[1]):
            if (img_edge[i, j]):
                img_ori_resize[i, j, :] = color_edge[inx, :]

    area_list2 = stats2[1:, 4].copy()
    area_list2.sort()
    if (len(area_list2) < 40):
        area_mean2 = round(
            np.mean(area_list2[int(len(area_list2) * 0.2):int(len(area_list2) * 0.8) + 1]))
    else:
        area_mean2 = round(
            np.mean(area_list2[int(len(area_list2) * 0.3):int(len(area_list2) * 0.7) + 1]))
    cellCount = 0
    out_file = open(json_path, "w")
    # exception
    font = cv2.FONT_HERSHEY_SIMPLEX
    if (np.isnan(area_mean2) or area_mean2 <= 0):
        cellCount_result = {'count': -1}
        cv2.putText(img_ori_resize, 'This image can not be analyzed.',
                    (40, 80), font, 1, (255, 255, 255), 2)
    else:
        for i in range(1, ret):
            tmpCount = (stats2[i, 4] / area_mean2)
            if (tmpCount >= 0.2 and tmpCount < 1):
                cellCount += 1
                cv2.putText(img_ori_resize, '1', (int(centroids2[i, 0]), int(
                    centroids2[i, 1])), font, 1, color_text[inx, :], 1)
            elif (np.floor(tmpCount)):
                if (float((max(stats2[i, 2:4]))) / min(stats2[i, 2:4]) > 1.5):  # 長條形
                    cellSubCount = np.round(tmpCount)
                # 矩形區域面積/實際面積 (值越大表示留白越多)
                elif (stats2[i, 2] * stats[i, 3] / float(stats[i, 4]) > 1.5):
                    cellSubCount = np.round(tmpCount)
                else:
                    cellSubCount = np.floor(tmpCount)
#                cellCount +=np.floor(tmpCount)
                cellCount += cellSubCount
                cv2.putText(img_ori_resize, str(int(cellSubCount)), (int(
                    centroids2[i, 0]), int(centroids2[i, 1])), font, 1, color_text[inx, :], 1)
        cv2.putText(img_ori_resize, 'counts=' + str(int(cellCount)),
                    (40, 80), font, 2, (255, 255, 255), 3)
        cellCount_result = {'count': int(cellCount)}

    img_ori_resize = cv2.resize(
        img_ori_resize, (img_ori.shape[1], img_ori.shape[0]))

    cv2.imwrite(task_record.result_image.path, img_ori_resize)
    cv2.imwrite(task_record.result_display.path, img_ori_resize)

    return cellCount_result

###############################################################################
#img_input_path=u'D:\Aaron workspace\Aaron\CellCount_Project\Image data'
# img_input_path=u'C:\\Users\\Aaron.Lin\\Desktop\\cellC1_issue_image'
#img_output_path=u'D:\Aaron workspace\Aaron\CellCount_Project\\tiff'
#file_list = listdir(img_input_path)
# for filename in file_list:
#    if (filename[0]!='.'):
#        print('Cell count analyzing for %s'%filename)
#        Img_filename=img_input_path+'\\'+filename
#        Img_output_filename=img_output_path+'\\'+filename
#        inx=Img_output_filename.rfind('.')
#        json_filename=Img_output_filename[0:inx]+'.json'
#        cellCount_singleTask(Img_filename,Img_output_filename,json_filename)


#image_path = "D:\Benchmark\BBBC005_v1_images\BBBC005_v1_images\SIMCEPImages_A24_C100_F1_s19_w1.TIF"
#image_output_path = "D:\Aaron workspace\Aaron\CellCount_Project\\tiff\\result.jpg"
#json_path = "D:\Aaron workspace\Aaron\CellCount_Project\\tiff\\result.json"
# cellCount_singleTask(image_path,image_output_path,json_path)


# for BBBC validation test
#import re
#from scipy import stats
# img_input_path=u'D:\Benchmark\BBBC005_v1_images\BBBC005_v1_images\F1'
# img_output_path=u'D:\Benchmark\BBBC005_v1_images\BBBC005_v1_images\F1_result'
#file_list = listdir(img_input_path)
# img_count=0
# result=np.empty([1,2])
# for filename in file_list:
#    searchObj=re.search('w1',filename)
#    if (filename[0]!='.' and searchObj):
#        tmp=re.search('_C[0-9]+',filename)
#        tmpStr=tmp.group()
#        inx=tmpStr.find('C')
#        ground_truth=int(tmpStr[inx+1:])
#        print('Cell count analyzing for %s'%filename)
#        Img_filename=img_input_path+'\\'+filename
#        Img_output_filename=img_output_path+'\\'+filename
#        inx=Img_output_filename.rfind('.')
#        json_filename=Img_output_filename[0:inx]+'.json'
#        cellCount=cellCount_singleTask(Img_filename,Img_output_filename,json_filename)
#        result=np.append(result,[[ground_truth,cellCount]],axis=0)
#        img_count+=1
#
#slope, intercept, r_value, p_value, std_err = stats.linregress(result[1:,1],result[1:,0])
# plt.figure()
# plt.scatter(result[1:,1],result[1:,0],color='blue')
# x=np.array(range(1,101),float)
# y=intercept+x*slope
# plt.plot(x,y,color='r',linewidth=3)
# plt.xlim([0,100])
# plt.ylim([0,100])
# plt.xlabel('CellC1',fontsize=14)
#plt.ylabel('Ground truth',fontsize=14)
#plt.text(5, 80,('y=%f+%f*x'%(intercept,slope)),fontsize=14)
#plt.text(5,72,'correlation coefficient=%f'%r_value,fontsize=14)
