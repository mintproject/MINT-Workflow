#!/usr/bin/env Rscript

require(zoo)
require(xts)
require(abind)
require(ncdf4)
library(raster)
library(rgdal)
library(rgeos)
library(sp)
library(xts)


readnc<-function(fn, xyid=c(1,1), vns=NULL){
  fid= nc_open(fn)
  
  if(is.null(vns)){
    vns = names(fid$var)
    vns = vns[!(vns %in% 'time_bnds')] # don't need the time_bnds
  }
  
  nv = length(vns)
  x.mat = matrix(0, ncol=nv, nrow=ns)
  
  for(i in 1:nv){  #reading file
    vn=vns[i]
    mat=ncvar_get(fid, vn)
    x.v = mat[xyid]
    x.mat[,i] = x.v
  }
  colnames(x.mat) = vns
  nc_close(fid)
  x.mat
}


writeshape <- function(shp, file=NULL){
  if( is.null(file) ){
    message('No file exported')
  }else{
    path = dirname(file)
    fn = basename(file)
    if(!dir.exists(path)){
      dir.create(path, showWarnings = T, recursive = T)
    }
    
    prj = sp::proj4string(shp)
    writeOGR(obj=shp, driver = 'ESRI Shapefile',
             layer=fn,
             dsn=path, overwrite_layer = T)
    if( !is.na(crs(shp))){
      fn.prj = file;
      raster::extension(fn.prj) = '.prj'
      invisible(rgdal::showWKT(prj, file = fn.prj))
    }
    message(file, ' is exported')
  }
}
add.df <- function(x){
  df=data.frame('ID'=1:length(x)); 
  row.names(df) = row.names(x)
  xx=SpatialPolygonsDataFrame(x,  data=df)
  xx
}


rplot<-raster::plot
saveraster<- function(x, fn='x'){
  message('Writing ', fn)
  raster::writeRaster(x, paste0(fn,'.asc'), overwrite=T)
  rgdal::showWKT(sp::proj4string(x), file = paste0(fn,'.prj'))
}

rep.row<-function(x,n){
  for(i in 1:n){
    if(i==1){
      ret = x;
    }else{
      ret=rbind(ret, x)
    }
  }
  return(ret)
}

rep.col<-function(x,n){
  for(i in 1:n){
    if(i==1){
      ret = x;
    }else{
      ret=cbind(ret, x)
    }
  }
  return(ret)
}

