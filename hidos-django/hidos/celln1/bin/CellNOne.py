
# coding: utf-8

# In[5]:


import numpy as np
import json
import pymorph
import mahotas as ma
import copy

from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
from skimage import io, morphology
from skimage.filters import threshold_otsu, rank, threshold_adaptive
from skimage.util import img_as_ubyte
from scipy import ndimage
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, skeletonize, disk
from skimage import color
from pymorph import overlay, se2hmt, supcanon
from skimage.filters.rank import mean
from skimage import feature
from skimage import exposure
from skimage import measure

def endPoints(skel):
    endpoint1 = np.array([[0, 0, 0],[0, 1, 0],[0, 0, 0]], dtype = bool)
    endpoint2 = np.array([[0, 0, 0],[1, 0, 1],[1, 1, 1]], dtype = bool)
    interval = se2hmt(endpoint1, endpoint2)
    ep = supcanon(skel, interval)
    return ep


def CellNOne(img_input_path, img_output_path, json_output_path):
    # --------------------------------------------------------------------------------------------
    # setting testing parameter
    parameter = 15
    # --------------------------------------------------------------------------------------------
    # read input image
    # tran image type as uint8

    ori_img = io.imread(img_input_path)
    ori_img_int8_norm = (ori_img - ori_img.min())/float(ori_img.max() - ori_img.min())*255.0
    ori_img_int8_norm = ori_img_int8_norm.astype('uint8')
    img = img_as_ubyte(ori_img_int8_norm)

    # --------------------------------------------------------------------------------------------
    # otsu thershold
    threshold_global_otsu = threshold_otsu(img)
    img_pp1 = img > threshold_global_otsu*0.4


    # --------------------------------------------------------------------------------------------
    # remove small object 500
    small_obj_thres = 500
    # morphology.remove_small_objects
    img_p1 = morphology.remove_small_objects(img_pp1, small_obj_thres)

    # --------------------------------------------------------------------------------------------
    # label each neuronal networks
    # take Median as key value
    # take 1/4-3/4 average as threshold(20%)

    trylabel = copy.copy(img_p1)
    trylabel_array_1, trylabel_features = ndimage.measurements.label(trylabel)
    area_count = []
    for region in measure.regionprops(trylabel_array_1):
        area_count.append(region.convex_area)
    area_count.sort()

    upper = trylabel_features/2 + trylabel_features/4
    lower = trylabel_features/2 - trylabel_features/4
    area_average = 0.2*sum(area_count[lower: upper])/len(area_count[lower: upper])


    labeled_im = morphology.label(trylabel, 8, background=0)
    # convex_obj = np.zeros(trylabel.shape, dtype=bool)
    convex_img = np.zeros(trylabel.shape, dtype=bool)

    for i in range(1, labeled_im.max() + 1):
        convex_obj = morphology.convex_hull_image(labeled_im == i)
        temp = np.sum(convex_obj)
        if temp > area_average:
            img_obj = np.logical_and((labeled_im == i), convex_obj)
            convex_img = np.logical_or(convex_img, img_obj)


    # --------------------------------------------------------------------------------------------
    # skeleton after dilation
    selem = disk(1)
    sk_temp = dilation(convex_img, selem)
    img_p6 = skeletonize(sk_temp)
    # img_p6 = morphology.remove_small_holes(img_p6, min_size = 5)
    img_skel = dilation(img_p6, selem)

    # --------------------------------------------------------------------------------------------
    # find soma using erosion
    # erosion time = 6
    # erosion time range > 3~10
    # erode_object = 100

    # label again for each label has at least one soma
    convex_label, convex_label_count = ndimage.measurements.label(convex_img)
    tmd = 0
    tmpoint = 0
    pointsmax = 10
    while(tmd < convex_label_count and tmpoint*1.3 < pointsmax):
        # erosion
        parameter = parameter - 1
        eroded = copy.copy(convex_img)
        erosion_time = parameter
        for i in range(0, erosion_time, 1):
            eroded = erosion(eroded, disk(1))
        erode_object = 100
        erode_array, erode_features = ndimage.measurements.label(eroded)
        eroded2 = morphology.remove_small_objects(eroded, erode_object)
        selem = disk(erosion_time)
        img_p2 = dilation(eroded2, selem)
        # testing
        tmf = []
        for i in range(1, convex_label.max() + 1):
            tmf.append(np.sum(np.logical_and(img_p2, (convex_label == i))))
        tmd = np.count_nonzero(tmf)

        # Soma Count and Attandance Count
        soma_array, soma_features = ndimage.measurements.label(img_p2)
        pointsmax = soma_features*20
        edges_soma = feature.canny(img_p2, sigma=0.5)
        attpoint = edges_soma & img_p6
        soma_points = dilation(attpoint, disk(2))
        tmpoint = np.count_nonzero(attpoint)

    # --------------------------------------------------------------------------------------------
    # Dendrite inside and outside
    dendrine_in = img_p2 & img_p6
    dendrine = img_p6 ^ dendrine_in
    dendrine = dilation(dendrine, disk(1))

    #---------------------------------------------------------------------------------------------
    # find endpoints of Dendrine
    ep = endPoints(img_p6)
    sum_ep = np.sum(ep)
    ep = dilation(ep, disk(3))
    ep = ep ^ (ep & img_p2)
    #---------------------------------------------------------------------------------------------
    # display using overlay
    result = overlay(img, red = img_p2, blue = soma_points , magenta = ep, green = dendrine)

    #---------------------------------------------------------------------------------------------
    # output as image and json file
    result = Image.fromarray(result)
#     img = Image.fromarray(img)
    Image.Image.save(result, img_output_path)
#     Image.Image.save(img, 'Example_3.jpg')

    # soma: number of soma
    # attands: startpoints from soma
    with open(json_output_path, "w") as outfile:
        json.dump({'soma':soma_features, 'body_attachments':tmpoint,
                   'endpoints':sum_ep}, outfile, indent=1)
    #---------------------------------------------------------------------------------------------






# debug
# img_input_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\TUJ1-0017.tif'
# img_output_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\\' + 'Example_3_output.jpg'
# json_output_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\\' + 'Example_3_output.json'
# CellNOne(img_input_path, img_output_path, json_output_path)


# In[ ]:



