import matplotlib.pyplot as plt 
from skimage.feature import greycomatrix, greycoprops
from skimage.io import imread, imsave
import numpy as np
import os
from skimage.measure import label, regionprops
from scipy import ndimage as ndi



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
    y_length = y2-y1
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


lost_image = open('./crop_nothing_list.txt','a')

f_n = [x for x in os.listdir('./')]

for count, image_name in enumerate(f_n):
    if  image_name.split('.')[1] == 'jpg':
        img = imread(image_name,as_grey=True)
        PATCH_SIZE = 30
        img = img*256
#         fig = plt.figure()
#         ax = fig.add_subplot(1,2,1)
#         ax.imshow(img, cmap='gray')

        img = img[:-15, :-20]  # small trick, ori image = 1220*915
        img[img >= 256] = 0

        locs = []
        for i in range(0, img.shape[0], PATCH_SIZE):
            for j in range(0, img.shape[1], PATCH_SIZE):
                locs.append((i, j))

        patches = []
        for loc in locs:
            patches.append(img[loc[0]:loc[0] + PATCH_SIZE,
                               loc[1]:loc[1] + PATCH_SIZE])


        xs = []
        ys = []
        for patch in patches:
            glcm = greycomatrix(patch, [5], [0], 256, symmetric=True, normed=True)
            xs.append(greycoprops(glcm, 'dissimilarity')[0, 0])
            ys.append(greycoprops(glcm, 'correlation')[0, 0])

        
        
        # the background patches have high similarity, thus we can remove it.
        selected_patch_idx =[xs.index(x) for x in xs if x > 5]
        img_zeros = np.zeros((img.shape[0],img.shape[1]))
        loc_select = []
        for i in selected_patch_idx:
            loc_select.append(locs[i])

#         for loc in loc_select:
#             img_zeros[loc[0]:loc[0] + PATCH_SIZE, loc[1]:loc[1] + PATCH_SIZE] = \
#             img[loc[0]:loc[0] + PATCH_SIZE,loc[1]:loc[1] + PATCH_SIZE]

#         ax = fig.add_subplot(1,2,2)
#         ax.imshow(img_zeros,cmap='gray')
        
        
        print(image_name)
        
        img_zeros = np.zeros((img.shape[0],img.shape[1]))
        loc_select = []
        for i in selected_patch_idx:
            loc_select.append(locs[i])

        for loc in loc_select:
            img_zeros[loc[0]:loc[0] + PATCH_SIZE, loc[1]:loc[1] + PATCH_SIZE] = 1

            
        # fill holes and remove small region
        img_zeros = ndi.binary_fill_holes(img_zeros)
        obj, lab = ndi.label(img_zeros)
        sizes = np.bincount(obj.ravel())
        mask_sizes = sizes > PATCH_SIZE**2*20 +1 # a block size = 30*30, exclude area that smaller than 10 patches
        mask_sizes[0] = 0
        img_zeros = mask_sizes[obj]
            
        img_label = label(img_zeros)
        regions = regionprops(img_label)
        
        # the photo size is 1200*900
        
        MARGIN_SIZE = 0
        
        img_time =0
        for props in regions:
            keep_flag = 0
            for point in props.coords:
                y = point[0]
                x = point[1]
                if x < MARGIN_SIZE or x > 1200-MARGIN_SIZE and y < 200 or y > 900-MARGIN_SIZE:
                    keep_flag += 1
            
            if keep_flag == 0:
                img_time += 1
                x1_old, x2_old, y1_old, y2_old =  findExtreme(props.coords)
                x1,x2,y1,y2 = findSquare(x1_old,x2_old,y1_old,y2_old)
                    
                img_crop = img[x1:x2,y1:y2]/256
                img_crop_path = './img_crop/'+str(image_name.split('.')[0])+'_Crop' + str(img_time)+'.jpg'
                imsave(img_crop_path, img_crop)
                
        if img_time == 0:
            print('This photo does not crop out anything!!')
            lost_image.write(image_name+'\n')

