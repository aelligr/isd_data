import numpy as np
import os
from os import listdir
from os.path import isfile, join
import re
import pandas as pd
from decode_para import windmetar, skycondition, cloudheight333, cloudheightlowestlist, windsynop

################################################################################
######## Some pre definitions for SYNOP and METAR ##############################
################################################################################

# Definition of the possible expressions in the ISD code(regular expression)
# METAR definitions
metarpre = '(METAR\s?C?O?R?|MET\d{3}M?E?T?A?R?)'        # prefix
metarsta = '\s*(\D{4})?'                                # Station: 4 characters
metardat = '\s*(\d{6}Z)?'                               # datetime
metarmod = '\s*(CC\w{1}|AUTO)?'                         # report modifier
metardti = '\s*(\d{6})?'                                # a number? maybe a hidden sign of aliens?!
metarwin = '\s*(\d{5}KT|VRB\d{2}KT|\d{5}(G\d{2})KT)?'   # wind
metarwch = '\s*(\d{3}V\d{3})?'                          # wind change
metarvis = '\s*(\d/\dSM|\d{3,4})?'                      # visibility
metarrun = '\s*(R\d{2}/{1,6}\d?\d?\d?\d?\w?\w?\d?\d?\d?\d?\w?)?'    # runway visual range
metarwet = '\s*([-]?\D{2}\s|[+]?\D{2}\s|[-]?\D{4}\s|[+]?\D{4}\s|/?/?)?' # weather phenomena
metarnum = '\s*(\(\d{1,2}\))?'                          # wierd number, no idea what it means 
metarskc = '\s*(\w{3}\d{2,3}\w{2,3}|\w{3}\d{2,3}|CAVOK)?'   # sky condition
metartem = '\s*(M?\d{2})?/?(M?\d{2})?'                  # temperature and dewpoint
metarslp = '\s*(SLP\d{3})?'                             # sea level pressure
metarred = '\s*(RE\w+)?'                                # recent development
metardev = '\s*(TEMPO|NOSIG=|BECMG)?'                   # change of weather is coming
metartwe = '\s*([-|\s|+][\w{2,4}]|//)?'                 # trend weather phenomena
metardsk = '\s*(\D{3}\d{3}/?/?/?|CAVOK)?'               # trend sky condition
metarpr1 = '\s*(P\d{4})?'                               # precipitation hourly
metarpr3 = '\s*(6\d{4})?'                               # precipitation 3-6 hourly
metarprd = '\s*(7\d{4})?'                               # precipitation daily
metarteh = '\s*(T\d{8})?'                               # temperature and dewpoint hourly
metartm6 = '\s*(1\d{4})?'                               # maximum temperature in last 6 hour
metartmd = '\s*(4\d{8})?'                               # daily max and min temp
metarpt3 = '\s*(5\d{4})?'                               # pressure tendency in 3 hours
metarali = '\s*(A|Q\d{4})?'                             # altimeter setting

metar_ex = metarpre+metarsta+metardat+metarmod+metarwin+metarwch+metarvis+ \
           metarrun+metarrun+metarwet+metarnum+metarskc+metarskc+metarskc+ \
           metarskc+metartem+metarslp+metarred+metardev+metartwe+metardsk+ \
           metardsk+metardsk+metarpr1+metarpr3+metarprd+metarteh+metartm6+ \
           metartmd+metarpt3+metarali         # 7*4+3+2=33 variables

# Definition of the possible expressions in the ISD code for SYNOP(regular expression)
# SYNOP Decode
# section 1: ground observation
synoppre = '(REMSYN\d{3})'
synopmsk = '\s*(\w{4,5})?'
synopgeo = '\s*([\d/]{5,7})?'
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
ixgggg   = '\s*(9[\d{1}/|/][\d{1}/|/][\d{1}/|/][\d{1}/|/])?'

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
fv = -9999
fv2 = -1111


################################################################################
####################### FUNCTIONS TO DECODE ####################################
################################################################################
def writeoutput(outfile,var):
    outfile.write('%9s ' % var)


