# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 16:02:34 2016

@author: Aaron.Lin
"""

#get_ipython().magic(u'matplotlib qt')
import cv2
import numpy as np
from skimage import filters
import json
#import time
#from os import listdir

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


def cellConfluence_singleTask(task_record):
    """Benchmark, repeat=5:
    IMG_0159.JPG = 14.129s
    1-3.jpg = 9.7s
    """
    img_ori = cv2.imread(task_record.uploaded_image.path)
    img_ori_resize = img_resize(img_ori, 1024)  # resize

    #
    img_gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)
    img_gray = img_resize(img_gray, 1024)  # resize

    img_prewitt = filters.prewitt(img_gray)  # detect edge
    # enhance
    img_enhance = filters.rank.enhance_contrast(
        img_prewitt, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.ubyte))
    # binarization
    thresh, img_thresh = cv2.threshold(
        img_enhance, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_thresh = img_enhance >= thresh
    img_thresh = np.uint8(img_thresh)
    # print thresh
    if (thresh < 5):
        kernel = np.ones((2, 2), np.uint8)
        img_thresh = cv2.morphologyEx(
            img_thresh, cv2.MORPH_OPEN, kernel)  # remove salt

    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.ubyte)
    img_dilation = cv2.dilate(img_thresh, kernel, iterations=4)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=2)
    img_opening = cv2.morphologyEx(
        img_erosion, cv2.MORPH_OPEN, kernel)  # remove salt

    for i in range(img_opening.shape[0]):
        for j in range(img_opening.shape[1]):
            if (img_opening[i, j]):
                img_ori_resize[i, j, 2] = 200

    # compute confluence
    confluence = 100 * float(img_opening.sum()) / img_opening.size

    # embed result to image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_ori_resize, '{0:.2f}'.format(confluence),
                (40, 80), font, 2, (255, 0, 0), 3)
    img_ori_resize = cv2.resize(
        img_ori_resize, (img_ori.shape[1], img_ori.shape[0]))

    cv2.imwrite(task_record.result_image.path, img_ori_resize)
    cv2.imwrite(task_record.result_display.path, img_ori_resize)

    #out_file = open(json_path,"w")
    #confluence_result = {'confluence': confluence}

    # json.dump(confluence_result,out_file)
    # out_file.close()

    #tEnd = time.time()
    #print ("It costs %f sec",tEnd-tStart)

    return {'confluence': confluence}
###############################################################################
#
#image_path = u"C:\\Users\\Aaron.Lin\\Desktop\\cellC2_issue"
#image_output_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\output_test\\result.jpg"
#json_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\output_test\\result.json"
#
#file_list = listdir(image_path)
#filename = file_list[7]
#filename=image_path +'\\'+filename
# cellConfluence_singleTask(filename,image_output_path,json_path)




def cell_confluency_cv2(task_record):
    """Benchmark, repeat=5:
    IMG_0159.JPG = 14.129s
    1-3.jpg = 9.7s
    """
    # load image
    # img = cv2.imread('IMG_0159.JPG')
    img = cv2.imread(task_record.uploaded_image.path)

    # resize
    max_size = 1024.
    img_s = cv2.resize(img, tuple(
        [int(max_size / max(img.shape[:2]) * d) for d in img.shape[:2]]))
    #cv2.imshow('img_s', img_s)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.ubyte)
    img_e = filters.rank.enhance_contrast(filters.prewitt(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), tuple(
        [int(max_size / max(img.shape[:2]) * d) for d in img.shape[:2]]))), kernel)
    #cv2.imshow('img_e', img_e)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    thresh = cv2.threshold(img_e, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]
    print thresh
    img_t = np.uint8(img_e >= thresh)
    #cv2.imshow('img_t', img_t)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if (thresh < 5):
        img_t = cv2.morphologyEx(
            img_t, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))  # remove salt
    img_o = cv2.morphologyEx(
        cv2.erode(cv2.dilate(img_t, kernel, iterations=4), kernel, iterations=2), cv2.MORPH_OPEN, kernel)  # remove salt
    #cv2.imshow('img_o', img_o)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    for i in range(img_o.shape[0]):
        for j in range(img_o.shape[1]):
            if (img_o[i, j]):
                img_s[i, j, 2] = 200

    # compute confluence
    confluence = 100 * float(img_o.sum()) / img_o.size
    # embed result to image
    cv2.putText(img_s, '{0:.2f}%'.format(confluence),
                (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
    img_s = cv2.resize(
        img_s, (img.shape[1], img.shape[0]))

    cv2.imwrite(task_record.result_image.path, img_s)
    cv2.imwrite(task_record.result_display.path, img_s)

    return json.dumps({'confluence': confluence})

class File(object):
    path = ''

class Task(object):
    uploaded_image = File()
    result_image = File()
    result_display = File()

file='IMG_0159.JPG'
task_record = Task
task_record.uploaded_image.path = file
task_record.result_image.path = file + '_result'
task_record.result_display.path = file + '_result_display'

def bench(func, file='IMG_0159.JPG', number=5):

    from timeit import default_timer as timer
    start = timer()
    for i in range(number):
        func(task_record)
    end = timer()
    print(end - start) 