fun.toForc <- function (x,lxy,years = 2001:2017,
                       path='./',
                       forc.name ='pihm.forc',
                       lc=1:14,
                       cns

){
  #    x
  #    years = 1979:2015
  #    path='./'
  #    forc.name ='PIHM.forc'
  #    pihmver=2.2
  #
  require(xts)
  if( !dir.exists(path)){
    dir.create(path, recursive = T, showWarnings = F)
  }
  nsites = length(x)
  vnames = names(x)
  tts=time(x[[1]])
  ts.yr = as.numeric(format(tts, '%Y'))
  ts=tts[ts.yr %in% years]
  print(range(ts))
  pb <- txtProgressBar(min=0, max=nsites)
  for (i in 1:nsites){
    #    message(i, '/', nsites, '\t', vnames[i]);
    setTxtProgressBar(pb, i)
    if (i==1){
      prcp = x[[i]][ts,cns[1]]
      temp = x[[i]][ts,cns[2]]
      SH   = x[[i]][ts,cns[3]]
      winds =x[[i]][ts,cns[4]]
      solar = x[[i]][ts,cns[5]]
      longw = x[[i]][ts,cns[6]]
      press = x[[i]][ts,cns[7]]
    }else{
      prcp = cbind(prcp, x[[i]][ts,cns[1]])
      temp = cbind(temp, x[[i]][ts,cns[2]])
      SH   = cbind(SH, x[[i]][ts,cns[3]])
      winds = cbind(winds,x[[i]][ts,cns[4]])
      solar = cbind(solar, x[[i]][ts,cns[5]])
      longw = cbind(longw, x[[i]][ts,cns[6]])
      press = cbind(press, x[[i]][ts,cns[7]])
    }
  }
  close(pb)

  names(prcp  ) = vnames
  names(temp  ) = vnames
  names(SH) = vnames
  names(winds ) = vnames
  names(solar ) = vnames
  names(longw ) = vnames
  names(press ) = vnames
  t0=273.15
  rh = 0.263*press*SH/exp(17.67 * (temp - t0) /(temp - 29.65) ) # specific hum to relative hum
  #  Forcing<-list('PRCP'  =    prcp / 3600   , #hourly to per second
  #                'SFCTMP'=    temp    ,
  #                'RH'    =    rh  ,
  #                'SFCSPD'=    winds   ,
  #                'SOLAR' =    solar   ,
  #                'LONGWV'=    longw   ,
  #                'PRES'  =    press ,
  #                'NumMeteoTS'=nsites);
  #
  mettab = data.frame(1:length(vnames), vnames)
  colnames(mettab) = c('INDEX', 'NLDAS_ID')
  write.table(file='NLDAS_ID.csv',x=mettab, quote=FALSE, row.names=FALSE, col.names=TRUE)

  message('Writing Forcing')
  #writeforc(Forcing, path=path, filename=forc.name)

  ns = ncol(prcp)
  nlc=length(lc)
  lr=fun.LaiRf(lc=lc, years=years)
  mf=fun.MeltFactor(years=years)

  forcnames = c( "Precip", "Temp", "RH", "Wind", "RN",
                 "G","LW", "LAI", "MF", "SS" )
  Forc<-list(   prcp * 86400/1000   , #mm/m2/s(FLDAS daily) to m/day (PIHM).
                temp -273.15   , # C
                rh/100  ,  # PERCENTAGE
                abs(winds) * 86400  , #m/s to m/day
                solar *24 *3600  , #
                0 ,
                0, #longw  *24 *3600  ,
                lr,
                mf,
                0);
  hd = c(ns, ns, ns, ns,ns,0,0, nlc,  1, 0)
  theFile = file.path(path, forc.name)
  names(Forc) = forcnames
  nf= length(forcnames)

  write(x=hd,file=theFile , append=FALSE, ncolumns=nf)

  for(i in 1:7){
    dat = Forc[[i]];
    vn =  forcnames[i]
    if(hd[i] <=0){
      next;
    }
    message('Writing ', vn, '...')
    t = time(dat)
    t0 = t[-(length(t) )]
    t1 = t[-1];
    dt = as.numeric(difftime(t1, t0, units='days'))
    #    dt1 = as.numeric(difftime(round(t[1], units='hours'), 
    #                              round(t[1], units='days'),
    #                              , units='days')) 

    dt=c(dt[1], dt)
    tt=cumsum( dt)

    pb <- txtProgressBar(min=0, max=hd[i])
    for( j in 1:hd[i]){

      setTxtProgressBar(pb, j)
      if(grepl('wind', tolower(vn)) ){
        subhd= c(vn, j, length(t) * 2, 10)
        nc = 4
      }else{
        subhd= c(vn, j, length(t) * 2)
        nc=3
      }
      write(x=subhd, file=theFile , append=TRUE, ncolumns=nc)
      mat = rbind( tt-dt, as.numeric(dat[t,j]),
                   tt, as.numeric(dat[t,j]))
      write(x=mat,file=theFile , append=TRUE, ncolumns=4)
    }
    close(pb)
  }
  i=8
  vn='LAI'
  dat = Forc[[i]]$LAI;
  message('Writing ', vn, '...')
  t = time(dat)
  t0 = t[-(length(t) )]
  t1 = t[-1];
  dt = as.numeric(difftime(t1, t0, units='days'))
  tt=cumsum(dt)

  for( j in 1:hd[i]){
    message(j, '/', hd[i] )
    subhd= c(vn, j,  length(t0) * 2 , 0.0002)
    write(x=subhd, file=theFile , append=TRUE, ncolumns=4)
    mat = rbind( tt-dt, as.numeric(dat[t0,j]),
                 tt, as.numeric(dat[t1,j]))
    write(x=mat, file=theFile , append=TRUE, ncolumns=4)
  }
  vn='Rough'
  dat = Forc[[i]]$Rough;
  message('Writing ', vn, '...')
  t = time(dat)
  t0 = t[-(length(t) )]
  t1 = t[-1];
  dt = as.numeric(difftime(t1, t0, units='days'))
  tt=cumsum(dt)
  for( j in 1:hd[i]){
    message(j, '/', hd[i] )
    subhd= c(vn, j, length(t0) * 2)
    write(x=subhd, file=theFile , append=TRUE, ncolumns=3)
    mat = rbind( tt-dt, as.numeric(dat[t0,j]),
                 tt, as.numeric(dat[t1,j]))
    write(x=mat, file=theFile , append=TRUE, ncolumns=4)
  }
  i=9
  vn='MF'
  dat = Forc[[i]];
  message('Writing ', vn, '...')
  t = time(dat)
  t0 = t[-(length(t) )]
  t1 = t[-1];
  dt = as.numeric(difftime(t1, t0, units='days'))
  tt=cumsum(dt)
  for( j in 1:hd[i]){
    message(j, '/', hd[i] )
    subhd= c(vn, j,  length(t0) * 2 )
    write(x=subhd, file=theFile , append=TRUE, ncolumns=3)
    mat = rbind( tt-dt, as.numeric(dat[t0,j]),
                 tt, as.numeric(dat[t1,j]))
    write(x=mat,file=theFile , append=TRUE, ncolumns=4)
  }

}


