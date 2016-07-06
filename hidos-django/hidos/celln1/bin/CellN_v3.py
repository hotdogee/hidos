
# coding: utf-8

# In[4]:

import cv2
import numpy as np
import json
import pymorph
import mahotas as ma
import copy

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
# from matplotlib import pyplot as plt
from skimage import io, morphology
from skimage.util import img_as_ubyte
from scipy import ndimage
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, skeletonize, disk
from skimage import color
from pymorph import overlay, se2hmt, supcanon
from skimage.filters.rank import enhance_contrast
from skimage import feature
from skimage import exposure
from skimage import measure
from skimage import filters
from skimage.segmentation import clear_border
import skimage
from scipy import ndimage


version = '0.3

# In[5]:

def PlotOut(img, title, img2, title2):
    fig = plt.figure(figsize=(30,30))
    ax0 = fig.add_subplot(121)
    ax0.imshow(img, cmap=plt.cm.spectral)
    ax0.set_title(title)
    ax0.axis('off')

    ax1 = fig.add_subplot(122)
    ax1.imshow(img2, cmap=plt.cm.spectral)

    ax1.set_title(title2)
    ax1.axis('off')
    # cmap='Greys'



# In[6]:

def PlotOne(img, title):
    fig = plt.figure(figsize=(30,30))
    ax0 = fig.add_subplot(111)
    ax0.imshow(img, cmap=plt.cm.spectral)
    ax0.set_title(title)
    ax0.axis('off')



# In[7]:

def endPoints(skel):
    endpoint1 = np.array([[0, 0, 0],[0, 1, 0],[0, 0, 0]], dtype = bool)
    endpoint2 = np.array([[0, 0, 1],[1, 0, 1],[1, 1, 1]], dtype = bool)
    endpoint3 = np.array([[0, 0, 0],[0, 1, 0],[0, 0, 0]], dtype = bool)
    endpoint4 = np.array([[1, 0, 0],[1, 0, 1],[1, 1, 1]], dtype = bool)
    interval_1 = se2hmt(endpoint1, endpoint2)
    ep_1 = supcanon(skel, interval_1)
    interval_2 = se2hmt(endpoint3, endpoint4)
    ep_2 = supcanon(skel, interval_2)
    ep = ep_1 + ep_2
    return ep


# In[8]:

def junctionPoints(skel):
    juncpoint1 = np.array([[0, 1, 0],[0, 1, 0],[1, 0, 1]], dtype = bool)
    juncpoint2 = np.array([[0, 0, 0],[1, 0, 1],[0, 1, 0]], dtype = bool)
    interval_A = se2hmt(juncpoint1, juncpoint2)
    jp_A = supcanon(skel, interval_A)

    juncpoint3 = np.array([[0, 1, 0],[1, 1, 1],[0, 0, 0]], dtype = bool)
    juncpoint4 = np.array([[1, 0, 1],[0, 0, 0],[0, 1, 0]], dtype = bool)
    interval_B = se2hmt(juncpoint3, juncpoint4)
    jp_B = supcanon(skel, interval_B)

    juncpoint5 = np.array([[0, 0, 1],[1, 1, 0],[0, 1, 0]], dtype = bool)
    juncpoint6 = np.array([[0, 1, 0],[0, 0, 1],[0, 0, 0]], dtype = bool)
    interval_C = se2hmt(juncpoint5, juncpoint6)
    jp_C = supcanon(skel, interval_C)

    jp = jp_A + jp_B + jp_C
    return jp


# In[68]:

def CellNOne(img_input_path, img_output_path, json_output_path):

#     import time
#     tStart=time.time()
    # --------------------------------------------------------------------------------------------
    # read input image
    # resize to 1200

    ori_img = cv2.imread(img_input_path)
    img_gray = cv2.cvtColor(ori_img, cv2.COLOR_BGR2GRAY)
    ori_img_int8 = img_as_ubyte(img_gray)

    height = np.size(ori_img_int8, 0)
    width = np.size(ori_img_int8, 1)
    if (width > 1200):
        factor = width / 1200
        dheight = height / factor
        dwidth = width / factor
        img = cv2.resize(ori_img_int8, (dwidth, dheight))
    else :
        img = ori_img_int8.copy()


    # --------------------------------------------------------------------------------------------
    # edge thershold
    blur = cv2.GaussianBlur(img,(5,5),0)
    thresh = skimage.filters.threshold_otsu(blur)
    edge = cv2.Canny(blur, 0, thresh)
    kernel = np.ones((5,5), np.uint8)
    img_thrs = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)
    img_thrs = img_thrs >= 1
    img_thrs = dilation(img_thrs, disk(1))
    img_thrs_reverse = 1 - img_thrs
    img_thrs_reverse = np.array(img_thrs_reverse, dtype=np.bool)
    small_holes = 100
    img_binary_reverse = morphology.remove_small_objects(img_thrs_reverse, small_holes)
    img_binary = 1 - img_binary_reverse
    # otsu thershold
    re3, img_thrs_1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_thrs_1 = np.array(img_thrs_1, dtype=np.bool)
    # combined those threshold result
    img_bi_or = np.logical_or(img_binary, img_thrs_1)

