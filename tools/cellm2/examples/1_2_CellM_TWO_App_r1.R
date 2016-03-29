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
  img_tif = readImage(image_file_path)
  
  img_tif_gray <- channel(img_tif,"gray")
  
  rsize_pixel = 256
  
  center_shft =rsize_pixel/5
  
  img_tif_rs = resize(img_tif_gray, rsize_pixel)  
  img_tif_rs[img_tif_rs>1] = 1 
  
  imgc_gray_mean = mean(img_tif_rs)
  
  img_tif_rs_intensity = img_tif_rs - (mean(img_tif_rs) - 0.3)
  
  #background processing ...
  hist_save <- hist(c(img_tif_rs),breaks=100,plot= FALSE, axes=FALSE)

  ValueOfBin = hist_save$breaks
  GrowthOfHist = hist_save$counts
  
  InxBegin = 50
  for(inx in 1:length(ValueOfBin)){
    if(ValueOfBin[inx] > mean(img_tif_rs)) {
      InxBegin = inx
      break
    }  
  }
  
  
  if (InxBegin > length(GrowthOfHist)){
    InxBegin = length(GrowthOfHist)
  }
  
  ValleyPoint = ValueOfBin[InxBegin] 
  
  hist_max_min_record = matrix(0,ncol = 2, nrow = length(GrowthOfHist))
  hist_max_min_inx_record = matrix(0,ncol = 2, nrow = length(GrowthOfHist))
  max_value = 0
  min_value = 100000
  inx_temp1 = 0
  max_inx = 50
  min_inx = 50
  meanGrowth = 0
  
  for(inx in InxBegin:-1:1){  
    
    
     if (inx > 3){
        meanGrowth = mean(GrowthOfHist[(inx-3):(inx-1)])
     }
     nextGrowthRate = (meanGrowth-GrowthOfHist[inx])/(GrowthOfHist[inx]+0.00001)
     
     if ((GrowthOfHist[inx] > max_value)){
        max_value = GrowthOfHist[inx]
        inx_temp1 = inx_temp1 + 1 
        max_inx = inx
        hist_max_min_record[inx_temp1,1] = max_value
        hist_max_min_record[inx_temp1,2] = min_value
        hist_max_min_inx_record[inx_temp1,1] = max_inx
        hist_max_min_inx_record[inx_temp1,2] = min_inx
     }
    if ((GrowthOfHist[inx] < min_value) & (nextGrowthRate > 0.1)){
       min_value = GrowthOfHist[inx]
       min_inx = inx
     }
  }  
  
  valley_inx = hist_max_min_inx_record[inx_temp1,2]
  #valley_inx = hist_max_min_inx_record[inx_temp1,1] + 3
  
  ValleyPoint = ValueOfBin[valley_inx] 
  

  img_binary1 <- ifelse(img_tif_rs < ValleyPoint,0,1)

  kern = makeBrush(3, shape='disc')
  p1 = dilate(img_binary1, kern)
  kern = makeBrush(3, shape='disc')
  p2 = erode(p1, kern)
  
  # fill Hull process-----------------------------------
  # swap one and zero
  p2[p2 >1] = 1 
  p2 = p2 + 1  
  p2[p2 >1] = 0 
  #display(p2)
  img_bwl <-bwlabel(p2)

  RegionProps<-data.frame(table(img_bwl))
  RemoveAreaThreshold = 500
  idx<-which(RegionProps$Freq < RemoveAreaThreshold) #delete those
  obj_idx <- idx-1
  img_bwl = rmObjects(img_bwl, obj_idx)
  #display(img_bwl)
  # swap one and zero
  img_bwl[img_bwl >1] = 1 
  img_bwl = img_bwl + 1  
  img_bwl[img_bwl >1] = 0 
  img_binary2 <- img_bwl
  #display(channel(img_binary2, 'rgb'))
  #----------------------------------------------------
  
  #remove small objects--------------------------------
  img_bwl <-bwlabel(img_binary2)
  
  RegionProps<-data.frame(table(img_bwl))
  RemoveAreaThreshold = 5000
  idx<-which(RegionProps$Freq < RemoveAreaThreshold) #delete those
  obj_idx <- idx-1
  
  img_bwl = rmObjects(img_bwl, obj_idx)
  img_binary3 <- img_bwl
  
  
  #----------------------------------------------------
  
  img_binary2_t = t(img_binary3)

  #Ray scanner horizontal 
  col_sum = colSums(img_binary2_t[center_shft:(rsize_pixel-center_shft),center_shft:(rsize_pixel-center_shft)], na.rm = FALSE, dims = 1)
  col_center = mean(sort.list(col_sum)[1:30])
  
  row_sum = rowSums(img_binary2_t[center_shft:(rsize_pixel-center_shft),center_shft:(rsize_pixel-center_shft)], na.rm = FALSE, dims = 1)
  row_center = mean(sort.list(row_sum)[1:30])
  
  
  #center parameter is very important, sort.list(row_sum)[1:20] for h22  
  center_radius = 75
  
 
  matrix_new = matrix(1, nrow = rsize_pixel, ncol = rsize_pixel)
  center_lattice = drawCircle(matrix_new, center_shft+col_center, center_shft+row_center, center_radius+15, col=0, fill=TRUE)
  
  #Ray scanner horizontal 
  contour_pattern<-channel(center_lattice+img_binary3,"gray")
  contour_pattern[contour_pattern>1] = 1
  
  
 
  #-----OUTPUT------------------------------------------------
  img_processed = paintObjects(resize(contour_pattern,dim(img_tif_gray)[1],dim(img_tif_gray)[2]), channel(img_tif_gray, 'rgb'), col='#ffff00')
  ratio = length(contour_pattern[contour_pattern<1])/length(contour_pattern)
  pixel_count = as.integer(ratio*dim(img_tif_gray)[1]*dim(img_tif_gray)[2]) 
  
  file_name_output = args[2]
  writeImage(img_processed,file_name_output, quality=100)
  

  write(toJSON(list(ratio = ratio, pixel_count = pixel_count, dim_x = dim(img_tif_gray)[1], dim_y = dim(img_tif_gray)[2])),file = args[3])
