
# coding: utf-8

# In[100]:

import cv2
import numpy as np
import json
import pymorph
import mahotas as ma
import copy

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from matplotlib import pyplot as plt
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
from skimage.segmentation import clear_border
import skimage
from scipy import ndimage


# In[101]:

def PlotOut(img, title, img2, title2):
    fig = plt.figure(figsize=(30, 30))
    ax0 = fig.add_subplot(121)
    ax0.imshow(img, cmap=plt.cm.spectral)
    ax0.set_title(title)
    ax0.axis('off')

    ax1 = fig.add_subplot(122)
    ax1.imshow(img2, cmap=plt.cm.spectral)

    ax1.set_title(title2)
    ax1.axis('off')
    # cmap='Greys'



# In[102]:

def PlotOne(img, title):
    fig = plt.figure(figsize=(30,30))
    ax0 = fig.add_subplot(111)
    ax0.imshow(img, cmap=plt.cm.spectral)
    ax0.set_title(title)
    ax0.axis('off')



# In[103]:

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


# In[104]:

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


# In[105]:

# def FindThreshold(img):



# In[225]:

def CellNOne(img_input_path, img_output_path, json_output_path):

#     import time
#     tStart=time.time()
    # --------------------------------------------------------------------------------------------
    # read input image
    # resize

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
    # otsu thershold
#     equ = cv2.equalizeHist(img)
    blur = cv2.GaussianBlur(img,(5,5),0)
#     print type(blur)
#     edge = cv2.Canny(blur, 0, 255)

#     thresh = skimage.filters.threshold_otsu(blur)
#     binary_1 = blur >= thresh * 0.05
#     binary_2 = blur >= thresh * 0.1
#     binary_3 = blur >= thresh * 0.5
#     binary_4 = blur >= thresh * 1

    ret3,img_thrs_1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#     img_thrs_1 = np.array(img_thrs_1, dtype=np.bool)

    img_thrs_2 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 0)
    img_thrs_2 = np.array(img_thrs_2, dtype=np.bool)

    img_thrs = np.logical_or(img_thrs_1, img_thrs_2)

    # --------------------------------------------------------------------------------------------
    # remove small object 100

    small_obj_thres = 100
    img_p3 = morphology.remove_small_objects(img_thrs, small_obj_thres)

#     img_thrs_uint8 = np.array(img_thrs, dtype=np.uint8)
#     ret, label_image, stats, centroids = cv2.connectedComponentsWithStats(img_thrs_uint8)
#     print stats
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
    # clear_border
#     clear_border
#     trylabel = copy.copy(img_p1)
#     trylabel_array_1, trylabel_features = ndimage.measurements.label(trylabel)

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
    # neuron density for soma points
    # mahotas.distance

# #     print np.mean(dmap)
# #     somap = dmap > ( dmap.max()+dmap.min() )/2
#     print dmap.max()
#     somap = dmap > dmap.max()/8

#     somap2 = ma.distance(somap)
#     print somap2.max()
#     somap3 = somap2 > somap2.max()/8


    dmap = ma.distance(img_p3)
    tmap = img_p3.copy()
    tmap_uint8 = np.array(tmap, dtype=np.uint8)
    ret, labeled_tmap, stats, centroids = cv2.connectedComponentsWithStats(tmap_uint8)

    cellbody = np.zeros(tmap.shape, dtype=bool)
#     dmap = (dmap - dmap.min())/float(dmap.max() - dmap.min())*255.0
#     dmap = dmap.astype('uint8')
#     dmap = img_as_ubyte(dmap)
#     C = np.mean(dmap)
#     cellbody = cv2.adaptiveThreshold(dmap, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, -20)
#     cellbody = np.array(cellbody, dtype=np.bool)
    for i in range(1, labeled_tmap.max() + 1):
        tmap_obj = labeled_tmap == i
        dismap = ma.distance(tmap_obj)

#         dismap_norm = (dismap - dismap.min())/float(dismap.max() - dismap.min())*255.0
#         dismap_norm = dismap_norm.astype('uint8')
#         dismap_norm = img_as_ubyte(dismap_norm)

#         ret4,tmap_obj = cv2.threshold(dismap_norm, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#         tmap_obj = cv2.adaptiveThreshold(dismap_norm, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101, 0)
#         tmap_obj = np.array(tmap_obj, dtype=np.bool)

        tmap_obj = dismap > dismap.max()*0.1
        cellbody = np.logical_or(cellbody, tmap_obj)





    cellbody = morphology.remove_small_objects(cellbody, 100)
    img_cellbody = dilation(cellbody, disk(2))

    # imfill
    img_cellbody = ndimage.binary_fill_holes(img_cellbody)



    labeled_cellbody, count_cellbody = ndimage.measurements.label(img_cellbody)

    # --------------------------------------------------------------------------------------------
    # skeleton after dilation
    selem = disk(1)
    sk_temp = dilation(img_p3, selem)
    img_skel = skeletonize(sk_temp)
    # img_p6 = morphology.remove_small_holes(img_p6, min_size = 5)
    skel_show = dilation(img_skel, selem)

    # --------------------------------------------------------------------------------------------
    # Dendrite inside and outside
    dendrine_in = img_cellbody & img_skel
    dendrine_tmp = img_skel ^ dendrine_in
    dendrine = dendrine_tmp.copy()
    # dendrine = morphology.remove_small_objects(dendrine_tmp, 30, connectivity = 2)
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
    # print attpoint_features

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
    # print sum_jp
    #---------------------------------------------------------------------------------------------
    # find endpoints of Dendrine
    ep = endPoints(img_skel)
    ep = ep ^ (ep & img_cellbody)
    count_ep = np.sum(ep)
    ep = dilation(ep, disk(3))
#     #---------------------------------------------------------------------------------------------
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
    # soma: number of soma
    # attands: startpoints from soma
#     img_save = Image.fromarray(img)
#     Image.Image.save(img_save, 'Example_2.jpg')

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

#     PlotOne(ori_img, 'ori_img')
#     PlotOne(img, 'img')
#     PlotOne(img_thrs, 'img_thrs')
#     PlotOne(img_p3, 'img_p3')
#     PlotOne(dmap, 'dmap')
#     PlotOne(result, 'result')

#     PlotOne(binary_1, 'binary_1')
#     PlotOne(binary_2, 'binary_2')
#     PlotOne(binary_3, 'binary_3')
#     PlotOne(binary_4, 'binary_4')
#     PlotOne(edge, 'edge')
#     PlotOne(img_thrs_1, 'img_thrs_1')
#     PlotOne(img_thrs_2, 'img_thrs_2')
#     plt.show()


# In[226]:

# debug
# import time
# img_input_path = 'C:\Users\Meriuser\Desktop\NeuronData\JPG_FILE\\TUJ1-0014.jpg'
# img_output_path = 'C:\Users\Meriuser\Desktop\NeuronData\JPG_FILE\\' + 'Example_2_output.jpg'
# json_output_path = 'C:\Users\Meriuser\Desktop\NeuronData\JPG_FILE\\' + 'Example_2_output.json'

# CellNOne(img_input_path, img_output_path, json_output_path)


# In[ ]:




# In[ ]:



