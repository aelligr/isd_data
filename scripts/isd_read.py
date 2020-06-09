import numpy as np
import os
from os import listdir
from os.path import isfile, join
import re
import pandas as pd
from decode import isdread, synopread, metarread
from decode_para import fusedata, writeoutput, fuse_diff_timesteps

################################################################################
################################################################################
############## Decode of ISD data inclusive SYNOP and METAR ####################
################################################################################
################################################################################

# The script checks for ISD files in <data>-folder with <year> and decodes them
# if they are available, concatenates the years given you want to decode and
# saves the file in <data>/<output>. Usually it should gzip the files, because
# of loads of redudant values in.

def split_isd_data(station, yearstr, yearend, mk_isd, mk_meta, csv):
    '''
    This function reads ISD data in and writes the data into a metar-, synop-, and/or isd-named file or to write a KASS-D readable file.
    The function is driven from main.py with input variable like years(time range) and station.
    '''
    # define paths to source and target file
    datapath_data = '../data'           # source file
    datapath_out  = '../data/output/'   # target file

    # define some variables
    years = np.arange(yearstr,yearend)
    fuse_timestep = False
    skip = False
    priority = ['isd','synop','metar']

    # headers
    index = ['wind_dir','wind_spd','wind_gst','temp','dtemp','press','sundur','synwea','synweco1','synweco2','metwe','preci1','precih1','preci2','precih2','preci3','precih3','preci4','precih4','clct','clfl','clgl','clhl','clgm','clgh','ga1clc','ga1clh','ga1clt','ga2clc','ga2clh','ga2clt','ga3clc','ga3clh','ga3clt','ga4clc','ga4clh','ga4clt','ga5clc','ga5clh','ga5clt','ga6clc','ga6clh','ga6clt']
                               
    # Which files to create
    if mk_meta:
        outfile_meta = open(datapath_out+'meta_%s_%s.txt' % (station,str(yearstr)+'_'+str(yearend-1)) , 'w')
        outfile_meta.write('Date,Time,isd,synop,metar,\n')

    if mk_isd:
        outfile_isd = open(datapath_out+'isd_%s_%s.txt' % (station,str(yearstr)+'_'+str(yearend-1)) , 'w')
        if csv:
            outfile_isd.write('Date,Time')
            outfile_isd.write(',lat:,lon:')
            for ih in range(len(index)):
                outfile_isd.write(','+index[ih])
                outfile_isd.write(','+index[ih])
            outfile_isd.write('\n')
        else:
            outfile_isd.write('%9s %6s ' % ('Date','Time'))
            outfile_isd.write('%6s %6s ' % ('lat:','lon:'))
            # Create File Header isd
            for ih in range(len(index)):
                outfile_isd.write('%9s ' % index[ih])
                outfile_isd.write('%9s ' % index[ih])
            outfile_isd.write('\n')

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

            # test for twice the same timestep
            try:
                date_next = data[i_line+1][15:23]
                time_next = data[i_line+1][23:27]
            except:
                data_next = None
                time_next = None
            
            if date_next == date and time_next == time:
                fuse_timestep = True

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

            if mk_meta:
                outfile_meta.write(date+','+time+',1,')
                if synopdata:
                    outfile_meta.write('1,')
                else:
                    outfile_meta.write('0,')
                if metardata:
                    outfile_meta.write('1\n')
                else:
                    outfile_meta.write('0\n')

	
            ###############################################################################
            ################### ISD only ##################################################
            ###############################################################################
            if mk_isd:
                # skip writing output, because next timestep is the same 
                if fuse_timestep:
                    # read and decode isd, synops, and metar information
                    isdser = isdread(line,index)
                    synopser = synopread(line,index,station,i_line)
                    metarser = metarread(line,index,i_line)
                
                    # fuse the three different data sources
                    (series, mask) = fusedata(isdser, synopser, metarser, index, priority)
                    skip = True
                    fuse_timestep = False

                # the same timestep, fuse both and write
                elif skip:      
                    # read and decode isd, synops, and metar information
                    isdser_next = isdread(line,index)
                    synopser_next = synopread(line,index,station,i_line)
                    metarser_next = metarread(line,index,i_line)

                    # fuse the three different data sources and previous timestep
                    (series_next,mask_next) = fusedata(isdser_next, synopser_next, metarser_next, index, priority)
                    (series_fuse, mask) = fuse_diff_timesteps(series, series_next, mask, mask_next, index)

                    # Write date, time, and coords
                    if csv:
                        outfile_isd.write(date+','+time)
                        outfile_isd.write(','+lat+','+lon)
                    else:
                        outfile_isd.write('%9s %6s ' % (date,time))
                        outfile_isd.write('%6s %6s ' % (lat,lon))

                    # Write variables into files
                    for var in index:
                        if var == 'wind_dir' and series[var] == -1.:
                            writeoutput(outfile_isd,'VRB',csv)
                            writeoutput(outfile_isd,mask[var],csv)
                        else:
                            writeoutput(outfile_isd,series_fuse[var],csv)
                            writeoutput(outfile_isd,mask[var],csv)
                    outfile_isd.write('\n')
                    skip = False

                # business as usual
                else:
                    # read and decode isd, synops, and metar information
                    isdser = isdread(line,index)
                    synopser = synopread(line,index,station,i_line)
                    metarser = metarread(line,index,i_line)
                
                    # fuse the three different data sources
                    (series, mask) = fusedata(isdser, synopser, metarser, index, priority)
    
                    # Write date, time, and coords
                    if csv:
                        outfile_isd.write(date+','+time)
                        outfile_isd.write(','+lat+','+lon)
                    else:
                        outfile_isd.write('%9s %6s ' % (date,time))
                        outfile_isd.write('%6s %6s ' % (lat,lon))
                    # Write variables into files
                    for var in index:
                        if var == 'wind_dir' and series[var] == -1.:
                            writeoutput(outfile_isd,'VRB',csv)
                            writeoutput(outfile_isd,mask[var],csv)
                        else:
                            writeoutput(outfile_isd,series[var],csv)
                            writeoutput(outfile_isd,mask[var],csv)
                    outfile_isd.write('\n')

			
    # end writing
    if mk_isd:
        outfile_isd.close()
    if mk_meta:
        outfile_meta.close()
    				
