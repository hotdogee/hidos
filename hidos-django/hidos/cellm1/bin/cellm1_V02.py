import cv2
from PIL import Image
import numpy as np
import mahotas as mh
from skimage import io, morphology, data, color, img_as_ubyte
from skimage.transform import resize
from skimage.util import img_as_ubyte
from skimage.morphology import erosion, dilation, disk
from PIL import ImageFont, ImageDraw
from django.conf import settings


version = '0.2'


def cellm1(task_record):

    ori_img = io.imread(task_record.uploaded_image_path)
    ori_img_int8 = img_as_ubyte(ori_img)

    # image resize
    scale_y_size = 1024
    scale_ratio = float(ori_img_int8.shape[1] / float(scale_y_size))
    scale_x_size = int(ori_img_int8.shape[0] / float(scale_ratio)) + 1
    input_img_gray_rs = resize(
        ori_img_int8, (scale_x_size, scale_y_size), mode='constant', preserve_range=True)
    input_img_gray_rs_int = input_img_gray_rs.astype(np.uint8)

    I = input_img_gray_rs_int
    img_p1 = (((I - I.min()) / float(I.max() - I.min()))
              * 255.9).astype(np.uint8)
    p1_norm = img_p1 * (150 / float(img_p1.mean()))

    p1_norm2 = ((I / float(255)))

    map_std = np.zeros((scale_x_size, scale_y_size), dtype=np.float)

    for x_inx in range(0, scale_x_size):
        for y_inx in range(0, scale_y_size):

            map_std[x_inx, y_inx] = np.std(p1_norm2[x_inx, y_inx, :])

    # threshold the highly colored pixel from the others.
    roi_area = (map_std > 0.05)
    roi_area_adjust = dilation(erosion(roi_area, disk(1)), disk(1))

    roi_area_dilation = dilation(roi_area_adjust, disk(1))
    mask_distance = mh.distance(roi_area_dilation)
    mask_contour = (mask_distance == 1)

    ratio = (roi_area_adjust.sum()) / float(scale_x_size * scale_y_size) * 100
    ratio_str = "%.2f" % ratio

    # coloring the ROI regions
    img_masked = np.array(p1_norm, copy=True)
    img_masked[:, :, 0][mask_contour] = 0
    img_masked[:, :, 1][mask_contour] = 255
    img_masked[:, :, 2][mask_contour] = 0

    img_masked_rs = resize(img_masked, (ori_img_int8.shape[0], ori_img_int8.shape[
                           1]), preserve_range=True).astype(np.uint8)


    ## remove draw on image (weian)
    # img = Image.fromarray(img_as_ubyte(img_masked_rs)).convert('RGB')
    # font = ImageFont.truetype(settings.FONT, ori_img_int8.shape[0] / 20)
    # draw = ImageDraw.Draw(img)
    # draw.text((100, 80), ratio_str + '%', (255, 255, 0), font=font)
    #
    # #img.save(output_image_path, "JPEG", quality=80)
    # cv2.imwrite(task_record.result_image.path, img)
    # cv2.imwrite(task_record.result_display.path, img)

    cv2.imwrite(task_record.result_image.path, img_masked_rs)
    cv2.imwrite(task_record.result_display.path, img_masked_rs)

    return {'ratio': ratio}