cfun <- function (x,tab, type=1) {                                                                  
  #Source: http://www.pihm.psu.edu/EstimationofVegitationParameters.htm                             
  dlai=rbind(c( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),                                                
             c(   8.76,  9.16,  9.827,  10.093,  10.36,  10.76,  10.493,  10.227,  10.093,  9.827,  9.16,  8.76),                                                                                       
             c(   5.117,  5.117,  5.117,  5.117,  5.117,  5.117,  5.117,  5.117,  5.117,  5.117,  5.117,  5.117),                                                                                       
             c(    8.76,  9.16,  9.827,  10.093,  10.36,  10.76,  10.493,  10.227,  10.093,  9.827,  9.16,  8.76),
             c(    0.52,  0.52,  0.867,  2.107,  4.507,  6.773,  7.173,  6.507,  5.04,  2.173,  0.867,  0.52),
             c(    4.64,  4.84,  5.347,  6.1,  7.4335,  8.7665,  8.833,  8.367,  7.5665,  6,  5.0135,  4.64),
             c(    5.276088,  5.528588,  6.006132,  6.4425972,  7.2448806,  8.3639474,  8.540044,  8.126544,  7.2533006,  6.3291908,  5.6258086,  5.300508),
             c(   2.3331824,  2.4821116,  2.7266101,  3.0330155,  3.8849492,  5.5212224,  6.2395131,  5.7733017,  4.1556703,  3.1274641,  2.6180116,  2.4039116 ),
             c(   0.580555,  0.6290065,  0.628558,  0.628546,  0.919255,  1.7685454,  2.5506969,  2.5535975,  1.7286418,  0.9703975,  0.726358,  0.6290065 ),
             c(    0.3999679,  0.4043968,  0.3138257,  0.2232945,  0.2498679,  0.3300675,  0.4323964,  0.7999234,  1.1668827,  0.7977234,  0.5038257,  0.4043968),
             c(    0.782,  0.893,  1.004,  1.116,  1.782,  3.671,  4.782,  4.227,  2.004,  1.227,  1.004,  0.893),
             c(    0.782,  0.893,  1.004,  1.116,  1.782,  3.671,  4.782,  4.227,  2.004,  1.227,  1.004,  0.893),
             c(   0.001,  0.001,  0.001,  0.001,  0.001,  0.001,  0.001,  0.001,  0.001,  0.001,  0.001,  0.001 ),
             c(    1.2867143,  1.3945997,  1.5506977,  1.7727263,  2.5190228,  4.1367678,  5.0212291,  4.5795799,  2.8484358,  1.8856229,  1.5178736,  1.3656797)
  );
  drl=rbind(c(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            c(  1.112, 1.103, 1.088, 1.082, 1.076, 1.068, 1.073, 1.079, 1.082, 1.088, 1.103, 1.112),
            c(  2.653, 2.653, 2.653, 2.653, 2.653, 2.653, 2.653, 2.653, 2.653, 2.653, 2.653, 2.653),
            c(  1.112, 1.103, 1.088, 1.082, 1.076, 1.068, 1.073, 1.079, 1.082, 1.088, 1.103, 1.112),
            c(  0.52, 0.52, 0.666, 0.91, 1.031, 1.044, 1.042, 1.037, 1.036, 0.917, 0.666, 0.52),
            c(  0.816, 0.8115, 0.877, 0.996, 1.0535, 1.056, 1.0575, 1.058, 1.059, 1.0025, 0.8845, 0.816),
            c(  0.7602524, 0.7551426, 0.7772204, 0.8250124, 0.846955, 0.8449668, 0.8471342, 0.8496604, 0.8514252, 0.8299022, 0.7857734, 0.7602744),
            c(  0.35090494, 0.34920916, 0.36891486, 0.40567288, 0.42336056, 0.42338372, 0.42328378, 0.42485112, 0.42631836, 0.40881268, 0.37218526, 0.35096866),
            c(  0.05641527, 0.05645892, 0.05557872, 0.05430207, 0.05425842, 0.05399002, 0.05361482, 0.0572041, 0.05892068, 0.05821407, 0.05709462, 0.05645892),
            c(  0.03699235, 0.03699634, 0.03528634, 0.03272533, 0.03272134, 0.03270066, 0.03268178, 0.03907616, 0.04149324, 0.04032533, 0.03823134, 0.03699634),
            c(  0.0777, 0.0778, 0.0778, 0.0779, 0.0778, 0.0771, 0.0759, 0.0766, 0.0778, 0.0779, 0.0778, 0.0778),
            c(  0.0777, 0.0778, 0.0778, 0.0779, 0.0778, 0.0771, 0.0759, 0.0766, 0.0778, 0.0779, 0.0778, 0.0778),
            c(  0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112, 0.0112),
            c(  0.1947138, 0.19413424, 0.20831414, 0.23348558, 0.24574614, 0.24605016, 0.24538258, 0.24630454, 0.247455, 0.23527388, 0.20963734, 0.19478494)
  );
  if(missing('tab') ){     #undefined table, use the default table.
    tab=switch(type,'lai'=dlai, 'rl'=drl)
  }
  ret = tab[x,]
}



fun.LaiRf <- function(lc,years=2000+1:2, if.daily=FALSE){
  #years=2000:(2010+1);
  years=sort(c(years,max(years)+1))
  yrlim=range(years);
  ny = length(years)
  t1=as.Date(paste(yrlim[1],'-01-01',sep=''))
  t2=as.Date(paste(yrlim[2],'-12-31',sep=''))
  tdaily = seq.Date(t1,t2,by=1)
  DataDaily=xts::as.xts(numeric(length(tdaily)),order.by=tdaily)
  DataMon=xts::apply.monthly(DataDaily,FUN=sum)
  tmon =as.Date( format(time(DataMon), "%Y-%m-01"))
  #tmon = time(DataMon)- days_in_month(time(DataMon))+1
  nlc=length(lc)
  l = matrix(0, nrow=12, ncol=nlc)
  r = matrix(0, nrow=12, ncol=nlc)
  for (i in 1:nlc){
    l[,i] = cfun(lc[i], type=1)
    r[,i] = cfun(lc[i], type=2)
  }
  lmat = xts::as.xts(rep.row(l, ny), order.by=tmon)
  rmat = xts::as.xts(rep.row(r, ny), order.by=tmon)
  colnames(lmat)=lc
  colnames(rmat)=lc
  ret=list('LAI'=lmat, 'Rough'=rmat)
  if(if.daily){
    ld = NA*rep.col(DataDaily, nlc);
    rd = NA*rep.col(DataDaily, nlc);
    ld[time(lmat),]=lmat
    rd[time(rmat),]=rmat
    ld=na.approx(ld)
    rd=na.approx(ld)
    colnames(ld)=lc
    colnames(rd)=lc
    ret=list('LAI'=ld, 'Rough'=rd)
  }
  return(ret)
}

fun.MeltFactor <- function(years=2000+1:2){
  mf=c(0.001308019, 0.001633298,  0.002131198, 0.002632776, 0.003031171,  0.003197325, 0.003095839, 0.00274524,     0.002260213, 0.001759481, 0.001373646,  0.001202083);
  years=sort(c(years,max(years)+1))
  yrlim=range(years);
  ny = length(years)
  t1=as.Date(paste(yrlim[1],'-01-01',sep=''))
  t2=as.Date(paste(yrlim[2],'-12-31',sep=''))
  tdaily = seq.Date(t1,t2,by=1)
  DataDaily=as.xts(numeric(length(tdaily)),order.by=tdaily)
  DataMon=apply.monthly(DataDaily,FUN=sum)
  #tmon = time(DataMon)- days_in_month(time(DataMon))+1
  tmon =as.Date( format(time(DataMon), "%Y-%m-01"))
  ret = as.xts(rep(mf, ny), order.by=tmon)
  ret
}

fun.vegtable <- function (lc, file){
  x=read.csv(file='lc_table.csv', header = T)
  y = x[lc,1:8]
  nr = nrow(y)
  write(nr, file=file, append = F)
  write.table(y, file=file, append=T,  row.names = F, col.names = F, quote = F)
  y
}


wdir = 'FLDAS_NOAH01_A_EA_D.001/'
fl=read.csv('PIHM-base/GISdata/Forcing/FLDAS_grids.csv')

years=2017
dirs = file.path(wdir, years)

ndir = length(dirs)
fn=list.files(wdir, pattern=glob2rx('*.nc'), recursive = T, full.names = T)[1]


fid=nc_open(fn)
xloc = round(fid$dim$X$vals,2)
yloc = round(fid$dim$Y$vals, 2)
nx=length(xloc)
ny = length(yloc)

#===================================================
xc = fl[,'xcenter']
yc = fl[,'ycenter']

xid = match(xc, xloc)
yid = match(yc, yloc)
xyid=cbind(xid,yid)

sn = paste0('X',xc*100, 'Y', yc*100)
ns = length(sn)

vns = names(fid$var)
vns = vns[!(vns %in% 'time_bnds')] # don't need the time_bnds
nv=length(vns)
for(idd  in 1:ndir){ # for each year dir
  cdir <- dirs[idd]
  fns = list.files(cdir, pattern=glob2rx('*.nc'), recursive = T, full.names = T)
  nf = length(fns)
  x.arr = array(0, dim=c(ns, nv, nf) )
  x.t= character(nf)
  for(j  in 1:nf){  # files in each year
    fn=fns[j]
    t=substr(basename(fn), 22, 29)
    message(j, '/', nf, '\t', t)
    x.mat = readnc(fn, xyid=xyid, vns=vns)
    x.t[j] = t
    x.arr[,,j ] = x.mat 
  }
  dimnames(x.arr) = list(sn, vns,  x.t)
  
  fn.rds = file.path('./', paste0('weather-', basename(cdir), '.RDS'))
  saveRDS(x.arr, file=fn.rds)
}


ddir = '.'
dem = raster('PIHM-base/GISdata/DEM/dem.asc')
cns = c('Rainf_f_tavg', 'Tair_f_tavg','Qair_f_tavg',
        'Wind_f_tavg', 'Swnet_tavg','Lwnet_tavg',
        'Psurf_f_tavg')
forcnames = c( "Precip", "Temp", "RH",
               "Wind", "RN","G",
               "VP", "LAI", "MF",
               "SS" )
fns = list.files(ddir, pattern=glob2rx('*.RDS'), full.names = T )
nf=length(fns)
i=1
for(i in 1:nf){
  x=readRDS(fns[i])
  message(i,'/', nf, '\t', basename(fns[i]))
  y=x[,cns,]
  if(i==1){
    dat = y
  }else{
    dat=abind::abind(dat, y, along=3)
  }
}
dn = dimnames(dat)
nd = dim(dat)
xl = list()
time = as.Date(dimnames(dat)[[3]],'%Y%m%d')
for(i in 1:nd[1]){
  message(i,'/', nd[1], '\t', dn[[1]][i] )
  x = t( dat[i,,] )
  xl[[i]]=as.xts(x, order.by=time)
}

names(xl) = dn[[1]]
fun.toForc(xl, years=years, cns=cns)


