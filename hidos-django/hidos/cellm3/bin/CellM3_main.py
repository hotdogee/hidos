
# coding: utf-8

# In[42]:

from PIL import Image
#%matplotlib inline
#%matplotlib qt
import numpy as np
import pylab
import cv2
import mahotas as mh
from matplotlib import pyplot as plt
from skimage import io, morphology, data, color, img_as_ubyte
from skimage.transform import resize
from skimage.filters import gabor, laplace, gaussian
from skimage.util import img_as_ubyte
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, skeletonize, disk
from PIL import ImageFont, ImageDraw
import json

def mask_create(image_phase):

        img_list = np.hstack(image_phase)

        #histogram the gray vale
        n, bins = np.histogram(img_list, 10)

        n2list = n.tolist()
        bins2list = bins.tolist()

        #segmentation the wound part
        img_pp = image_phase >= bins2list[1]

        selem = disk(1)

        #dilation and erosion
        eroded = dilation(img_pp, selem)
        img_p3 = erosion(eroded, selem)

        #remove the small white dot
        img_p3_inv = img_p3 == 0
        small_obj_thres = 800
        img_p4 = morphology.remove_small_holes(img_p3_inv, small_obj_thres)

        #remove the small black dot
        img_p4_inv = img_p4 == 0
        img_p5 = morphology.remove_small_holes(img_p4_inv, small_obj_thres)


        return img_p5

def cellm3(input_image_path, output_image_path, json_path):



        ori_img = io.imread(input_image_path)
        ori_img_int8 = img_as_ubyte(ori_img)


        # image resize
        scale_x_size = 512
        scale_ratio = float(ori_img_int8.shape[0]/float(scale_x_size))
        scale_y_size = int(ori_img_int8.shape[1]/float(scale_ratio))
        input_img_gray_rs = resize(ori_img_int8, (scale_x_size,scale_y_size),preserve_range=True)
        input_img_gray_rs_int = input_img_gray_rs.astype(np.uint8)

        I = input_img_gray_rs_int
        img_p1 = (((I - I.min()) / float(I.max() - I.min())) * 255.9).astype(np.uint8)
        #io.imshow(img_p1)

        #normalization to mean: 150
        p1_norm = img_p1*(150/float(img_p1.mean()))
        p1_norm = p1_norm.astype(np.uint8)

        # high pass filter, edge detector
        filt_imag = laplace(p1_norm, ksize=5, mask=None)
        # rescale the gray level
        I = np.absolute(filt_imag)
        img_p2 = (((I - I.min()) / float(I.max() - I.min())) * 255.9).astype(np.uint8)
        p2_norm = img_p2*(150/float(img_p2.mean()))
        p2_norm[p2_norm > 255] = 255
        p2_norm = p2_norm.astype(np.uint8)


        #----------------------------------

        mask_2 = mask_create(p2_norm)


        mask_img_rs_2 = resize(mask_2, (ori_img_int8.shape[0], ori_img_int8.shape[1]),preserve_range=True)
        mask_img_rs_int_2 = mask_img_rs_2.astype(np.uint8)


        img_p5_inverse = (mask_img_rs_int_2 == 0)



        #boundary handling
        #print img_p5.shape
        boundry_size = 1
        img_p5_inverse[:,0:boundry_size] = False
        img_p5_inverse[0:boundry_size,:] = False
        img_p5_inverse[:,(img_p5_inverse.shape[1]-boundry_size-1):(img_p5_inverse.shape[1])] = False
        img_p5_inverse[(img_p5_inverse.shape[0]-boundry_size-1):(img_p5_inverse.shape[0]),:] = False




        ratio = (img_p5_inverse.sum())/float(img_p5_inverse.shape[0]*img_p5_inverse.shape[1])*100


        json_out_file = open(json_path,'w')
        ratio_rsult = {'ratio' : ratio}
        json.dump(ratio_rsult, json_out_file)
        json_out_file.close()


        img_color = np.dstack((ori_img_int8, ori_img_int8, ori_img_int8))

        color_mask = np.zeros((ori_img_int8.shape[0], ori_img_int8.shape[1], 3))


        color_mask[img_p5_inverse] = [0, 0.9, 0.1]  # Red block

        # Convert the input image and color mask to Hue Saturation Value (HSV)
        # colorspace
        img_hsv = color.rgb2hsv(img_color)
        color_mask_hsv = color.rgb2hsv(color_mask)
        alpha = 0.6
        # Replace the hue and saturation of the original image
        # with that of the color mask
        img_hsv[..., 0] = color_mask_hsv[..., 0]
        img_hsv[..., 1] = color_mask_hsv[..., 1] * alpha

        img_masked = color.hsv2rgb(img_hsv)


        img = Image.fromarray(img_as_ubyte(img_masked)).convert('RGB')
        img.save(output_image_path, quality=80)
