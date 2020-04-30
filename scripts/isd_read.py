import numpy as np
import os
from os import listdir
from os.path import isfile, join
import re
import pandas as pd
from decode import decodemetar, decodesynop, decodeisd

################################################################################
################################################################################
############## Decode of ISD data inclusive SYNOP and METAR ####################
################################################################################
################################################################################

# The script checks for ISD files in <data>-folder with <year> and decodes them
# if they are available, concatenates the years given you want to decode and
# saves the file in <data>/<output>. Usually it should gzip the files, because
# of loads of redudant values in.

def split_isd_data(station, yearstr, yearend, mk_isd, mk_metar, mk_synop):
    '''
    This function reads ISD data in and writes the data into a metar-, synop-, and/or isd-named file or to write a KASS-D readable file.
    The function is driven from main.py with input variable like years(time range) and station.
    '''
    # define paths to source and target file
    datapath_data = '../data'           # source file
    datapath_out  = '../data/output/'   # target file

    years = np.arange(yearstr,yearend)

    header_SYNOP = ['T','Td','Tmax','Tmin','RH','Wdir','Wspd','Prec','clhlow','clfrtot','clfrlow','clt_l','clt_m','clt_h','clh1','clfr1','clty1','clh2','clfr2','clty2','clh3','clfr3','clty3','clh4','clfr4','clty4']
    header_METAR = ['METwdir','METwspd','METwgst','visib','press','temp','dewp','whe_phe','cc1','ch1','cc2','ch2','cc3','ch3','cc4','ch4']
    header_ISD = ['wind_dir','wind_spd','temp','dtemp','press','Sundur','preci1','precih1','preci2','precih2','preci3','precih3','preci4','precih4','clct','clfl','clgl','clhl','clgm','clgh','ga1clc','ga1clh','ga1clt','ga2clc','ga2clh','ga2clt','ga3clc','ga3clh','ga3clt','ga4clc','ga4clh','ga4clt','ga5clc','ga5clh','ga5clt','ga6clc','ga6clh','ga6clt']
    # header for KASS-D
    variables_synop = 'variable = cloud_height_lowest,cloud_area_fraction_total,cloud_area_fraction_lowest,'+ \
        'cloud_genus_low,cloud_genus_medium,cloud_genus_high,cloud_altitude_1,cloud_fraction_1,cloud_type_1,'+ \
        'cloud_altitude_2,cloud_fraction_2,cloud_type_2,cloud_altitude_3,cloud_fraction_3,cloud_type_3'

                               
    # Which files to create
    if mk_metar:
        outfile_met = open(datapath_out+'met_%s_%s.txt' % (station,str(yearstr)+'_'+str(yearend)) , 'w')
        outfile_met.write('%9s %6s ' % ('Date','Time'))
        outfile_met.write('%6s %6s ' % ('lat:','lon:'))
        # Create File Header met
        for ih in range(len(header_METAR)):
            outfile_met.write('%9s ' % header_METAR[ih])
        outfile_met.write('\n')

    if mk_synop:
        outfile_syn = open(datapath_out+'syn_%s_%s.txt' % (station,str(yearstr)+'_'+str(yearend)) , 'w')
        outfile_syn.write('%9s %6s ' % ('Date','Time'))
        outfile_syn.write('%6s %6s ' % ('lat:','lon:'))
        # Create File Header syn
        for ih in range(len(header_SYNOP)):
            outfile_syn.write('%9s ' % header_SYNOP[ih])
        outfile_syn.write('\n')

    if mk_isd:
        outfile_isd = open(datapath_out+'isd_%s_%s.txt' % (station,str(yearstr)+'_'+str(yearend-1)) , 'w')
        outfile_isd.write('%9s %6s ' % ('Date','Time'))
        outfile_isd.write('%6s %6s ' % ('lat:','lon:'))
        # Create File Header isd
        for ih in range(len(header_ISD)):
            outfile_isd.write('%9s ' % header_ISD[ih])
        outfile_isd.write('\n')


    '''
    RELICT, TRY
                        This is for kassd format
                        if mk_synop:
                            tfile_syn =  open(datapath_out+'syn_%s_%s.txt' % (stat,YY) , 'w')
                          # Create File Header syn
                          outfile_syn.write('station_name = Libreville \nstation_id = '+station[0][0:5]+ \
                           ' \nlat = '+lat+' \nlon = '+lon+'\n')
                        utfile_syn.write(variables_synop+'\n')
                          outfile_syn.write('m, , , , , ,m, , ,m, , ,m, ,\n')
    '''
    
    for YY in years: 
        try:
            filenames = [f for f in listdir(datapath_data+'/%s' % str(YY)) if f == station+'-99999-'+str(YY)]
            print(filenames[0])
        except:
            print('for '+str(YY)+' and station '+station+' no files available')
            continue
        try:
            with open('%s/%s' % (datapath_data+'/%s' % YY,filenames[0]),'r') as infile:
                data = infile.read().splitlines()
        except:
            continue
        lat = data[0][28:34]
        lon = data[0][35:41]
		
        date_prev = ''
        time_prev = ''
		
        # GO through data line by line
        for i_line,line in enumerate(data):
			
            date = line[15:23]
            time = line[23:27]
			
            # Proof if SYNOP and/or METAR is in with the prefix in the ISD code
            metardata = False
            synopdata = False
            if line[41:46] == 'FM-15':
                metardata = True
            elif line[41:46] == 'FM-16':
                metardata = True
            elif line[41:46] == 'SY-MT':
                metardata = True
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
            ############### METAR decoding and writing in met_-file #######################
            ###############################################################################

            if mk_metar and metardata:

                decodemetar(line,date,time,lat,lon,header_METAR,outfile_met)


            ###############################################################################
            ################### SYNOP only ################################################
            ###############################################################################

            if mk_synop and synopdata:

                decodesynop(station,line,date,time,lat,lon,header_SYNOP,outfile_syn)

	
            ###############################################################################
            ################### ISD only ##################################################
            ###############################################################################
            if mk_isd:

                decodeisd(station,line,date,time,lat,lon,header_ISD,outfile_isd,metardata,synopdata)

			
    # End Line ---------------------------------------------------------------------

    if mk_metar:
        outfile_met.close()
    if mk_synop:
        outfile_syn.close()
    if mk_isd:
        outfile_isd.close()
    				