################################################################################
###################### MAIN FUNCTION FOR KASSD #################################
################################################################################
def isd_into_kassd(station=['645000'],yearstr=2019,yearend=2020):
    # This scripts decodes ISD-data an writes it into a KASS-D readable file
    # Change the output variables(header: line 19 ff) if you want other outputs and the units too

    # Concatenate string for synop decoding
    synopsta = '\s*('+station[0:5]+')?'
    synop_ex =  synoppre +synopmsk +synopgeo +synopsta +irixhvv  +nddff    +\
                oofff    +isnttt   +iisnttt  +iiipppp  +ivpppp   +vappp    +\
                virrrtr  +viiwww1w2+nhclcmch +ixgggg   +preiii   +prezero  +\
                isnttt2  +iisnttt2 +iiiesntgt+ivesss   +vvsss    +vvsss    +\
                vvsss    +vvsss    +iiffff   +iiiffff  +ivffff   +vviiiss  +\
                iiffff2  +iiiffff2 +ivffff2  +virrrtr2 +nschshs  +nschshs  +\
                nschshs  +nschshs  +ixspspsps #39

    # define paths to source and target file
    datapath_data = '../data'           # source file
    datapath_out  = '../data/output/'   # target file

    years = np.arange(yearstr,yearend)

    # header for KASS-D
    variables_kassd = 'variable = cloud_height_lowest,cloud_area_fraction_total,cloud_area_fraction_lowest,'+ \
        'cloud_genus_low,cloud_genus_medium,cloud_genus_high,cloud_altitude_1,cloud_fraction_1,cloud_type_1,'+ \
        'cloud_altitude_2,cloud_fraction_2,cloud_type_2,cloud_altitude_3,cloud_fraction_3,cloud_type_3,'+ \
        'cloud_altitude_4,cloud_fraction_4,cloud_type_4,'
    variables_units = 'm, , , , , ,m, , ,m, , ,m, ,\n'

    # Create file
    outfile_kassd =  open(datapath_out+'kassd_%s_%s_%s.txt' % (station,yearstr,yearend) , 'w')

    # find name of station id
    stationlist = pd.read_csv('stationlist.py',sep=' ')
    station_name = 'not in list'
    for l in range(len(stationlist)):
        if station == str(stationlist['stat_id'][l]):
            station_name = stationlist['name'][l]
            break
        else:
            continue

    for YY in years: 
        try:
            filenames = [f for f in listdir(datapath_data+'/%s' % str(YY)) if f == station+'-99999-'+str(YY)]
            print(filenames[0])
        except:
            print('for '+str(YY)+' and station '+station+' no files available')
            continue
        with open('%s/%s' % (datapath_data+'/%s' % YY,filenames[0]),'r') as infile:
            data = infile.read().splitlines()

        # Create File Header for KASSD
        if YY == yearstr:
            lat = data[0][28:34]
            lon = data[0][35:41]
            outfile_kassd.write('station_name = '+station_name+' \nstation_id = '+station[0:5]+ \
                    ' \nlat = '+lat+' \nlon = '+lon+'\n')
            outfile_kassd.write(variables_kassd+'\n')
            outfile_kassd.write(variables_units)

	
        # GO through data line by line
        for i_line, line in enumerate(data):
			
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
            ################### ISD only ##################################################
            ###############################################################################
            # Prepare for checking SYNOP data in the code
            case_SYNOP = re.findall('REMSYN\w+',line)
            if case_SYNOP != []:
                if re.findall('BUFR',case_SYNOP[0]) == 'BUFR':
                    case_SYNOP = []
                check_SYNOP = re.findall(synop_ex,line)

            # Prepare for checking METAR data in the code
            check_METAR = ''
            check_METAR = [item for t in re.findall(metar_ex,line) for item in t]

            # Find additional not mandatory data in ISD
            clfl = fv
            clgl = fv
            clgm = fv
            clgh = fv
            clct = fv
            clhl = fv
            ga_out = { 'ga'+str(n) : [fv, fv, fv] for n in range(1,7) }

            if 'ADD' in line:
                # Find precipitation AA1-4
                # Find skycover GF1
                gf1 = str(re.findall('GF1\d{2}\d{2}\d{1}\d{2}\d{1}\d{2}\d{1}\d{5}\d{1}\d{2}\d{1}\d{2}\d{1}',line))
        
                # Test if GF1 is there, if not check SYNOP
                if len(gf1) > 3: 
                    # Cloud fraction total
                    clct = gf1[5:7]
        
                    # Cloud fraction lowest
                    clfl = gf1[10:12]
        
                    # Cloud genus lowest
                    clgl = gf1[13:15]
        
                    # Cloud height lowest
                    clhl = gf1[16:21]
                    
                    # Cloud genus middle
                    clgm = gf1[22:24]
        
                    # Cloud genus high
                    clgh = gf1[25:27]
        
                # Check for SYNOP to update if missing
                if synopdata and case_SYNOP:
                    # Cloud fraction total
                    if clct == '99' or clct == fv:
                        if check_SYNOP[0][5][0:1].isnumeric():
                            clct = check_SYNOP[0][5][0:1]
                    # Cloud fraction lowest
                    if clfl == '99' or clct == fv:
                        if check_SYNOP[0][14][2:3].isnumeric():
                            clgl = check_SYNOP[0][14][2:3]
                    # Cloud genus lowest
                    if clgl == '99' or clct == fv:
                        if check_SYNOP[0][14][2:3].isnumeric():
                            clgl = check_SYNOP[0][14][2:3]
                    # Cloud height lowest
                    if clhl == '99999' or clct == fv:
                        if check_SYNOP[0][4][2:3].isnumeric():
                            clhl = cloudheightlowestlist(check_SYNOP[0][4][2:3])
                    # Cloud genus middle
                    if clgm == '99' or clct == fv:
                        if check_SYNOP[0][14][3:4].isnumeric():
                            clgm = check_SYNOP[0][14][3:4]
                    # Cloud genus high
                    if clgh == '99' or clct == fv:
                        if check_SYNOP[0][14][4:5].isnumeric():
                            clgh = check_SYNOP[0][14][4:5]
        
                # Check for METAR to update if missing
                if metardata and check_METAR:
                    # Cloud fraction lowest
                    if clfl == '99' or clct == fv:
                        if check_METAR[12]:
                            (clfl,dum,dumm) = skycondition(check_METAR[12])
                    # Cloud height lowest
                    if clhl == '99999' or clct == fv:
                        if check_METAR[12]:
                            (dum,clhl,dumm) = skycondition(check_METAR[12])
                    # Cloud genus low
                    if clgm == '99' or clct == fv:
                        if check_METAR[12]:
                            (dum,dumm,clgl) = skycondition(check_METAR[12])
        
                # Find skycover GA1-6
                # Create dicitionary
                for n in range(1,7):
                    # Check ISD data
                    ga_check = str(re.findall('GA'+str(n)+'\d{2}\w{1}\+\d{5}\w{1}\d{2}\w{1}',line))
                    if ga_check != '[]':
                        # cloud cover 
                        ga_out['ga'+str(n)][0] = ga_check[5:7]
                        # cloud height
                        ga_out['ga'+str(n)][1] = ga_check[9:14]
                        # cloud type
                        ga_out['ga'+str(n)][2] = ga_check[15:17]
        
                    # Check for SYNOP to update if missing
                    if synopdata and case_SYNOP and n < 5:
                        # cloud cover
                        if ga_out['ga'+str(n)][0] == '99' or clct == fv:
                            if check_SYNOP[0][n+34].isnumeric():
                                ga_out['ga'+str(n)][0] = check_SYNOP[0][n+34][1:2]
                        # cloud height
                        if ga_out['ga'+str(n)][1] == '99999' or clct == fv:
                            if check_SYNOP[0][n+34].isnumeric():
                                ga_out['ga'+str(n)][1] = cloudheight333(check_SYNOP[0][n+34][3:5])
                        # cloud type
                        if ga_out['ga'+str(n)][2] == '99' or clct == fv:
                            if check_SYNOP[0][n+34].isnumeric():
                                ga_out['ga'+str(n)][2] = check_SYNOP[0][n+34][2:3]
        
                    # Check for METAR to update if missing
                    if metardata and check_METAR and n < 5:
                        if check_METAR[n+12]:
                            (ga_out['ga'+str(n)][0],ga_out['ga'+str(n)][1],ga_out['ga'+str(n)][2]) = skycondition(check_METAR[n+12])
                
            # Write output
            outfile_kassd.write(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' ' )
            outfile_kassd.write(time[0:2]+':'+time[2:4])
            writeoutput(outfile_kassd,clhl)
            writeoutput(outfile_kassd,clct)
            writeoutput(outfile_kassd,clfl)
            writeoutput(outfile_kassd,clgl)
            writeoutput(outfile_kassd,clgm)
            writeoutput(outfile_kassd,clgh)

            for n in range(1,7):
                writeoutput(outfile_kassd,ga_out['ga'+str(n)][1])
                writeoutput(outfile_kassd,ga_out['ga'+str(n)][0])
                writeoutput(outfile_kassd,ga_out['ga'+str(n)][2])
    
            outfile_kassd.write('\n')

    # End Line ---------------------------------------------------------------------
    				
    outfile_kassd.close()
