#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
#from mpl_toolkits.basemap import cm as cm2
import os
import datetime
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.collections as mc
from matplotlib.collections import LineCollection
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import glob
import datetime
import dateutil.rrule as rrule
from math import radians, cos, sin, asin, sqrt
from scipy.io import netcdf as netcdf
#from pyhdf import SD
from scipy.interpolate import griddata
import netCDF4
from os import listdir
from os.path import isfile, join
import re
import pandas as pd

# ------------------------------------------------------------------------------

def isd_into_kassd(station=['645000'],yearstart=2019,yearend=2020):
    datapath_data = '../data'
    datapath_out  = '../data/output/'
    dummyvar = True

    # variable for output, check order
    variables_synop = 'variable = cloud_height_lowest,cloud_area_fraction_total,cloud_area_fraction_lowest,'+ \
        'cloud_genus_low,cloud_genus_medium,cloud_genus_high,cloud_altitude_1,cloud_fraction_1,cloud_type_1,'+ \
        'cloud_altitude_2,cloud_fraction_2,cloud_type_2,cloud_altitude_3,cloud_fraction_3,cloud_type_3,'+ \
        'cloud_altitude_4,cloud_fraction_4,cloud_type_4,'

    years = [i for i in range(yearstart,yearend)]

    times = []
    for t in range(24):
        times.append('%02d00' % t)
        times.append('%02d10' % t)
        times.append('%02d20' % t)
        times.append('%02d30' % t)
        times.append('%02d40' % t)
        times.append('%02d50' % t)

    # defintions to make
    mk_isd   = False
    mk_metar = False
    mk_synop = True

    fv = -9999		# Fill_Value -> not available
    fv2 = -1111		# Fill_Value -> Unknown Code

    # SYNOP Decode
    # section 1: ground observation
    synoppre = '(REMSYN\d{3}'+station[0:5]+'|REMSYN\d{3}\s*\s?\s?\w{4}\s+\d{5}\s+'+station[0:5]+')'
    synoppre2= '(REMSYN\d{3}333)'    # Old Synop Code
    synoppre3= '(REMSYN\d{3})'    # Old Synop Code
    irixhvv  = '\s*([0-4][0-7][/|\d{1}][/|\d{1}][/|\d{1}])?'
    nddff    = '\s*([/|\d{1}][/|\d{1}][/|\d{1}][/|\d{1}][/|\d{1}])?'
    oofff    = '\s*(00\d{3})?'
    isnttt   = '\s*(1[0|1]\d{3})?'
    iisnttt  = '\s*(2[0|1|9]\d{3})?'
    iiipppp  = '\s*(3\d{3}[\d{1}|/])?'
    ivpppp   = '\s*(4\d{3}[\d{1}|/])?'
    vappp    = '\s*(5\d{4})?'
    virrrtr  = '\s*(6\d{3}[\d{1}|/])?'
    viiwww1w2= '\s*(7\d{4})?'
    nhclcmch = '\s*(8[\d{1}/|/][\d{1}/|/][\d{1}/|/][\d{1}/|/])?'
    ixgggg   = '\s*(9\d{4})?'

    # section 3: climate data
    preiii   = '\s*(333)?'
    prezero  = '\s*(0[\d{1}|/][\d{1}|/][\d{1}|/][\d{1}|/])?'
    isnttt2  = '\s*(1[0|1]\d{3})?'
    iisnttt2 = '\s*(2[0|1|9]\d{3})?'
    iiiesntgt= '\s*(3\d{1}[0|1][\d{1}|/][\d{1}|/])?'
    ivesss   = '\s*(4[\d{1}|/]\d{3})?'
    vvsss    = '\s*(5\d{4})?'
    iiffff   = '\s*(2\d{4})?'
    iiiffff  = '\s*(3\d{4})?'
    ivffff   = '\s*(4\d{4})?'
    vviiiss  = '\s*(553\d{2})?'
    iiffff2  = '\s*(2\d{4})?'
    iiiffff2 = '\s*(3\d{4})?'
    ivffff2  = '\s*(4\d{4})?'
    virrrtr2 = '\s*(6[\d{1}|/][\d{1}|/][\d{1}|/]\[\d{1}|/])?'
    nschshs  = '\s*(8[\d{1}|/][\d{1}|/]\d{2})?'      # up to 4 times
    ixspspsps= '\s*(9\d{4})?'

    # a dummy for not matching patterns
    dummat   = '(99999)?'

    # Synop concatenate
    synop_ex =  synoppre +irixhvv  +nddff    +oofff    +isnttt   +iisnttt  +\
                iiipppp  +ivpppp   +vappp    +virrrtr  +viiwww1w2+nhclcmch +\
                ixgggg   +preiii   +prezero  +isnttt2  +iisnttt2 +iiiesntgt+\
                ivesss   +vvsss    +vvsss    +vvsss    +vvsss    +iiffff   +\
                iiiffff  +ivffff   +vviiiss  +iiffff2  +iiiffff2 +ivffff2  +\
                virrrtr2 +nschshs  +nschshs  +nschshs  +nschshs  +ixspspsps #36
    synop_ex2=  synoppre2+dummat   +dummat   +dummat   +dummat   +dummat   +\
                dummat   +dummat   +dummat   +dummat   +dummat   +dummat   +\
                dummat   +dummat   +ixgggg   +preiii   +prezero  +isnttt2  +\
                ivesss   +vvsss    +vvsss    +vvsss    +vvsss    +iiffff   +\
                iiiffff  +ivffff   +vviiiss  +iiffff2  +iiiffff2 +ivffff2  +\
                virrrtr2 +nschshs  +nschshs  +nschshs  +nschshs  +ixspspsps #36
    synop_ex3=  synoppre3+dummat   +dummat   +dummat   +dummat   +dummat   +\
                dummat   +dummat   +dummat   +dummat   +dummat   +dummat   +\
                dummat   +dummat   +ixgggg   +preiii   +prezero  +isnttt2  +\
                ivesss   +vvsss    +vvsss    +vvsss    +vvsss    +iiffff   +\
                iiiffff  +ivffff   +vviiiss  +iiffff2  +iiiffff2 +ivffff2  +\
                virrrtr2 +nschshs  +nschshs  +nschshs  +nschshs  +ixspspsps #36

                               
    for YY in years: 
        if dummyvar:
            if dummyvar:
                try:
                    filenames = [f for f in listdir(datapath_data+'/%s' % YY) if isfile(join(datapath_data+'/%s' % YY, f)) and '%s' % station in f]
                    print(filenames)
                except:
                    print('for '+str(YY)+' and station '+station+' no files available')
                    continue

                # find name of station id
                stationlist = pd.read_csv('stationlist.py',sep=' ')
                station_name = 'not in list'
                for l in range(len(stationlist)):
                    if station == str(stationlist['stat_id'][l]):
                        station_name = stationlist['name'][l]
                        break
                    else:
                        continue
    
                if not filenames:
                    print(YY,station,'not available')
                    continue
    
                with open('%s/%s' % (datapath_data+'/%s' % YY,filenames[0]),'r') as infile:
                    data = infile.read().splitlines()
                lat = str(data[0][28:34])
                lon = str(data[0][34:41])

                if mk_synop:
                    outfile_syn =  open(datapath_out+'syn_%s_%s.txt' % (station,YY) , 'w')
                    # Create File Header syn
                    outfile_syn.write('station_name = '+station_name+' \nstation_id = '+station[0:5]+ \
                        ' \nlat = '+lat+' \nlon = '+lon+'\n')
                    outfile_syn.write(variables_synop+'\n')
                    outfile_syn.write('m, , , , , ,m, , ,m, , ,m, ,\n')
    		
                date_prev = ''
                time_prev = ''
    		
                # GO through data
    		
                for i_line,line in enumerate(data):
    			
                    date = line[15:23]
                    time = line[23:27]
    			
                    if (date == date_prev and time == time_prev):
                        continue
    			
                    if not time in times:
                        continue
    			
                    # Proof if SYNOP and/or METAR is in
                    synopdata = False
                    if line[41:46] == 'SY-MT':
                        synopdata = True
                    elif line[41:46] == 'FM-12':
                        synopdata = True
                    elif line[41:46] == 'FM-14':
                        synopdata = True
                    elif line[41:46] == 'S-S-A':
                        synopdata = True
                    elif line[41:46] == 'SY-AE':
                        synopdata = True
                    elif line[41:46] == 'SY-AU':
                        synopdata = True
                    elif line[41:46] == 'SY-SA':
                        synopdata = True
    
                    ###############################################################################
                    ################### SYNOP only ################################################
                    ###############################################################################

                    if not mk_synop or not synopdata:
                        continue
                    else:
                        check_SYNOP = ''
                        bla = ''

                        # Check which SYNOP decoder to use
                        case_SYNOP = re.findall('REMSYN\w+',line)
                        check_SYNOP = re.findall(synop_ex,line)
                        if str(check_SYNOP) == '[]':
                            check_SYNOP = re.findall(synop_ex2,line)
                            if str(check_SYNOP) == '[]':
                                check_SYNOP = re.findall(synop_ex3,line)

                        # write date and time
                        if not case_SYNOP:
                            outfile_syn.write(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' '+time[0:2]+':'+time[2:4])
                            outfile_syn.write(('%9s ' % fv)*18)
                        elif re.findall('BUFR',case_SYNOP[0]):
                            outfile_syn.write(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' '+time[0:2]+':'+time[2:4])
                            outfile_syn.write(('%9s ' % fv)*18)
                        elif str(check_SYNOP) == '[]':
                            outfile_syn.write(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' '+time[0:2]+':'+time[2:4])
                            outfile_syn.write(('%9s ' % fv)*18)
                        else:
                            outfile_syn.write(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' '+time[0:2]+':'+time[2:4])
                            # write output synop mask section

    		            # Clouds cover ----------------------------------------------------------------
                            if check_SYNOP[0]:

    			        # Cloud height lowest		
                                if check_SYNOP[0][1]:
                                    chl = check_SYNOP[0][1][2:3]
                                    if chl == '0':
                                        outfile_syn.write('%9s ' % '0')
                                    elif chl == '1':
                                        outfile_syn.write('%9s ' % '50')
                                    elif chl == '2':
                                        outfile_syn.write('%9s ' % '100')
                                    elif chl == '3':
                                        outfile_syn.write('%9s ' % '200')
                                    elif chl == '4':
                                        outfile_syn.write('%9s ' % '300')
                                    elif chl == '5':
                                        outfile_syn.write('%9s ' % '600')
                                    elif chl == '6':
                                        outfile_syn.write('%9s ' % '1000')
                                    elif chl == '7':
                                        outfile_syn.write('%9s ' % '1500')
                                    elif chl == '8':
                                        outfile_syn.write('%9s ' % '2000')
                                    elif chl == '9':
                                        outfile_syn.write('%9s ' % '2500')
                                    else:
                                        outfile_syn.write('%9s ' % fv)
                                else:
                                    outfile_syn.write('%9s ' % fv)

                                # Cloud area fraction total
                                if check_SYNOP[0][2]:
                                    if check_SYNOP[0][2][0:1].isnumeric():
                                        outfile_syn.write('%9s ' % check_SYNOP[0][2][0:1])
                                    else:
                                        outfile_syn.write('%9s ' % fv)
                                else:
                                    outfile_syn.write('%9s ' % fv)

    			        # Cloud fraction and type
                                if check_SYNOP[0][11]:
    			            # Cloud area fraction lowest		
                                    if check_SYNOP[0][11][1:2].isnumeric():
                                        outfile_syn.write('%9s ' % check_SYNOP[0][11][1:2])
                                    else:
                                        outfile_syn.write('%9s ' % fv)

                                    # Cloud genus low
                                    if check_SYNOP[0][11][2:3].isnumeric():
                                        outfile_syn.write('%9s ' % check_SYNOP[0][11][2:3])
                                    else:
                                        outfile_syn.write('%9s ' % fv)

                                    # Cloud genus medium
                                    if check_SYNOP[0][11][3:4].isnumeric():
                                        outfile_syn.write('%9s ' % check_SYNOP[0][11][3:4])
                                    else:
                                        outfile_syn.write('%9s ' % fv)

                                    # Cloud genus high
                                    if check_SYNOP[0][11][4:5].isnumeric():
                                        outfile_syn.write('%9s ' % check_SYNOP[0][11][4:5])
                                    else:
                                        outfile_syn.write('%9s ' % fv)

                                else:
                                    outfile_syn.write(('%9s ' % fv)*4)

    			        # Cloud altidute, fraction, and type up to 4 times(ascending order)		
                                for k in range(31,35):
                                    if check_SYNOP[0][k]:
                                        # Cloud height
                                        clhe = check_SYNOP[0][k][3:5]
                                        if int(clhe[0:2]) < 51:
                                            for i in range(0,51):
                                                if str(i).zfill(2) == clhe:
                                                    outfile_syn.write('%9s ' % str(i*30))
                                                    break
                                                else:
                                                    continue
                                        elif int(clhe[0:2]) < 80 and int(clhe[0:2]) > 49:
                                            for i in range(56,80):
                                                if str(i) == clhe:
                                                    outfile_syn.write('%9s ' % str((i-55)*300+1500))
                                                    break
                                                else:
                                                    continue
                                        elif int(clhe[0:1]) == 8:
                                                for i in range(80,90):
                                                    if str(i) == clhe:
                                                        outfile_syn.write('%9s ' % str((i-80)*1500+9000))
                                                        break
                                                    else:
                                                        continue
                                        elif int(clhe[0:1]) == 9:
                                            if int(clhe) < 93:
                                                outfile_syn.write('%9s ' % str((int(clhe)-90)*50))
                                            elif int(clhe) > 92 and int(clhe) < 95:
                                                outfile_syn.write('%9s ' % str((int(clhe)-91)*100))
                                            elif int(clhe) == 95:
                                                outfile_syn.write('%9s ' % '600')
                                            elif int(clhe) > 95:
                                                outfile_syn.write('%9s ' % str((int(clhe)-94)*500))
                                            else:
                                                outfile_syn.write('%9s ' % fv)
                                        else:
                                            outfile_syn.write('%9s ' % fv)
                                        # Cloud fraction
                                        if check_SYNOP[0][k][1:2].isnumeric():
                                            outfile_syn.write('%9s ' % check_SYNOP[0][k][1:2])
                                        else:
                                            outfile_syn.write('%9s ' % fv)
                                        # Cloud type
                                        if check_SYNOP[0][k][2:3].isnumeric():
                                            outfile_syn.write('%9s ' % check_SYNOP[0][k][2:3])
                                        else:
                                            outfile_syn.write('%9s ' % fv)
    
                                    else:
                                        outfile_syn.write(('%9s ' % fv)*3)

                            else:
                                outfile_syn.write(('%9s ' % fv)*18)


                        outfile_syn.write('\n')
    					

                    # End Line ---------------------------------------------------------------------
    				
                    date_prev = date
                    time_prev = time
    				
                if mk_isd:
                    outfile_syn.close()
