
# coding: utf-8

# In[8]:

from PIL import Image
import numpy as np
import pylab
import cv2
from skimage import io, morphology, data, color
from skimage.transform import resize
from skimage.filters import gabor, laplace, gaussian, threshold_otsu
from skimage.util import img_as_ubyte
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, skeletonize, disk
import json


def cellm3(input_image_path, output_image_path, json_path):

        selem = disk(1)

        ori_img = io.imread(input_image_path, plugin='tifffile')
        ori_img_int8 = cv2.convertScaleAbs(ori_img)


        # image resize
        scale_x_size = 512
        scale_ratio = float(ori_img_int8.shape[0]/float(scale_x_size))
        scale_y_size = int(ori_img_int8.shape[1]/float(scale_ratio))
        input_img_gray_rs = resize(ori_img_int8, (scale_x_size,scale_y_size),preserve_range=True)
        input_img_gray_rs_int = input_img_gray_rs.astype(np.uint8)

        #normalization to mean: 150
        input_img_gray_rs_int_norm = input_img_gray_rs_int*(150/float(ori_img_int8.mean()))


        # high pass filter, edge detector
        filt_imag = laplace(input_img_gray_rs_int_norm, ksize=5, mask=None)
        # rescale the gray level
        I = np.absolute(filt_imag)
        img_p1 = (((I - I.min()) / (I.max() - I.min())) * 255.9).astype(np.uint8)

        img_list = np.hstack(img_p1)

        #histogram the gray vale
        n, bins, patches = pylab.hist(img_list, 50, histtype='stepfilled')

        n2list = n.tolist()

        #find the seg value of wound part
        max_inx = n2list.index(max(n2list))

        bins2list = bins.tolist()

        #segmentation the wound part
        img_p2 = img_p1 >= bins2list[max_inx+1]

        #dilation and erosion
        eroded = dilation(img_p2, selem)
        img_p3 = erosion(eroded, selem)

        #remove the small white dot
        img_p3_inv = img_p3 == 0
        small_obj_thres = 50
        img_p4 = morphology.remove_small_holes(img_p3_inv, small_obj_thres)

        #remove the small black dot
        img_p4_inv = img_p4 == 0
        img_p5 = morphology.remove_small_holes(img_p4_inv, small_obj_thres)


        #----------------------------------


        mask_img_rs = resize(img_p5, (ori_img_int8.shape[0], ori_img_int8.shape[1]),preserve_range=True)
        mask_img_rs_int = mask_img_rs.astype(np.uint8)


        img_p5_inverse = mask_img_rs_int == 0

        #boundary handling
        #print img_p5.shape
        boundry_size = 1
        img_p5_inverse[:,0:boundry_size] = False
        img_p5_inverse[0:boundry_size,:] = False
        img_p5_inverse[:,(img_p5_inverse.shape[1]-boundry_size-1):(img_p5_inverse.shape[1])] = False
        img_p5_inverse[(img_p5_inverse.shape[0]-boundry_size-1):(img_p5_inverse.shape[0]),:] = False


        #io.imshow(img_p5_inverse)



        ratio = 100-(img_p5_inverse.sum())/float(img_p5_inverse.shape[0]*img_p5_inverse.shape[1])*100

        json_out_file = open(json_path,'w')
        ratio_rsult = {'ratio' : ratio}
        json.dump(ratio_rsult, json_out_file)
        json_out_file.close()


        img_color = np.dstack((ori_img_int8, ori_img_int8, ori_img_int8))
        #io.imshow(img_color)

        color_mask = np.zeros((ori_img_int8.shape[0], ori_img_int8.shape[1], 3))


        color_mask[img_p5_inverse] = [0, 0.9, 0.1]  # Red block
        #io.imshow(color_mask)

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
        img.save(output_image_path, "JPEG", quality=80)

