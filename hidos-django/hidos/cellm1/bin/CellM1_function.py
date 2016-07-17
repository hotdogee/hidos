
# coding: utf-8

# In[2]:

from PIL import Image
import numpy as np
# import pylab
import mahotas as mh
# from matplotlib import pyplot as plt
from skimage import io, morphology, data, color, img_as_ubyte
from skimage.transform import resize
from skimage.filters import gabor, laplace, gaussian, threshold_otsu
from skimage.util import img_as_ubyte
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, skeletonize, disk
from PIL import ImageFont, ImageDraw
import json

from django.conf import settings

def mask_create(image_phase, bin_select):

        img_list = np.hstack(image_phase)

        #histogram the gray vale
        n, bins = np.histogram(img_list, 20)

        n2list = n.tolist()
        bins2list = bins.tolist()

        #segmentation the wound part
        img_out = image_phase >= bins2list[bin_select]

        return img_out

def cellm1(input_image_path, output_image_path, json_path):

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

        #normalization to mean: 150
        p1_norm = img_p1*(150/float(img_p1.mean()))
        #p1_norm[p1_norm > 255] = 255
        p1_norm = p1_norm.astype(np.uint8)

        map_std = np.zeros((scale_x_size, scale_y_size), dtype=np.float)

        for x_inx in range(0, scale_x_size):
            for y_inx in range(0, scale_y_size):

                map_std[x_inx,y_inx] = np.std(p1_norm[x_inx,y_inx,:])

        II = map_std
        map_std_norm = (((II - II.min()) / float(II.max() - II.min())) * 255.9).astype(np.uint8)


        mask = mask_create(map_std_norm, 4)
        mask_img_int = (mask*255).astype(np.uint8)


        roi_area = (mask_img_int > 0)

        selem = disk(2)
        roi_area_dilation = dilation(roi_area, selem)

        mask_distance = mh.distance(roi_area_dilation)


        mask_contour = (mask_distance == 1)

        ratio = (roi_area.sum())/float(scale_x_size*scale_y_size)*100
        ratio_str = "%.2f"%ratio

        json_out_file = open(json_path,'w')
        ratio_rsult = {'ratio' : ratio}
        json.dump(ratio_rsult, json_out_file)
        json_out_file.close()


        img_masked = np.array(p1_norm, copy=True)

        img_masked[:,:,1][mask_contour] = 255
        img_masked_rs = (resize(img_masked, (ori_img_int8.shape[0],ori_img_int8.shape[1]),preserve_range=True)).astype(np.uint8)


        img = Image.fromarray(img_as_ubyte(img_masked_rs)).convert('RGB')
        font = ImageFont.truetype(settings.FONT,ori_img_int8.shape[0]/20)
        draw = ImageDraw.Draw(img)
        draw.text((100, 80), ratio_str + '%', (255,255,0), font = font)

        img.save(output_image_path, "JPEG", quality=80)







