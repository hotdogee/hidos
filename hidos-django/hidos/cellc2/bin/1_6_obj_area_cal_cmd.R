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
imgcs = resize(imgc, 1024)

imgc_gray <- channel(imgcs, 'gray')

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

#imgc_p3 = imgc_p1+imgc_p2
imgc_p3 = imgc_p2
#display(imgc_p3)

kern = makeBrush(15, shape='diamond')
nuct3 = dilate(imgc_p3, kern)

#nuct4 = fillHull(nuct3)

kern = makeBrush(7, shape='disc')
nuct5 = erode(nuct3, kern)
nuclabel3 = bwlabel(nuct5)
#display(nuct5)

h7 <- distmap(nuct5)
h8 <- watershed(h7, tolerance=0.5)
ftrs = computeFeatures.shape(h8)
id <- which(ftrs[, 's.area']>(mean(ftrs[, 's.area'])-sd(ftrs[, 's.area'])))
h8[is.na(match(h8, id))] <- 0
h9 = resize(h8, dim(imgc)[1],  dim(imgc)[2])
#display(normalize(h8))

count_min = length(id)
count_max = floor(sum(ftrs[, 's.area']) / median(ftrs[, 's.area']))

#nuclabel3_gray<-channel(nuclabel3,"gray")
img_processed = paintObjects(h9, imgc, col=c('#FF0000', '#FF0000'), opac=c(1, 0.4), thick=TRUE, closed=TRUE)
#img_processed = paintObjects(nuclabel3_gray, imgc, col='#ff00ff')
#display(img_processed)

file_name_output = args[2]

writeImage(img_processed,file_name_output, quality=100)

ratio = length(nuclabel3[nuclabel3>0])/length(nuclabel3)

write(toJSON(list(ratio = ratio, count_min=count_min, count_max=count_max)),file = args[3])
