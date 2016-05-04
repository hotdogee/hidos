setwd('/home/irashadow/r_workspace/CellObjIden')
library("EBImage")


image_data_path = '/home/irashadow/r_workspace/data/cell_img_1'

image_out_path = '/home/irashadow/r_workspace/output/cell_img_1'

files_list = list.files(path = image_data_path)

ratio_list = c()


for (item in files_list){

  print(item)
  
  image_file_path = paste0(image_data_path,'/',item)
  
  image_file = file.path(image_file_path)
  imgc = readImage(image_file)

  imgc_gray <- channel(imgc,"gray")

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
  img_processed = paintObjects(nuclabel3_gray, imgc, col='#ff00ff')

  file_name_temp = unlist(strsplit(item, "[.]"))[1]
  
  file_name_output = paste0(image_out_path,"/",file_name_temp,"_p.JPG")
  
  writeImage(img_processed,file_name_output, quality=100)
  
  ratio = length(nuclabel3[nuclabel3>0])/length(nuclabel3)
}

