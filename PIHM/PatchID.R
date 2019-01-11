#!/usr/bin/env Rscript

"
Code to read all triangles/cells/elements from Cell shape file.
Tranform coodinates into latitude and longitudes and filter results for elements where land cover type as Cropland.
"

require('rgdal')
require('rgeos')
require('sp')
require(zoo)
require(xts)
require(abind)
require(ncdf4)
library(raster)
library(xts)

# Land Cover: Cropland: 12
ilc = 12

x.pcs = readOGR('ModelInfo/GISlayer/Cells.shp');
x.gcs = spTransform(x.pcs, CRSargs(CRS("+init=epsg:4326")))
DF <- as.data.frame(x.gcs)

ll = coordinates(x.gcs)
# ll

DF$X_c = ll[,1]
DF$Y_c = ll[,2]
DF$SP_ID = as.numeric(DF$SP_ID)

DF = subset(DF, LC == ilc)

write.csv(DF, file = "for-cycles.csv", row.names=F)