#     re3,img_thrs_1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#     img_thrs_1 = np.array(img_thrs_1, dtype=np.bool)
#     img_thrs_2 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 0)
#     img_thrs_2 = np.array(img_thrs_2, dtype=np.bool)
#     img_thrs = np.logical_or(img_thrs_1, img_thrs_2)
#     kernel = np.array([(0,0,1,0,0), (0,1,1,1,0), (1,1,1,1,1), (0,1,1,1,0), (0,0,1,0,0)], np.uint8)
#     equ = cv2.equalizeHist(img)

    # --------------------------------------------------------------------------------------------
    # remove small object 100
    img_bi_or_bool = np.array(img_bi_or, dtype=np.bool)
    small_obj_thres = 100
    img_p3 = morphology.remove_small_objects(img_bi_or_bool, small_obj_thres)

    # --------------------------------------------------------------------------------------------
    # clear border for small object or not
#     img_thrs_uint8 = np.array(img_thrs, dtype=np.uint8)
#     ret, label_image, stats, centroids = cv2.connectedComponentsWithStats(img_thrs_uint8)
#     img_p3 = clear_border(img_p2)
#     img_tmp = img_p2 ^ img_p3
#     clear_labeled = morphology.label(img_tmp, 8, background=0)
#     for i in range(1, clear_labeled.max() + 1):
#         clear_obj = clear_labeled == i
#         temp = np.sum(clear_obj)
#         if temp > 5000:
#             img_p3 = np.logical_or(img_p3, clear_obj)

    # --------------------------------------------------------------------------------------------
    # label each neuronal networks
    # take Median as key value
    # take 1/4-3/4 average as threshold(50%)
    # convexhull

#     area_count = []
#     for region in measure.regionprops(trylabel_array_1):
#         area_count.append(region.convex_area)
#     area_count.sort()
#     area_average = clear_border
#     upper = trylabel_features/2 + trylabel_features/4
#     lower = trylabel_features/2 - trylabel_features/4
#     area_average = 0.5*sum(area_count[lower: upper])/len(area_count[lower: upper])


#     labeled_im = morphology.label(trylabel, 8, background=0)
#     # convex_obj = np.zeros(trylabel.shape, dtype=bool)
#     img_p2 = np.zeros(trylabel.shape, dtype=bool)

#     for i in range(1, labeled_im.max() + 1):
#         convex_obj = morphology.convex_hull_image(labeled_im == i)
#         temp = np.sum(convex_obj)
#         if temp > area_average:
#             img_obj = np.logical_and((labeled_im == i), convex_obj)
#             img_p2 = np.logical_or(img_p2, img_obj)
    # --------------------------------------------------------------------------------------------
    # Find Soma Area
    # neuron density for soma points
    # mahotas.distance
    # remove wrong soma
    tmap = img_p3.copy()
    tmap_uint8 = np.array(tmap, dtype=np.uint8)
    ret, labeled_tmap, stats, centroids = cv2.connectedComponentsWithStats(tmap_uint8)
    cellbody = np.zeros(tmap.shape, dtype=bool)
    for i in range(1, labeled_tmap.max() + 1):
        tmap_obj = labeled_tmap == i
        dismap = ma.distance(tmap_obj)
        tmap_obj_soma = dismap > dismap.max()*0.1
        if (np.sum(tmap_obj)*0.8 > np.sum(tmap_obj_soma)):
            cellbody = np.logical_or(cellbody, tmap_obj_soma)

    cellbody = morphology.remove_small_objects(cellbody, 100)
    img_cellbody = dilation(cellbody, disk(2))
    img_cellbody = ndimage.binary_fill_holes(img_cellbody)
    labeled_cellbody, count_cellbody = ndimage.measurements.label(img_cellbody)

#     ret4,tmap_obj = cv2.threshold(dismap_norm, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#     tmap_obj = cv2.adaptiveThreshold(dismap_norm, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101, 0)
#     tmap_obj = np.array(tmap_obj, dtype=np.bool)
#     dmap = (dmap - dmap.min())/float(dmap.max() - dmap.min())*255.0
#     dmap = dmap.astype('uint8')
#     dmap = img_as_ubyte(dmap)
#     C = np.mean(dmap)
#     cellbody = cv2.adaptiveThreshold(dmap, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, -20)
#     cellbody = np.array(cellbody, dtype=np.bool)


    # --------------------------------------------------------------------------------------------
    # skeleton after dilation
    selem = disk(1)
    sk_temp = dilation(img_p3, selem)
    img_skel = skeletonize(sk_temp)
    skel_show = dilation(img_skel, selem)
