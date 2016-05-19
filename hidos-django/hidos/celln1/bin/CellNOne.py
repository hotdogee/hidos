
# coding: utf-8

# In[104]:


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
from pymorph import overlay
from skimage.filters.rank import mean
from skimage import feature
from skimage import exposure
from skimage import measure
from django.conf import settings
import skimage
# def PlotOut(img, title, img2, title2):
#     fig = plt.figure(figsize=(30,30))
#     ax0 = fig.add_subplot(121)
#     ax0.imshow(img, cmap='Greys')
#     ax0.set_title(title)
#     ax0.axis('off')

#     ax1 = fig.add_subplot(122)
#     ax1.imshow(img2, cmap='Greys')
#     ax1.set_title(title2)
#     ax1.axis('off')


def endPoints(skel):
    endpoint1=np.array([[0, 0, 0],[0, 1, 0],[2, 1, 2]])
    endpoint2=np.array([[0, 0, 0],[0, 1, 2],[0, 2, 1]])
    endpoint3=np.array([[0, 0, 2],[0, 1, 1],[0, 0, 2]])
    endpoint4=np.array([[0, 2, 1],[0, 1, 2],[0, 0, 0]])
    endpoint5=np.array([[2, 1, 2],[0, 1, 0],[0, 0, 0]])
    endpoint6=np.array([[1, 2, 0],[2, 1, 0],[0, 0, 0]])
    endpoint7=np.array([[2, 0, 0],[1, 1, 0],[2, 0, 0]])
    endpoint8=np.array([[0, 0, 0],[2, 1, 0],[1, 2, 0]])
    ep1=ma.morph.hitmiss(skel,endpoint1)
    ep2=ma.morph.hitmiss(skel,endpoint2)
    ep3=ma.morph.hitmiss(skel,endpoint3)
    ep4=ma.morph.hitmiss(skel,endpoint4)
    ep5=ma.morph.hitmiss(skel,endpoint5)
    ep6=ma.morph.hitmiss(skel,endpoint6)
    ep7=ma.morph.hitmiss(skel,endpoint7)
    ep8=ma.morph.hitmiss(skel,endpoint8)
    ep = ep1+ep2+ep3+ep4+ep5+ep6+ep7+ep8
    return ep


def CellNOne(img_input_path, img_output_path, json_output_path):

    # --------------------------------------------------------------------------------------------
    # read input image
    # tran image type as uint8

    ori_img = io.imread(img_input_path)
    ori_img_int8 = skimage.img_as_ubyte(ori_img)
    ori_img_int8_norm = (ori_img_int8 - ori_img.min())/float(ori_img_int8.max() - ori_img.min())*255.0
    ori_img_int8_norm = ori_img_int8_norm.astype('uint8')

    img = img_as_ubyte(ori_img_int8_norm)

    # --------------------------------------------------------------------------------------------
    # otsu thershold (not use)
    threshold_global_otsu = threshold_otsu(img)

    # img = mean(img, disk(1))
    global_otsu = img > threshold_global_otsu*0.4

    # --------------------------------------------------------------------------------------------
    # adaptive threshold
    block_size = 35
    img_pp1 = threshold_adaptive(img, block_size, offset = -10)

    # --------------------------------------------------------------------------------------------
    # remove small object 500
    small_obj_thres = 500
    # morphology.remove_small_objects
    # labeled_array, num_features = ndimage.measurements.label(global_otsu)
    img_p1 = morphology.remove_small_objects(img_pp1, small_obj_thres)

    # --------------------------------------------------------------------------------------------
    # skeleton after dilation
    selem = disk(1)
    temp = dilation(img_p1, selem)
    img_p6 = skeletonize(temp)
    img_skel = dilation(img_p6, selem)

    # --------------------------------------------------------------------------------------------
    # find soma using erosion
    # erosion time = 6
    # erosion time range > 3~10
    # erode_object = 100
    eroded = copy.copy(img_p1)
    erosion_time = 6
    for i in range(0, erosion_time, 1):
        eroded = erosion(eroded, selem)

    erode_object = 100
    erode_array, erode_features = ndimage.measurements.label(eroded)
    eroded2 = morphology.remove_small_objects(eroded, erode_object)

    selem = disk(erosion_time)
    img_p2 = dilation(eroded2, selem)

    # count soma number
    soma_array, soma_features = ndimage.measurements.label(img_p2)
    regions = measure.regionprops(soma_array)
    cen = []
    for props in regions:
        cen += props.centroid

    # --------------------------------------------------------------------------------------------
    # Attandance points
    # seperate counting
    edges_soma = feature.canny(img_p2)
    attpoint = edges_soma & img_p6
    soma_points = dilation(attpoint, disk(2))
    find_attand = attpoint*soma_array
    count = [0] * (soma_features+1)
    for i, row in enumerate(find_attand):
        for j, element in enumerate(row):
            count[element] = count[element] + 1
    del count[0]

    # total count
    sum_attpoints = np.sum(count)

    # --------------------------------------------------------------------------------------------
    # Dendrite inside and outside
    dendrine_in = img_p2 & img_p6
    dendrine = img_p6 ^ dendrine_in
    dendrine = dilation(dendrine, disk(1))

    #---------------------------------------------------------------------------------------------
    # find endpoints of Dendrine

    ep = endPoints(img_p6)>0
    sum_ep = np.sum(ep)
    ep = dilation(ep, disk(3))
    ep = ep ^ (ep & img_p2)
    #---------------------------------------------------------------------------------------------
    # display using overlay
    # draw text count on image
    display_1 = overlay(img)
    display_2 = overlay(dendrine, red = img_p6) # blue = img_p2
    display_3 = overlay(img, yellow = img_p2, magenta = dendrine) # magenta
    display_4 = overlay(img_p2, red = soma_points)
    display_5 = overlay(img, red = img_p2, blue = soma_points , magenta = ep, green = dendrine)

    display_3 = Image.fromarray(display_3)
    text = ImageFont.truetype(settings.FONT,16)
    draw = ImageDraw.Draw(display_3)

    k = 0
    for i in range(0,soma_features,1):
        draw.text((cen[k+1],cen[k]), str(i+1), (34, 139, 34), font = text)
        k = k + 2
    #---------------------------------------------------------------------------------------------
    # output as image and json file
    display_5 = Image.fromarray(display_5)
    Image.Image.save(display_5, img_output_path)

    # soma: number of soma
    # attands: startpoints from soma
    with open(json_output_path, "w") as outfile:
        json.dump({'soma':soma_features, 'body_attachments':sum_attpoints,
                   'endpoints':sum_ep}, outfile, indent=1)
    #---------------------------------------------------------------------------------------------
    # subplot image as testing
    # PlotOut(img, 'Original', display_5, 'display')
    # plt.show()
    #---------------------------------------------------------------------------------------------





# debug
# img_input_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\TUJ1-0001.tif'
# img_output_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\' + 'Example_1_output.tif'
# json_output_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\' + 'Example_1_output.json'
# CellNOne(img_input_path, img_output_path, json_output_path)


# In[ ]:




# In[ ]:



