#!/usr/bin/env python3

import configparser
import datetime
import math
import subprocess
import sys

from netCDF4 import Dataset
from dateutil import parser


def closest(start_dt, lat, lon):
    '''
    read a FLDAS NC file, and figure out what the closest x,y grid point
    is to the give lat,lon
    '''
    best_x = None
    best_y = None
    best_distance = 1000000000
    nc_path = 'FLDAS_NOAH01_A_EA_D.001/%d/%02d/FLDAS_NOAH01_A_EA_D.A%d%02d%02d.001.nc' \
              %(start_dt.year, start_dt.month, start_dt.year, start_dt.month, start_dt.day)
    nc = Dataset(nc_path, 'r')

    dim_x = nc.dimensions['X'].size                                                                 
    dim_y = nc.dimensions['Y'].size   
    for x in range(0, dim_x):
        for y in range(0, dim_y):
            grid_lat = float(nc['Y'][y])
            grid_lon = float(nc['X'][x])
            distance = math.sqrt((lat - grid_lat)**2 + (lon - grid_lon)**2)
            if distance < best_distance:
                best_distance = distance
                best_x = x
                best_y = y

    print("Closest grid point is: x=%d, y=%d (lat=%.2f, lon=%.2f)" \
          %(best_x, best_y, nc['Y'][best_y], nc['X'][best_x]))
    return (best_x, best_y)


def satvp(temp):
    return .6108 * math.exp(17.27 * temp / (temp + 237.3))


def tdew(ea):
    return 237.3 * math.log(ea / 0.6108) / (17.27 - math.log(ea / 0.611))


def ea(patm, q):
    return patm * q / (0.622 * (1 - q) + q)


def add_day(dt, x, y, outf):
    '''
    process one day of FLDAS data and convert it to Cycles input
    '''
    nc_path = 'FLDAS_NOAH01_A_EA_D.001/%d/%02d/FLDAS_NOAH01_A_EA_D.A%d%02d%02d.001.nc' \
              %(dt.year, dt.month, dt.year, dt.month, dt.day)
    print('Opening ' + nc_path)
    nc = Dataset(nc_path, 'r')
    outf.write(dt.strftime('%Y  %j'))
 
    tavg = nc['Tair_f_tavg'][0, x, y] - 273.15
    ea_kPa = ea(nc['Psurf_f_tavg'][0, x, y], nc['Qair_f_tavg'][0, x, y]) / 1000
    rH = ea_kPa / satvp(tavg)
    vpd_ea = satvp(tavg) - ea_kPa
    delta_T = 17.37 * (1 - 1 / (1 + vpd_ea / (0.33 * ea_kPa)))
    Tdew = tdew(ea_kPa)
    
    pp = nc['Rainf_f_tavg'][0, x, y] * 86400
    tx = tavg + .5 * delta_T
    tn = tavg - .5 * delta_T
    solar =  nc['SWdown_f_tavg'][0, x, y] * 86400 / 1000000
    if tn > Tdew:
        rhx = 100 * ea_kPa / satvp(tn)
    else:
        rhx = 99.9
    if tx > Tdew:
        rhn = 100 * ea_kPa / satvp(tx)
    else:
        rhn = 99.8
    wind = nc['Wind_f_tavg'][0, x, y]

    outf.write('  %6.2f  %6.2f  %6.2f  %8.4f  %8.4f %8.4f %6.2f\n' %(pp, tx, tn, solar, rhx, rhn, wind))


def main():

    # weater input is a tarball
    if subprocess.call('tar xzf tar czf weather.tar.gz', shell=True) != 0:
        print("Untaring weather.tar.gz failed")
        sys.exit(1)A

    # get the general configuration from the global mint_run.config
    fp = open('mint_run.config', 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    run_config = configparser.ConfigParser()
    run_config.read_string(config_string)

    # get the model configuration from mint_cycles.config
    fp = open('mint_cycles.config', 'r')
    config_string = '[DEFAULT]\n' + fp.read()
    fp.close()
    config = configparser.ConfigParser()
    config.read_string(config_string)

    start_time = run_config.get('DEFAULT', 'start_time')
    start_dt = parser.parse(start_time)
    end_time = run_config.get('DEFAULT', 'end_time')
    end_dt = parser.parse(end_time)

    lat = config.get('DEFAULT', 'lat')
    lon = config.get('DEFAULT', 'lon')

    # find the FLDAS x,y closest to the lon,lat
    (x, y) = closest(start_dt, float(lat), float(lon))

    fp = open('Cycles.weather', 'w')
    fp.write('LATITUDE %.2f\n' %float(lat))
    # TODO, were do we get altitude and screening height from?
    fp.write('ALTITUDE 590\n')
    fp.write('SCREENING_HEIGHT 2\n')
    fp.write('YEAR  DOY     PP      TX      TN     SOLAR      RHX      RHN     WIND\n')
    
    # now extract daily values for the time range
    dt = start_dt
    while dt <= end_dt:
        add_day(dt, x, y, fp)
        # move on to the next day
        dt = dt + datetime.timedelta(days = 1)

    fp.close()

    if len(sys.argv) > 1:
        subprocess.call('mv Cycles.weather ' + sys.argv[1], shell=True)

main()

