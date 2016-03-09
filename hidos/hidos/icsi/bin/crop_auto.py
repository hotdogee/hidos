from skimage.feature import greycomatrix, greycoprops
from skimage.io import imread, imsave
import numpy as np
import os
from skimage.measure import label, regionprops
from scipy import ndimage as ndi
import argparse 

parser = argparse.ArgumentParser(description='auto crop out the ovum from image')
parser.add_argument('--input')
parser.add_argument('--output')
args = parser.parse_args()
INPUT_IMAGE_PATH = args.input
OUTPUT_IMAGE_PATH = args.output


def findExtreme(array):
    x=[]
    y=[]
    for point in array:
        x.append(point[0])
        y.append(point[1])

    x = np.array(x)
    y = np.array(y)
    return(x.min(), x.max(), y.min(), y.max())

def findSquare(x1,x2,y1,y2):
    center = [(x2-x1)/2+x1, (y2-y1)/2+y1]
    x_length = x2-x1
    y_length = y1-y1
    width = 0
    if x_length > y_length:
        width = x_length
    else:
        width = y_length
        
    new_x1 = center[0] - width/2; new_x2 = center[0] + width/2
    new_y1 = center[1] - width/2; new_y2 = center[1] + width/2
    
    if new_x1 < 0:
        new_x1 = 0
        
    if new_y1 < 0:
        new_y1 = 0
    
    return(new_x1,new_x2,new_y1,new_y2)


# settings  
PATCH_SIZE = 30 # glcm patch sizes
MIN_OBJECT_PATCH_NUMBER = 20
MARGIN_SIZE = 0

ori_img = imread(INPUT_IMAGE_PATH)
img = imread(INPUT_IMAGE_PATH,as_grey=True)
img = img*256
IMG_HEIGHT, IMG_WIDTH  = img.shape[:2]


rm_margin_x = IMG_HEIGHT % PATCH_SIZE
rm_margin_y = IMG_WIDTH % PATCH_SIZE


if rm_margin_x and rm_margin_y != 0:
    img = img[:(-(img.shape[0] % PATCH_SIZE)),:(-(img.shape[1] % PATCH_SIZE))]
    ori_img = ori_img[:(-(ori_img.shape[0] % PATCH_SIZE)),:(-(ori_img.shape[1] % PATCH_SIZE)),:]
elif rm_margin_x == 0:
    img = img[:,:(-(img.shape[1] % PATCH_SIZE))]
    ori_img = ori_img[:,:(-(ori_img.shape[1] % PATCH_SIZE)),:]
elif rm_margin_y == 0:
    img = img[:(-(img.shape[0] % PATCH_SIZE)),:]
    ori_img = ori_img[:(-(ori_img.shape[0] % PATCH_SIZE)),:,:]
else:
    img = img[:,:]
    ori_img = ori_img[:,:,:]

img[img >= 256] = 255 

ori_img_for_out = ori_img.copy()

# Define the locations of each pathes
locs = []
for i in range(0,img.shape[0], PATCH_SIZE):
    for j in range(0, img.shape[1], PATCH_SIZE):
        locs.append((i,j))


# save patch data 
patches = []
for loc in locs:
    patches.append(img[loc[0]:loc[0] + PATCH_SIZE,
                       loc[1]:loc[1] + PATCH_SIZE])


    
xs = []
for patch in patches:
    glcm = greycomatrix(patch, [5], [0], 256, symmetric=True, normed=True)
    xs.append(greycoprops(glcm, 'dissimilarity')[0, 0])

# the background patches have high similarity, thus we can remove it.
# and rebuilt a binary mask
selected_patch_idx =[xs.index(x) for x in xs if x > 8]
img_zeros = np.zeros((img.shape[0],img.shape[1]))
loc_select = []
for i in selected_patch_idx:
    loc_select.append(locs[i])

img_zeros = np.zeros((img.shape[0],img.shape[1]))
loc_select = []
for i in selected_patch_idx:
    loc_select.append(locs[i])

for loc in loc_select:
    img_zeros[loc[0]:loc[0] + PATCH_SIZE, loc[1]:loc[1] + PATCH_SIZE] = 1


# fill holes and remove small region on the mask 
img_zeros = ndi.binary_fill_holes(img_zeros)
obj, lab = ndi.label(img_zeros)
sizes = np.bincount(obj.ravel())
mask_sizes = sizes > PATCH_SIZE**2*MIN_OBJECT_PATCH_NUMBER +1 # a block size = 30*30, exclude area that smaller than 10 patches
mask_sizes[0] = 0
img_zeros = mask_sizes[obj]
img_label = label(img_zeros)
regions = regionprops(img_label)


img_time =0
for props in regions:
    keep_flag = 0
    for point in props.coords:
        y = point[0]
        x = point[1]
        if x < MARGIN_SIZE or x > IMG_WIDTH-MARGIN_SIZE and y < MARGIN_SIZE or y > IMG_HEIGHT-MARGIN_SIZE:
            keep_flag += 1
    
    if keep_flag == 0:
        img_time += 1
        x1_old, x2_old, y1_old, y2_old =  findExtreme(props.coords)
        x1,x2,y1,y2 = findSquare(x1_old,x2_old,y1_old,y2_old)
            
        if x2 > ori_img.shape[0]:
            x2 = ori_img.shape[0]-1
        if y2 > ori_img.shape[1]:
            y2 = ori_img.shape[1]-1

        img_crop = ori_img[x1:x2,y1:y2]/256


        for i in range(0,3):
            if i == 0:
                ori_img_for_out[x1,y1:y2,i]=255
                ori_img_for_out[x2,y1:y2,i]=255
                ori_img_for_out[x1:x2,y1,i]=255
                ori_img_for_out[x1:x2,y2,i]=255
            else:
                ori_img_for_out[x1,y1:y2,i]=0
                ori_img_for_out[x2,y1:y2,i]=0
                ori_img_for_out[x1:x2,y1,i]=0
                ori_img_for_out[x1:x2,y2,i]=0

        img_crop_path = OUTPUT_IMAGE_PATH +'_Crop' + str(img_time)+'.jpg'
        imsave(img_crop_path, img_crop)

ori_img_out_path = OUTPUT_IMAGE_PATH + '_out.jpg'
imsave(ori_img_out_path, ori_img_for_out)

if img_time == 0:
    print('This photo does not crop out anything!!')



