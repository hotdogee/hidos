#setwd('C:\\Han\\Work\\Meridigen\\hidos\\tools\\1_6_obj_area_cal')
# "C:\Program Files\R\R-3.2.2\bin\RScript.exe" 1_1_CellM_han.R "171-1 40x_c005_24.96.JPG" "171-1 40x_c005_24.96_out.JPG" "171-1 40x_c005_24.96.json"
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

image_file_path = args[1]

image_file = file.path(image_file_path)
imgc = readImage(image_file)
imgcs = resize(imgc, 1024)

imgc_data = imageData(imgc)

#--------------------------------------
dimens = dim(imgc_data)
imgc_data_var = matrix(0,dimens[1],dimens[2])
for (i in 1:dimens[1] ) {
  for (j in 1:dimens[2] ) {
    imgc_data_var[i,j] = sd(imgc_data[i,j,])
  }
}
thr = 0.05
#-----------------------------------------
img_binary <- ifelse(imgc_data_var<thr,1,0)

kern = makeBrush(3, shape='disc')
nuct3 = dilate(img_binary, kern)

kern = makeBrush(3, shape='disc')
nuct4 = erode(nuct3, kern)

nuclabel3 = bwlabel(nuct4)
nuclabel3_gray<-channel(nuclabel3,"gray")
ratio = length(nuclabel3[nuclabel3<1])/length(nuclabel3)

img_processed = paintObjects(nuclabel3_gray, imgc, col='#ffff00', opac=c(1, 0.4), thick=TRUE, closed=TRUE)
file_name_output = args[2]
writeImage(img_processed,file_name_output, quality=100)

write(toJSON(list(ratio = ratio)),file = args[3])



