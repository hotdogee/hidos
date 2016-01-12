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

#image_file_path = "IMG_0168.JPG"
#image_file_path = "IMG_0159.JPG"
#image_file_path = "IMG_0161.JPG"
image_file_path = args[1]

image_file = file.path(image_file_path)
imgc = readImage(image_file)
#y = floodFill(imgc, c(67, 146), 0.5)
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

imgc_p3 = imgc_p1 + imgc_p2
#display(imgc_p3)

kern = makeBrush(7, shape='diamond')
nuct3 = dilate(imgc_p3, kern)

nuct4 = fillHull(nuct3)

kern = makeBrush(11, shape='disc')
nuct5 = erode(nuct4, kern)
#display(nuct5)

nuclabel3 = bwlabel(nuct5)

imgc_o = thresh(imgc_gray)
imgc_1o = imgc_p1 + imgc_o
h1 = imgc_1o * -1 + 1
kern = makeBrush(3, shape='disc')
h2 = dilate(h1, kern)
h3 = h2 * -1 + 1
kern = makeBrush(3, shape='disc')
h4 = fillHull(dilate(h3, kern))
h5 = erode(h4, kern)
h6 = bwlabel(h5)
ftrs = computeFeatures.shape(h6)
id <- which(ftrs[, 's.area']>mean(ftrs[, 's.area']))
h6[is.na(match(h6, id))] <- 0
#h7 <- distmap(h6)
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


#-------------------
accepted
The focal() function in the raster package is designed for calculations like this. The following code returns coordinates of all local maxima, including those on edges and those that are parts of "plateaus ".
library(raster)
wt <- watershed(dx)
display(normalize(wt))
display(normalize(wt))
gelwsh02 <- watershed(dx, tolerance=0.2)
gelwsh10 <- watershed(dx, tolerance=1)
gelwsh40 <- watershed(dx, tolerance=4)
gelresult <- EBImage::combine(normalize(gelwsh02),
                     normalize(gelwsh10),
                     normalize(gelwsh40))
display(normalize(gelwsh02))
display(normalize(gelwsh40))
display(gelwsh40)
peaks <- findPeaks(dx)
findPeaks <- function(img) {
  mask <- img > 0
  m1 <- matrix(c(0, 0, 0, -1, 1, 0, 0, 0, 0), 3, 3, byrow=TRUE)
  m2 <- matrix(c(0, -1, 0, 0, 1, 0, 0, 0, 0), 3, 3, byrow=TRUE)
  m3 <- matrix(c(0, 0, 0, 0, 1, 0, 0, -1, 0), 3, 3, byrow=TRUE)
  m4 <- matrix(c(0, 0, 0, 0, 1, -1, 0, 0, 0), 3, 3, byrow=TRUE)
  peak1 <- filter2(img, m1)
  peak2 <- filter2(img, m2)
  peak3 <- filter2(img, m3)
  peak4 <- filter2(img, m4)
  peak1 <- peak1 > 0
  peak2 <- peak2 > 0
  peak3 <- peak3 > 0
  peak4 <- peak4 > 0
  img1234 <- peak1 & peak2 & peak3 & peak4
  img1234*mask
}
peaks <- findPeaks(dx)
display(normalize(peaks), "Peaks")
seg1 <- propagate(nuct5, bwlabel(peaks), nuct5)
display(normalize(seg1), "Segmentaion by Voronoi")
ftrs <- hullFeatures(nuct5)
ftrs = computeFeatures.shape(nuct5)
id <- which(ftrs[, 'g.acirc']<0.05 & ftrs[, 'g.pdm']>2)
ftrs[, 'g.acirc']
ftrs[, ]
ftrs
ftrs = computeFeatures.shape(nuct5, properties=TRUE)
ftrs
nuclabel3 = bwlabel(nuct5)
ftrs = computeFeatures.shape(nuclabel3)
ftrs
id <- which(ftrs[, 's.area']<100 & ftrs[, 's.radius.mean']<10)
display(shapesl, "Obal objects")
display(nuclabel3, "Obal objects")
nuclabel3[is.na(match(nuclabel3, id))] <- 0
display(nuclabel3, "Obal objects")
nuclabel3 = bwlabel(nuct5)
id <- which(ftrs[, 's.area']>100 & ftrs[, 's.radius.mean']>10)
nuclabel3[is.na(match(nuclabel3, id))] <- 0
display(nuclabel3, "Obal objects")
w <- distmap(nuclabel3)
gelwsh40 <- watershed(w, tolerance=4)
display(gelwsh40)
display(normalize(gelwsh40))
ftrs[, 's.area']
mean(ftrs[, 's.area'])
sd(ftrs[, 's.area'])
mean(ftrs[, 's.radius.mean'])
id <- which(ftrs[, 's.area']>mean(ftrs[, 's.area']) & ftrs[, 's.radius.mean']>mean(ftrs[, 's.radius.mean']))
nuclabel3 = bwlabel(nuct5)
nuclabel3[is.na(match(nuclabel3, id))] <- 0
display(nuclabel3, "Obal objects")
w <- distmap(nuclabel3)
gelwsh40 <- watershed(w, tolerance=4)
display(normalize(gelwsh40))
ftrs = computeFeatures.shape(gelwsh40)
ftrs
id <- which(ftrs[, 's.area']>mean(ftrs[, 's.area']) & ftrs[, 's.radius.mean']>mean(ftrs[, 's.radius.mean']))
nuclabel3 = bwlabel(nuct5)
nuclabel3[is.na(match(nuclabel3, id))] <- 0
display(nuclabel3, "Obal objects")
mean(ftrs[, 's.area']
)
mean(ftrs[, 's.radius.mean'])
sd(ftrs[, 's.area'])
id <- which(ftrs[, 's.area']>(mean(ftrs[, 's.area'])-sd(ftrs[, 's.area'])))
nuclabel3 = bwlabel(nuct5)
nuclabel3[is.na(match(nuclabel3, id))] <- 0
display(nuclabel3, "Obal objects")
sd
id
w <- distmap(nuclabel3)
gelwsh40 <- watershed(w, tolerance=4)
display(normalize(gelwsh40))
nuclabel3 = bwlabel(nuct5)
display(nuclabel3, "Obal objects")
nuclabel3[is.na(match(nuclabel3, id))] <- 0
display(nuclabel3, "Obal objects")
is.na(match(nuclabel3, id))
match(nuclabel3, id)
history
history()
history(100)
history(100)

h6 = bwlabel(h5)