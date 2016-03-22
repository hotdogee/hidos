library("stats")
library("graphics")
library("grDevices")
library("utils")
library("datasets")
library("methods")
library("base")
library("EBImage")
library("RJSONIO")
library(rjson)

args <- commandArgs(TRUE)
#print(args)

image_file_path = args[1]

image_file = file.path(image_file_path)
imgc = readImage(image_file)

img_tif_rs = imgc
imgc_blue = channel(img_tif_rs[,,3],'gray')


nuc_th <- ifelse(imgc_blue < 0.05,0,1)
nuc_th = fillHull(nuc_th)

img_bwl <-bwlabel(nuc_th)
RegionProps<-data.frame(table(img_bwl))
RemoveAreaThreshold = 50
idx<-which(RegionProps$Freq < RemoveAreaThreshold) #delete those
obj_idx <- idx-1
img_bwl = rmObjects(img_bwl, obj_idx)


nuc_label = bwlabel(img_bwl)
a = rep(10000,5000)
b = rep(0,5000)
cord_table = cbind(a,a,b,b)

#nuc_label = bwlabel(img_watsh)
h2<-dim(nuc_label)[1]
w2<-dim(nuc_label)[2]
nuc_label_matrix = t(matrix(nuc_label,nrow = h2,ncol = w2))
h3<-dim(nuc_label_matrix)[1]
w3<-dim(nuc_label_matrix)[2]
for (inx_j in c(1:h3)){
  for (inx_i in c(1:w3)){
    
      print_inx = nuc_label_matrix[inx_j,inx_i]
      if (print_inx > 0){
        if(inx_j > cord_table [print_inx,4])
          cord_table[print_inx,4] = inx_j
        if(inx_i > cord_table [print_inx,3])
          cord_table[print_inx,3] = inx_i
      
        if(inx_j < cord_table [print_inx,2])
          cord_table[print_inx,2] = inx_j
        if(inx_i < cord_table [print_inx,1])
          cord_table[print_inx,1] = inx_i
      }
  }
}    
    
cell_count = max(nuc_label)

cord_table_out = matrix(0,cell_count,5)
for (inx_i in c(1:cell_count)){
  
  cord_table_out[inx_i,1] = cord_table[inx_i,1]
  cord_table_out[inx_i,2] = cord_table[inx_i,2]
  cord_table_out[inx_i,3] = cord_table[inx_i,3] - cord_table[inx_i,1]
  cord_table_out[inx_i,4] = cord_table[inx_i,4] - cord_table[inx_i,2]
  cord_table_out[inx_i,5] = sum(nuc_label == inx_i)
  
}



img_processed = paintObjects(img_bwl, imgc, col=c('#FF0000', '#FF0000'), opac=c(1, 0), thick=TRUE, closed=TRUE)
file_name_output = args[2]
writeImage(img_processed,file_name_output, quality=100)

cord_table_data_frame = as.data.frame(cord_table_out)
colnames(cord_table_data_frame) = c('cord_x','cord_y','width','height','size')
writeLines(toJSON(list(count = cell_count, objects = cord_table_data_frame)), args[3])





