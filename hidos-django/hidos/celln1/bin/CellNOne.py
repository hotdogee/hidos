
# coding: utf-8

# In[30]:


import numpy as np
import json
import pymorph
import mahotas as ma
import copy

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from matplotlib import pyplot as plt
from skimage import io, morphology
from skimage.filters import threshold_otsu, rank, threshold_adaptive
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
import cv2




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

def PlotOne(img):
    fig = plt.figure(figsize=(30,30))
    ax0 = fig.add_subplot(111)
    ax0.imshow(img, cmap=plt.cm.spectral)
    ax0.axis('off')


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

def deleShortline(skel):
    line_array, line_features = ndimage.measurements.label(trylabel)



def CellNOne(img_input_path, img_output_path, json_output_path):
    # --------------------------------------------------------------------------------------------
    # setting testing parameter
    # parameter = 25


    # --------------------------------------------------------------------------------------------
    # read input image
    # tran image type as uint8
    


    ori_img=cv2.imread(input_image_path)
    img_gray=cv2.cvtColor(ori_img, cv2.COLOR_BGR2GRAY)
    ori_img = img_as_ubyte(img_gray)

    ori_img_int8_norm = (ori_img - ori_img.min())/float(ori_img.max() - ori_img.min())*255.0
    ori_img_int8_norm = ori_img_int8_norm.astype('uint8')
    img = img_as_ubyte(ori_img_int8_norm)

    # --------------------------------------------------------------------------------------------
    # test for enhance_contrast
    # out = enhance_contrast(img, disk(5))
    # mean = np.mean(img)
    # img_pp1 = img >= (mean*0.5)
    # img1 = Image.fromarray(img)
    # contrast = ImageEnhance.Contrast(img1)

    # --------------------------------------------------------------------------------------------
    # otsu thershold (not use)
    threshold_global_otsu = threshold_otsu(img)

    img_thrs = img > threshold_global_otsu*0.1

    # --------------------------------------------------------------------------------------------
    # adaptive threshold
#     block_size = 75
#     img_pp1 = threshold_adaptive(img, block_size, offset = -5)

    # --------------------------------------------------------------------------------------------
    # remove small object 500
    small_obj_thres = 500
    img_p2 = morphology.remove_small_objects(img_thrs, small_obj_thres)
    img_p3 = clear_border(img_p2)
    img_tmp = img_p2 ^ img_p3
    clear_labeled = morphology.label(img_tmp, 8, background=0)
    for i in range(1, clear_labeled.max() + 1):
        clear_obj = clear_labeled == i
        temp = np.sum(clear_obj)
        if temp > 5000:
            img_p3 = np.logical_or(img_p3, clear_obj)

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
    dmap = ma.distance(img_p3)
# #     print np.mean(dmap)
# #     somap = dmap > ( dmap.max()+dmap.min() )/2
#     print dmap.max()
#     somap = dmap > dmap.max()/8

#     somap2 = ma.distance(somap)
#     print somap2.max()
#     somap3 = somap2 > somap2.max()/8

    tmap = copy.copy(img_p3)
    labeled_tmap = morphology.label(tmap, 8, background=0)
    cellbody = np.zeros(tmap.shape, dtype=bool)
    for i in range(1, labeled_tmap.max() + 1):
        tmap_obj = labeled_tmap == i
        dismap = ma.distance(tmap_obj)
        tmap_obj = dismap > dismap.max()*0.2
        cellbody = np.logical_or(cellbody, tmap_obj)

    cellbody = morphology.remove_small_objects(cellbody, 100)
    img_cellbody = dilation(cellbody, disk(3))
    labeled_cellbody, count_cellbody = ndimage.measurements.label(img_cellbody)


    # adaptive threshold
#     block_size = 175
#     smap = threshold_adaptive(dmap, block_size, offset = -20)

#     tt = exposure.histogram(dmap, nbins = 256)


#     fig = plt.figure(figsize=(30,30))
#     ax = fig.add_subplot(111)

#     # Display histogram
#     ax.hist(dmap.ravel(), bins=25)
#     ax.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
#     ax.set_xlabel('Pixel intensity')
#     ax.set_xlim(10, 255)
#     ax.set_ylim(0, 15000)
#     ax.set_yticks([])



    # --------------------------------------------------------------------------------------------
    # skeleton after dilation
    selem = disk(1)
    sk_temp = dilation(img_p3, selem)
    img_skel = skeletonize(sk_temp)
    # img_p6 = morphology.remove_small_holes(img_p6, min_size = 5)
    skel_show = dilation(img_skel, selem)

    # --------------------------------------------------------------------------------------------
    # find soma using erosion
    # erosion time = 6
    # erosion time range > 3~10
    # erode_object = 100

    # label again for each label has at least one soma
#     convex_label, convex_label_count = ndimage.measurements.label(convex_img)
#     tmd = 0
#     tmpoint = 0
#     pointsmax = 10
    # tmpoint*1.5 < pointsmax

#     while(tmd < convex_label_count):
#         # erosion
#         parameter = parameter - 1
#         print parameter, "parameter"
#         eroded = copy.copy(convex_img)
#         erosion_time = parameter
#         for i in range(0, erosion_time, 1):
#             eroded = erosion(eroded, disk(1))
# #         erode_object = 100
# #         erode_array, erode_features = ndimage.measurements.label(eroded)
# #         eroded2 = morphology.remove_small_objects(eroded, erode_object)
#         selem = disk(erosion_time-3)
#         img_p2 = dilation(eroded, selem)
#         # testing
#         tmf = []
#         for i in range(1, convex_label_count+1):
#             tmf.append(np.sum(np.logical_and(img_p2, (convex_label == i))))
#         print tmf
#         tmd = np.count_nonzero(tmf)
#         print tmd, "tmd"

#         # Soma Count and Attandance Count
# #         soma_array, soma_features = ndimage.measurements.label(img_p2)
# #         pointsmax = soma_features*15
# #         edges_soma = feature.canny(img_p2, sigma=0.5)
# #         attpoint = edges_soma & img_p6
# #         tmpoint = np.count_nonzero(attpoint)
# #         print tmpoint, pointsmax
#         result = overlay(img, red = img_p2)
#         PlotOne(result)

    # --------------------------------------------------------------------------------------------

    # count soma number
#         regions = measure.regionprops(soma_array)
    # soma centroid
#     cen = []
#     for props in regions:
#         cen += props.centroid



    # --------------------------------------------------------------------------------------------
    # Dendrite inside and outside
    dendrine_in = img_cellbody & img_skel
    dendrine_tmp = img_skel ^ dendrine_in
    dendrine = morphology.remove_small_objects(dendrine_tmp, 30, connectivity = 2)
    img_skel = img_skel ^ (dendrine ^ dendrine_tmp)
    dendrine_dila = dilation(dendrine, disk(1))

    count_length = np.sum(dendrine)

    # --------------------------------------------------------------------------------------------
    # test for delete shortline
    small_line = 10
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
#     display_1 = overlay(dendrine, red = dendrine)
#     display_2 = overlay(img_p6, yellow = img_p2, blue = dendrine_in)
#     display_12 = overlay(img_p6, magenta = ep)
#     display_3 = overlay(img, magenta = dendrine, blue = soma_points) # magenta
#     display_32 = overlay(img, magenta = dendrine_dila)
#     display_4 = overlay(img_p2, red = soma_points)
    result = overlay(img, green = img_cellbody, yellow = soma_points , cyan = ep, red = dendrine_dila) # blue = jp
#     display_6 = overlay(img_p6, red = ep)
#     display_7 = overlay(img, red = smap)
#     display_8 = overlay(img_p3, red = cellbody)
#     display_9 = overlay(img_p3, red = img_cellbody)
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
#     Image.Image.save(img_save, 'Example_1.jpg')

    result_save = Image.fromarray(result)
    Image.Image.save(result_save, img_output_path)
    with open(json_output_path, "w") as outfile:
        json.dump({'cell_body':count_cellbody,
                   'outgrowth_length':count_length,
                   'mean_length':mean_length,
                   'number_of_branches':count_branches,
                   'mean_branch':mean_branch,
                   'neurite_outgrowth':count_attpoint,
                   'mean_outgrowth':mean_outgrowth},
                  outfile, indent=1)
    #---------------------------------------------------------------------------------------------
    # subplot image as testing
#     PlotOut(img_p6, 'skeleton', display_6, 'Result')
#     PlotOut(img_p1, 'Original', img_pp1, 'Result')
#     PlotOut(img, 'Original', out, 'out')
#     PlotOut(img, 'Original', img_pp1, 'img_pp1')
#     PlotOut(convex_img, 'output1', display_7, 'output2')
#     PlotOut(somap, 'output1', dmap, 'output2')
#     PlotOut(img, 'img', result, 'result')
#     PlotOut(img, 'img', contrast, 'contrast')
#     PlotOut(img_p6, 'img_p6', dendrine, 'dendrine')
#     PlotOut(smap, 'result', tt, 'img')
#     PlotOut(img_p2, 'img_p1', img, 'img')
#     PlotOut(result, 'result', img, 'img')
#     PlotOne(result)
#     PlotOne(img_thrs)
#     PlotOne(dmap)
#     PlotOut(display_9, 'display_9', display_8, 'display_8')
#     PlotOut(img_p3, 'img_p3', dendrine, 'dendrine')
#     plt.show()
    #---------------------------------------------------------------------------------------------





# debug
# img_input_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\TUJ1-0011.tif'
# img_output_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\' + 'Example_1_output.tif'
# json_output_path = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\' + 'Example_1_output.json'
# CellNOne(img_input_path, img_output_path, json_output_path)


# In[ ]:



