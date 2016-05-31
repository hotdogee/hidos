# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 17:59:21 2016

@author: Aaron.Lin
"""
#get_ipython().magic(u'matplotlib qt')
from skimage import io
from skimage import color
from skimage import filters
from skimage.transform import resize
from skimage import morphology
from skimage.morphology import disk
#from skimage.measure import label
#from os import listdir
from PIL import Image,ImageDraw,ImageFont
#import numpy
import json
from django.conf import settings

def img_resize(img,max_size):
    len1 = img.shape[0]
    len2 = img.shape[1]
    if (len1>=len2):
        factor = float(max_size)/len1
        img_out = resize(img,(max_size,int(factor*len2)))
    else:
        factor =float(max_size)/len2
        img_out = resize(img,(int(factor*len1),max_size))
    return img_out
###############################################################################


def cellConfluence_singleTask(image_input_path, image_output_path, json_path):

    img_ori=io.imread(image_input_path)

    if(img_ori.shape[0]>1024 or img_ori.shape[1]>1024):
        img_ori_resize=img_resize(img_ori,1024)  #resize
    else:
        img_ori_resize=img_ori

    img_gray=color.rgb2gray(img_ori_resize)  #rgb2gray
    #io.imshow(img_gray)
    #io.show()
    img_prewitt=filters.prewitt(img_gray)    #detect edge
    #io.imshow(img_prewitt)
    #io.show()
    #enhance
    img_enhance=filters.rank.enhance_contrast(img_prewitt,disk(5))
    #binarization
    thresh=filters.threshold_otsu(img_enhance)
    img_thresh=img_enhance>=thresh

    #local binarization
#    thresh1=filters.threshold_otsu(img_enhance[:img_enhance.shape[0]/2,:img_enhance.shape[1]/2])
#    thresh2=filters.threshold_otsu(img_enhance[:img_enhance.shape[0]/2,img_enhance.shape[1]/2+1:])
#    thresh3=filters.threshold_otsu(img_enhance[img_enhance.shape[0]/2+1:,:img_enhance.shape[1]/2])
#    thresh4=filters.threshold_otsu(img_enhance[img_enhance.shape[0]/2+1:,img_enhance.shape[1]/2+1:])
#    i1=img_enhance[:img_enhance.shape[0]/2,:img_enhance.shape[1]/2]>=thresh1
#    i2=img_enhance[:img_enhance.shape[0]/2,img_enhance.shape[1]/2+1:]>=thresh2
#    i3=img_enhance[img_enhance.shape[0]/2+1:,:img_enhance.shape[1]/2]>=thresh3
#    i4=img_enhance[img_enhance.shape[0]/2+1:,img_enhance.shape[1]/2+1:]>=thresh4
#    ii1 = numpy.concatenate((i1,i2),axis=1)
#    ii2 = numpy.concatenate((i3,i4),axis=1)
#    img_thresh = numpy.concatenate((ii1,ii2),axis=0)

    #io.imshow_collection([img_gray,img_prewitt,img_enhance,img_thresh])
    #img_closing=morphology.binary_closing(img_thresh)
    #img_label=label(img_closing,neighbors=8)
    img_dilation=morphology.binary_dilation(img_thresh)
    img_dilation=morphology.binary_dilation(img_dilation)
    img_dilation=morphology.binary_dilation(img_dilation)
    img_dilation=morphology.binary_dilation(img_dilation)

    img_erosion=morphology.binary_erosion(img_dilation)
    img_erosion=morphology.binary_erosion(img_erosion)
    #img_erosion=morphology.binary_erosion(img_erosion)
    #img_erosion=morphology.binary_erosion(img_erosion)
    img_opening=morphology.binary_opening(img_erosion)
    img_opening_ori_size =  resize(img_opening,(img_ori.shape[0],img_ori.shape[1]))

    for i in range(img_opening_ori_size.shape[0]):
        for j in range(img_opening_ori_size.shape[1]):
            if (img_opening_ori_size[i,j]):
                img_ori[i,j,0]=200

    #io.imshow(img_ori_resize_result)
    #io.show()
    #compute confluence
    confluence = 100*float(img_opening_ori_size.sum())/img_opening_ori_size.size

    confluence = '%.2f' % confluence
    ### embed result to image
    img_ori=Image.fromarray(img_ori)
    font=ImageFont.truetype(settings.FONT,img_ori.size[0]/20)  ## uncomment to deploy on server
    #font=ImageFont.truetype('/System/Library/Fonts/Apple Braille.ttf', img_ori.size[0]/20)
    draw = ImageDraw.Draw(img_ori)
    draw.text((100, 80), str(confluence+'%'), (0, 0, 255), font=font)
    ###
    #io.imsave(image_output_path,img_ori)
    Image.Image.save(img_ori,image_output_path)

    out_file = open(json_path,"w")
    confluence_result = {'ratio': confluence}

    json.dump(confluence_result,out_file)
    out_file.close()

    return
###############################################################################

#image_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\CellC MSC Images\\11d7909a9593cbea6e4179f36ba04640_in.jpg"
#image_output_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\output_test\\result.jpg"
#json_path = u"D:\Aaron workspace\Aaron\CellConfluence_Project\output_test\\result.json"
#cellConfluence_singleTask(image_path,image_output_path,json_path)


