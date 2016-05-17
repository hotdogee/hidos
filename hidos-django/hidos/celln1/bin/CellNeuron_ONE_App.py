
# coding: utf-8

# In[62]:


import cv2
from PIL import Image, ImageDraw, ImageFont
import json

from skimage import io, morphology
from skimage.filters import threshold_otsu, rank
from skimage.util import img_as_ubyte
from scipy import ndimage
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, skeletonize, disk
from pymorph import overlay
from skimage import feature
from skimage import measure




def CellNOne(img_input_path, img_output_path, json_output_path):

#     input_dir = 'C:\Users\Meriuser\Desktop\python image processing\CellN\mHN\\'
#     img_name = 'TUJ1-0006.tif'
#     img_input_path = input_dir+img_name
    ori_img = io.imread(img_input_path)

    ori_img_int8 = cv2.convertScaleAbs(ori_img)
    ori_img_int8_norm = (ori_img_int8 - ori_img.min())/float(ori_img_int8.max() - ori_img.min())*255.0
    ori_img_int8_norm = ori_img_int8_norm.astype('uint8')

    # print (ori_img_int8.max())
    # print (ori_img_int8.min())

    img = img_as_ubyte(ori_img_int8_norm)
    # img = exposure.equalize_hist(img)

    threshold_global_otsu = threshold_otsu(img)
    # print img.max()
    # print img.min()


#    img2 = mean(img, disk(10))
    global_otsu = img > threshold_global_otsu
    # print global_otsu
    # filled = ndimage.binary_fill_holes(global_otsu)
    small_obj_thres = 500
    # morphology.remove_small_objects
    labeled_array, num_features = ndimage.measurements.label(global_otsu)
    img_p1 = morphology.remove_small_objects(global_otsu, small_obj_thres)

    selem = disk(1)
    temp = dilation(img_p1, selem)
    img_p6 = skeletonize(temp)
    img_skel = dilation(img_p6, selem)

    # find soma
    selem = disk(8)
    eroded = erosion(img_p1, selem)
    selem = disk(7)
    img_p2 = dilation(eroded, selem)
    soma_array, soma_features = ndimage.measurements.label(img_p2)
    regions = measure.regionprops(soma_array)
    cen = []
    for props in regions:
        cen += props.centroid



    edges_soma = feature.canny(img_p2)

    attpoint = edges_soma & img_p6
    selem = disk(1)
    test = dilation(attpoint, selem)

    # Attandance points
    find_attand = attpoint*soma_array
    count = [0] * (soma_features+1)
    for i, row in enumerate(find_attand):
        for j, element in enumerate(row):
            count[element] = count[element] + 1
    del count[0]
    # print count

    # Dendrite
    dendrine_in = img_p2 & img_p6
    dendrine = img_p6 ^ dendrine_in
    dendrine = dilation(dendrine, selem)

    display_1 = overlay(img)
    display_2 = overlay(dendrine, blue = img_p2, red = img_p6)
    display_3 = overlay(img, cyan = img_p2, magenta = dendrine)
    display_4 = overlay(img_p2, red = test)
    # display_3 = overlay(filled, blue = sk2, green = spine_sk, red = ep_show)

    display_3 = Image.fromarray(display_3)
    text = ImageFont.truetype("/Library/Fonts/PTMono.ttc",16)
    draw = ImageDraw.Draw(display_3)

    k = 0
    for i in range(0,soma_features,1):
        draw.text((cen[k+1],cen[k]), str(i+1), (34, 139, 34), font = text)
        k = k + 2

    Image.Image.save(display_3, img_output_path)
#     imsave('Example_2.tif', img)

    # soma: number of soma
    # attands: startpoints from soma
    #
    with open(json_output_path, "w") as outfile:
        json.dump({'soma':soma_features, 'attands':count}, outfile, indent=1)