#     img_p6 = morphology.remove_small_holes(img_p6, min_size = 5)

    # --------------------------------------------------------------------------------------------
    # Dendrite inside and outside
    dendrine_in = img_cellbody & img_skel
    dendrine_tmp = img_skel ^ dendrine_in
    dendrine = dendrine_tmp.copy()
    img_skel = img_skel ^ (dendrine ^ dendrine_tmp)
    dendrine_dila = dilation(dendrine, disk(1))
    count_length = np.sum(dendrine)

    # --------------------------------------------------------------------------------------------
    # test for delete shortline
    small_line = 30
    img_t1 = morphology.remove_small_objects(dendrine, small_line, connectivity = 2)
    img_t2 = img_skel^img_t1
    img_skel2 = img_skel^(dendrine^img_t1)
    # --------------------------------------------------------------------------------------------
    # Attandance points
    # seperate counting
    # edges_soma = measure.find_contours(img_p2, 0.8)
    attpoint = dilation(img_cellbody, disk(2)) & img_t1
    soma_points = dilation(attpoint, disk(3))
    labeled_attpoint, count_attpoint = ndimage.measurements.label(soma_points)

#     edges_soma2 = feature.canny(img_cellbody, sigma=0.5)
#     attpoint2 = edges_soma2 & img_p6
#     find_attand = attpoint2*soma_array
#     count = [0] * (soma_features+1)
#     for i, row in enumerate(find_attand):
#         for j, element in enumerate(row):
#             count[element] = count[element] + 1
#     del count[0]

    # total count
#     sum_attpoints = np.sum(count)


#     jp = junctionPoints(dendrine)
#     jp = dilation(jp, disk(3))
#     sum_jp = np.sum(jp)


    #---------------------------------------------------------------------------------------------
    # find endpoints of Dendrine
    ep = endPoints(img_skel)
    ep = ep ^ (ep & img_cellbody)
    count_ep = np.sum(ep)
    ep = dilation(ep, disk(3))



    #---------------------------------------------------------------------------------------------
#     # display using overlay

    result = overlay(img, green = img_cellbody, yellow = soma_points , cyan = ep, red = dendrine_dila) # blue = jp
    count_branches = count_ep-count_attpoint
    mean_length = round(float(count_length)/count_cellbody,3)
    mean_branch = round(float(count_branches)/count_cellbody,3)
    mean_outgrowth = round(float(count_attpoint)/count_cellbody,3)

    # draw text count on image
#     display_3 = Image.fromarray(display_3)
#     text = ImageFont.truetype("arial.ttf",16)
#     draw = ImageDraw.Draw(display_3)

#     k = 0
#     for i in range(0,soma_features,1):
#         draw.text((cen[k+1],cen[k]), str(i+1), (34, 139, 34), font = text)
#         k = k + 2
    #---------------------------------------------------------------------------------------------
    # output as image and json file

    result_save = Image.fromarray(result)
    Image.Image.save(result_save, img_output_path)
    with open(json_output_path, "w") as outfile:
        json.dump({'cell_body': count_cellbody,
                   'outgrowth_length': count_length,
                   'mean_length': mean_length,
                   'number_of_branches': count_branches,
                   'mean_branch': mean_branch,
                   'neurite_outgrowth': count_attpoint,
                   'mean_outgrowth': mean_outgrowth},
                  outfile, indent=1)
    #---------------------------------------------------------------------------------------------
    # subplot image as testing


#     tEnd=time.time()
#     print ("It costs %f sec",tEnd-tStart)

    PlotOne(img, 'img')
    PlotOne(edge, 'edge')
    PlotOne(img_p3, 'img_p3')
    PlotOne(result, 'result')
    plt.show()


# In[69]:

# debug
# import time
# img_input_path = 'C:\Users\Meriuser\Desktop\NeuronData\JPG_FILE\\TUJ1-0008.jpg'
# img_output_path = 'C:\Users\Meriuser\Desktop\NeuronData\JPG_FILE\\' + 'Example_2_output.jpg'
# json_output_path = 'C:\Users\Meriuser\Desktop\NeuronData\JPG_FILE\\' + 'Example_2_output.json'

# CellNOne(img_input_path, img_output_path, json_output_path)


# In[ ]:




# In[ ]:



