from os.path import isfile, join
import re
from decode_para import windmetar, skycondition, cloudheight333, cloudheightlowestlist, windsynop, rh2dewpoint, synoprain
import pandas as pd
import numpy as np

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
synopmsk = '\s*(AAXX)?'
synopgeo = '\s*([\d/]{5,7})?'
irixhvv  = '\s*([0-4][0-7][/|\d{1}][/|\d{1}][/|\d{1}])?'
nddff    = '\s*([/|\d{1}][/|\d{1}][/|\d{1}][/|\d{1}][/|\d{1}])?'
oofff    = '\s*(00\d{3})?'
isnttt   = '\s*(1[0|1]\d{3})?'
iisnttt  = '\s*(2[0|1|9]\d{3})?'
iiipppp  = '\s*(3[\d{1}|/][\d{1}|/][\d{1}|/][\d{1}|/])?'
ivpppp   = '\s*(4[\d{1}|/][\d{1}|/][\d{1}|/][\d{1}|/])?'
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
vvsss    = '\s*(5[\d{1}|/][\d{1}|/][\d{1}|/][\d{1}|/])?'
iiffff   = '\s*(2\d{4})?'
iiiffff  = '\s*(3\d{4})?'
ivffff   = '\s*(4\d{4})?'
vevap    = '\s*(5[\d{1}|/][\d{1}|/][\d{1}|/][\d{1}|/])?'
vvss     = '\s*(55[\d{1}|/][\d{1}|/][\d{1}|/])?'
vviiiss  = '\s*(553[\d{1}|/][\d{1}|/])?'
vpres    = '\s*(5[8|9|/][\d{1}|/][\d{1}|/][\d{1}|/])?'
iiffff2  = '\s*(2\d{4})?'
iiiffff2 = '\s*(3\d{4})?'
ivffff2  = '\s*(4\d{4})?'
virrrtr2 = '\s*(6[\d{1}|/][\d{1}|/][\d{1}|/]\[\d{1}|/])?'
nschshs  = '\s*(8[\d{1}|/][\d{1}|/]\d{2})?'      # up to 4 times
ixspspsps= '\s*(9\d{4})?'

# a dummy for not matching patterns
dummat   = '(99999)?'
fv = np.nan
fv2 = '-1111'


################################################################################
####################### FUNCTIONS TO DECODE ####################################
################################################################################
def isdread(line,index):
    isdser = pd.Series(np.nan,index)
    if line[60:63] != '999':
        isdser['wind_dir'] = line[60:63]
    if line[65:69] != '9999':
        isdser['wind_spd'] = float(line[65:69])/10.
    if line[87:92] != '+9999':
        isdser['temp'] = line[87]+str(round(float(line[88:92])/10,1))
    if line[93:98] != '+9999':
        isdser['dtemp'] = line[93]+str(round(float(line[94:98])/10,1))
    if line[99:104] != '99999':
        isdser['press'] = line[99:104]

    if 'ADD' in line:
        # Find precipitation AA1-4
        for n in range(1,5):
            # Check ISD data
            aa_check = str(re.findall('AA'+str(n)+'\d{2}\d{4}\w{1}\w{1}',line))
            if aa_check != '[]':
                prec = aa_check[7:11]
                prec_h = aa_check[5:7]
                # Calculate mm/h
                if prec != '9999':
                    if prec_h != '99' and prec_h != '00':
                        isdser['preci'+str(n)] = str(round(float(prec) / float(prec_h) / 10., 2))
                        isdser['precih'+str(n)] = prec_h
                    elif prec == '0000':
                        isdser['preci'+str(n)] = prec
                        isdser['precih'+str(n)] = prec_h

        # Find skycover GF1
        gf1 = str(re.findall('GF1\d{2}\d{2}\d{1}\d{2}\d{1}\d{2}\d{1}\d{5}\d{1}\d{2}\d{1}\d{2}\d{1}',line))

        # Test if GF1 is there, if not check SYNOP
        if len(gf1) > 3: 
            # Cloud fraction total
            if gf1[5:7] != '99':
                isdser['clct'] = gf1[5:7]

            # Cloud fraction lowest
            if gf1[10:12] != '99':
                isdser['clfl'] = gf1[10:12]

            # Cloud genus lowest
            if gf1[13:15] != '99':
                isdser['clgl'] = gf1[13:15]

            # Cloud height lowest
            if gf1[16:21] != '99999':
                isdser['clhl'] = gf1[16:21]
            
            # Cloud genus middle
            if gf1[22:24] != '99':
                isdser['clgm'] = gf1[22:24]

            # Cloud genus high
            if gf1[25:27] != '99':
                isdser['clgh'] = gf1[25:27]

        for n in range(1,7):
            # Check ISD data
            ga_check = str(re.findall('GA'+str(n)+'\d{2}\w{1}\+\d{5}\w{1}\d{2}\w{1}',line))
            if ga_check != '[]':
                # cloud cover 
                if ga_check[5:7] != '99':
                    isdser['ga'+str(n)+'clc'] = ga_check[5:7]
                # cloud height
                if ga_check[9:14] != '99999':
                    isdser['ga'+str(n)+'clh'] = ga_check[9:14]
                # cloud type
                if ga_check[15:17] != '99':
                    isdser['ga'+str(n)+'clt'] = ga_check[15:17]

        # Find radiation in ISD and SYNOP
        gj1 = str(re.findall('GJ1\d{4}\w{1}',line))
        if len(gj1) > 3:
            # Cloud fraction total
            if gj1[5:9] != '9999':
                isdser['sundur'] = str(round(float(gj1[5:9])/60))

    return isdser


def synopread(line,index,station,i_line):
    synopser = pd.Series(np.nan,index)
    # Synop concatenate
    synopsta = '\s*('+station[0:5]+')'
    synop_ex =  synoppre +synopmsk +synopgeo +synopsta +irixhvv  +nddff    +\
                oofff    +isnttt   +iisnttt  +iiipppp  +ivpppp   +vappp    +\
                virrrtr  +viiwww1w2+nhclcmch +ixgggg   +preiii   +prezero  +\
                isnttt2  +iisnttt2 +iiiesntgt+ivesss   +vvsss    +vevap    +\
                vvss     +vviiiss  +vpres    +iiffff   +iiiffff  +ivffff   +\
                dummat   +dummat   +dummat   +iiffff2  +iiiffff2 +ivffff2  +\
                virrrtr2 +nschshs  +nschshs  +nschshs  +nschshs  +ixspspsps #42

    # Prepare for checking SYNOP data in the code
    case_SYNOP = re.findall('REMSYN\w+',line)
    if case_SYNOP != []:
        if re.findall('BUFR',case_SYNOP[0]) == 'BUFR':
            case_SYNOP = []
            
        check_SYNOP = re.findall(synop_ex,line)

        if check_SYNOP != []:
            check_SYNOP = check_SYNOP[0][3:]
        else:
            return synopser

        # clouds first group
        if case_SYNOP:
            # Cloud fraction total
            if check_SYNOP[2]:
                if check_SYNOP[2][0].isnumeric():
                    synopser['clct'] = check_SYNOP[2][0]
            # Cloud fraction lowest
            if check_SYNOP[11]:
                if check_SYNOP[11][1].isnumeric():
                    synopser['clfl'] = check_SYNOP[11][1]
            # Cloud genus lowest
            if check_SYNOP[11]:
                if check_SYNOP[11][2].isnumeric():
                    synopser['clgl'] = check_SYNOP[11][2]
            # Cloud height lowest
            if check_SYNOP[1]:
                if check_SYNOP[1][2].isnumeric():
                    synopser['clhl'] = cloudheightlowestlist(check_SYNOP[1][2])
            # Cloud genus middle
            if check_SYNOP[11]:
                if check_SYNOP[11][3].isnumeric():
                    synopser['clgm'] = check_SYNOP[11][3]
            # Cloud genus high
            if check_SYNOP[11]:
                if check_SYNOP[11][4:5].isnumeric():
                    synopser['clgh'] = check_SYNOP[11][4]
        
        # clouds 333 group
        syn_skip = True
        for n in range(1,5):
            # Check for SYNOP to update if missing
            if case_SYNOP and syn_skip:
                if check_SYNOP[n+33] == '':
                    syn_skip = False
                # cloud cover
                if check_SYNOP[n+33].isnumeric():
                    synopser['ga'+str(n)+'clc'] = check_SYNOP[n+33][1:2]
                # cloud height
                if check_SYNOP[n+33].isnumeric():
                    synopser['ga'+str(n)+'clh'] = cloudheight333(check_SYNOP[n+33][3:5])
                # cloud type
                if check_SYNOP[n+33].isnumeric():
                    synopser['ga'+str(n)+'clt'] = check_SYNOP[n+33][2:3]
        
        # sun duration
        if check_SYNOP[19].isnumeric():
            synopser['sundur'] = str(float(check_SYNOP[19][2:5])/10)

        # check weather phenomena of synop
        if check_SYNOP[10]:
            if check_SYNOP[10][1:3] != '00':
                synopser['synwea'] = check_SYNOP[10][1:3]
            if check_SYNOP[10][3] != '/':
                synopser['synweco1'] = check_SYNOP[10][3]
            if check_SYNOP[10][4] != '/':
                synopser['synweco2'] = check_SYNOP[10][4]

        # temperature
        if check_SYNOP[4]:
            if check_SYNOP[4][2:5].isdigit():
                if check_SYNOP[4][1] == '0':
                    synopser['temp'] = round(float(check_SYNOP[4][2:5]) / 10.,2)
                else:
                    synopser['temp'] = round(float(check_SYNOP[4][2:5]) / 10.,2) *-1.

        # dew Point
        if check_SYNOP[5].isnumeric():
            if check_SYNOP[5][2:5].isdigit():
                if check_SYNOP[5][1] == '0':
                    synopser['dtemp'] = float(check_SYNOP[5][2:5]) / 10.
                elif check_SYNOP[5][1] == '1':
                    synopser['dtemp'] = float(check_SYNOP[5][2:5]) / 10. *-1.
                elif check_SYNOP[5][1] == '9':
                    synopser['dtemp'] = rh2dewpoint(synopser['temp'],float(check_SYNOP[5][2:5]))

        # wind direction and wind speed
        if check_SYNOP[2].isnumeric():
            (synopser['wind_dir'],synopser['wind_spd']) = windsynop(check_SYNOP[2])

        # precipitation
        if check_SYNOP[1].isnumeric():
            if check_SYNOP[1][0] == '0' or check_SYNOP[1][0] == '1':
                if check_SYNOP[9]:
                    synopser['preci1'] = synoprain(check_SYNOP[9])

        # pressure
        if check_SYNOP[8].isnumeric():
            if check_SYNOP[8][1:5].isdigit():
                synopser['press'] = float(check_SYNOP[8][1:5])/10. + 1000. if float(check_SYNOP[8][1:5])/10. + 1000. < 1200. else float(check_SYNOP[8][1:5])/10.
            elif check_SYNOP[8][1:4].isdigit():
                synopser['press'] = float(check_SYNOP[8][1:4]) + 1000. if float(check_SYNOP[8][1:4]) + 1000. < 1200. else float(check_SYNOP[8][1:4])

    return synopser

    
def metarread(line,index,i_line):
    # define time series to return
    metarser = pd.Series(np.nan,index)

    # prepare for checking METAR data in the code
    check_METAR = [item for t in re.findall(metar_ex,line) for item in t]

    # test for NIL
    if re.search('MET\w*\s*\w*\s*NIL',line):
        check_METAR = []
        return metarser
    if re.search('MET\d{3}NOSIG',line):
        check_METAR = []
        return metarser

    if check_METAR != []:
        # Cloud fraction, height, and genus lowest
        if check_METAR[12].isnumeric():
             (metarser['clfl'],metarser['clhl'],metarser['clgl']) = skycondition(check_METAR[12])

        met_skip = True
        for n in range(1,5):
            if met_skip:
                if check_METAR[n+11] == '':
                    met_skip = False
                if check_METAR[n+11].isnumeric():
                    (metarser['ga'+str(n)+'clc'],metarser['ga'+str(n)+'clh'],metarser['ga'+str(n)+'clt']) = skycondition(check_METAR[n+11])

        # wind speed and wind gust and wind direction
        if check_METAR[4].isnumeric():
            (metarser['wind_dir'], metarser['wind_spd'], metarser['wind_gst']) = windmetar(check_METAR[4],check_METAR[5])

        # Pressure
        if check_METAR[32].isnumeric():
            metarser['press'] = check_METAR[32][1:]

        # Temperature
        if check_METAR[16].isnumeric():
            metarser['temp'] = check_METAR[16]

        # Dew point Temperature
        if check_METAR[17].isnumeric():
            metarser['dtemp'] = check_METAR[17]

    return metarser

    
