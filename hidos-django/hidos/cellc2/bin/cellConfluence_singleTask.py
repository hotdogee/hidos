# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 16:02:34 2016

@author: Aaron.Lin
"""

#get_ipython().magic(u'matplotlib qt')
import cv2
import numpy as np
from skimage import filters


def cell_confluency_cv2(task_record):
    """Benchmark, repeat=5:
    IMG_0159.JPG = 5.66s (1.13s avg)
    1-3.jpg = 3.51s (0.70s avg)
    """
    max_size = 1024
    # load image
    img = cv2.imread(task_record.uploaded_image.path)
    img_s = cv2.resize(img, tuple(
        [max_size * d / max(img.shape[:2]) for d in img.shape[1::-1]]))

    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.ubyte)
    img_e = cv2.GaussianBlur(filters.rank.enhance_contrast(filters.prewitt(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), tuple(
        [max_size * d / max(img.shape[:2]) for d in img.shape[1::-1]]))), kernel), (7, 7), 0)

    thresh = cv2.threshold(
        img_e, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]
    img_t = np.uint8(img_e >= thresh)
    if (thresh < 5):
        img_t = cv2.morphologyEx(img_t, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))  # remove salt
    img_o = cv2.morphologyEx(
        cv2.erode(cv2.dilate(img_t, kernel, iterations=4), kernel, iterations=2), cv2.MORPH_OPEN, kernel)  # remove salt

    img_s[:, :, 2][np.where(img_o > 0)] = 200

    # compute confluence
    confluence = float(img_o.sum()) / img_o.size

    # embed result to image
    cv2.putText(img_s, '{0:.2f}%'.format(confluence * 100),(40, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
    img_s = cv2.resize(img_s, (img.shape[1], img.shape[0]))

    cv2.imwrite(task_record.result_image.path, img_s)
    cv2.imwrite(task_record.result_display.path, img_s)
    return {'confluence': confluence}


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


def cellConfluence_singleTask(task_record):
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
    img_enhance = cv2.GaussianBlur(img_enhance, (7, 7), 0)
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

    mask = np.where(img_opening > 0)
    img_ori_resize[:, :, 2][mask] = 200

    # compute confluence
    confluence = float(img_opening.sum()) / img_opening.size

    # embed result to image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_ori_resize, '{0:.2f}%'.format(confluence * 100),
                (40, 80), font, 2, (255, 0, 0), 3)
    img_ori_resize = cv2.resize(
        img_ori_resize, (img_ori.shape[1], img_ori.shape[0]))

    cv2.imwrite(task_record.result_image.path, img_ori_resize)
    cv2.imwrite(task_record.result_display.path, img_ori_resize)

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


class File(object):
    path = ''


class Task(object):
    uploaded_image = File()
    result_image = File()
    result_display = File()

# from cellc2.bin import cellConfluence_singleTask as p
# p.bench(t.cell_confluency_cv2, file='IMG_0159.JPG', number=1)
# p.bench(t.cellConfluence_singleTask, file='IMG_0159.JPG', number=1)
# reload(p)
def bench(func, file='IMG_0159.JPG', number=5):
    from timeit import default_timer as timer
    from os import path
    name, ext = path.splitext(file)
    task_record = Task
    task_record.uploaded_image.path = name + ext
    task_record.result_image.path = name + '_result' + ext
    task_record.result_display.path = name + '_result_display' + ext

    print('Benchmarking {0} repeat {1}\nInput: {2}'.format(
        func.__name__, number, file))

    start = timer()
    for i in range(number):
        func(task_record)
    end = timer()

    print('Time: {0:.2f}s ({1:.2f}s avg)'.format(
        end - start, (end - start) / number))
