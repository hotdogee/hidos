#setwd('C:\\Han\\Work\\Meridigen\\hidos\\tools\\1_6_obj_area_cal')
library("stats")
library("graphics")
library("grDevices")
library("utils")
library("datasets")
library("methods")
library("base")
library("EBImage")
library("RJSONIO")

args <- commandArgs(TRUE)
print(args)

image_file_path = args[1]

image_file = file.path(image_file_path)
imgc = readImage(image_file)

imgc_gray <- channel(imgc, 'gray')

img_gray_data = imageData(imgc_gray)

#--------------------------------------
imgc_p1 = imgc_gray
imgc_p2 = imgc_gray
img_mean = mean(imgc_gray)
img_std = sd(imgc_gray)
thres = img_mean - img_std
imgc_p1[imgc_gray < thres] = 1
imgc_p1[imgc_gray >= thres] = 0
thres = img_mean + img_std
imgc_p2[imgc_gray >= thres] = 1
imgc_p2[imgc_gray < thres] = 0

imgc_p3 = imgc_p1 + imgc_p2
#display(imgc_p3)

kern = makeBrush(7, shape='diamond')
nuct3 = dilate(imgc_p3, kern)

nuct4 = fillHull(nuct3)

kern = makeBrush(11, shape='disc')
nuct5 = erode(nuct4, kern)
#display(nuct5)

nuclabel3 = bwlabel(nuct5)

nuclabel3_gray<-channel(nuclabel3,"gray")
img_processed = paintObjects(nuclabel3_gray, imgc, col=c('#FF0000', '#FF0000'), opac=c(1, 0.4), thick=TRUE, closed=TRUE)


file_name_output = args[2]

writeImage(img_processed,file_name_output, quality=100)

ratio = length(nuclabel3[nuclabel3>0])/length(nuclabel3)

write(toJSON(list(ratio = ratio)),file = args[3])