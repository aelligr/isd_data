from os.path import isfile, join
import re
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

def decodemetar(line,date,time,lat,lon,header_METAR,outfile_met):

    # Check for according strings in line
    check_METAR = ''
    check_METAR = [item for t in re.findall(metar_ex,line) for item in t]

    # write output isd additional section
    if len(check_METAR)<3:
        outfile_met.write('%9s %6s ' % (date,time))
        outfile_met.write('%6s %6s ' % (lat,lon))
        for ih in range(len(header_METAR)):
            outfile_met.write('%9s ' % fv)
        return
    else:
        # Wind Speed and Wind Gust and  Wind direction ----------------------------------
        if check_METAR[4]:
            (wdir, wspd, wgst) = windmetar(check_METAR[4],check_METAR[5])
        else:
            wdir = fv
            wspd = fv
            wgst = fv

         # Visibility -------------------------------------------------------------------
        if check_METAR[7]:
            vis = check_METAR[7]
        else:
            vis = fv

        # Pressure ---------------------------------------------------------------------
        if check_METAR[32]:
            prs = check_METAR[32][1:]
        else:
            prs = fv

        # Temperature -------------------------------------------------------------------
        if check_METAR[16]:
            tmp = check_METAR[16]
        else:
            tmp = fv

        # Dew point Temperature ---------------------------------------------------------
        if check_METAR[17]:
            dtmp = check_METAR[17]
        else:
            dtmp = fv

        # Weather Phenomeana ------------------------------------------------------------
        if check_METAR[10]:
            weatherphen = check_METAR[10]
        else:
            weatherphen = fv

        # Sky Condition 1-4 --------------------------------------------------------------
        # Create dicitionary
        ga_out = { 'ga'+str(n) : [fv, fv, fv] for n in range(1,5) }
        for n in range(1,5):
            if check_METAR[n+12]:
                (ga_out['ga'+str(n)][0],ga_out['ga'+str(n)][1],ga_out['ga'+str(n)][2]) = skycondition(check_METAR[n+12])

    # Write date, time, and coords
    outfile_met.write('%9s %6s ' % (date,time))
    outfile_met.write('%6s %6s ' % (lat,lon))
    # Write output to metar-file
    writeoutput(outfile_met,wdir)
    writeoutput(outfile_met,wspd)
    writeoutput(outfile_met,wgst)
    writeoutput(outfile_met,vis)
    writeoutput(outfile_met,prs)
    writeoutput(outfile_met,tmp)
    writeoutput(outfile_met,dtmp)
    writeoutput(outfile_met,weatherphen)
    for n in range(1,7):
        for x in range(0,3):
            writeoutput(outfile_met,ga_out['ga'+str(n)][x])
            
    outfile_met.write('\n')
    
    return


def decodesynop(station,line,date,time,lat,lon,header_SYNOP,outfile_syn):

    # Definition of the possible expressions in the ISD code for SYNOP(regular expression)

    # section 1: ground observation

    # Synop concatenate
    synopsta = '\s*('+station[0:5]+')?'
    synop_ex =  synoppre +synopmsk +synopgeo +synopsta +irixhvv  +nddff    +\
                oofff    +isnttt   +iisnttt  +iiipppp  +ivpppp   +vappp    +\
                virrrtr  +viiwww1w2+nhclcmch +ixgggg   +preiii   +prezero  +\
                isnttt2  +iisnttt2 +iiiesntgt+ivesss   +vvsss    +vvsss    +\
                vvsss    +vvsss    +iiffff   +iiiffff  +ivffff   +vviiiss  +\
                iiffff2  +iiiffff2 +ivffff2  +virrrtr2 +nschshs  +nschshs  +\
                nschshs  +nschshs  +ixspspsps #39

    # Check for according strings in line
    fv = -9999
    fv2 = -1111
    check_SYNOP = ''
    dummyvar = True

    # Check which SYNOP decoder to use
    case_SYNOP = re.findall('REMSYN\w+',line)
    if not case_SYNOP:
        return

    if re.findall('BUFR',case_SYNOP[0]):
        print('BUFR data. Binary BUFR data not in ISD, go to NOAA page for ordering according product')
        return

    check_SYNOP = re.findall(synop_ex,line)

    if not case_SYNOP:
        print(date,time,station,'Not able to decode synop data')
        return
    else:

        # Temperature ----------------------------------------------------------------
        if check_SYNOP[0][8]:
            if check_SYNOP[0][8][2:5].isdigit():
                tmp = round(float(check_SYNOP[0][8][2:5]) / 10.,2)
                if check_SYNOP[0][8][1] == '1':
                    tmp = tmp*(-1)
            else:
                tmp =fv
        else:
            tmp =fv

        # Dew Point ----------------------------------------------------------------
        if check_SYNOP[0][9]:
            if check_SYNOP[0][9][2:5].isdigit():
                if not check_SYNOP[0][9][1] == '9':
                    dtmp = float(check_SYNOP[0][9][2:5]) / 10.
                    if check_SYNOP[0][9][1] == '1':
                        dtmp = dtmp*(-1)
                    elif check_SYNOP[0][9][1] != '0' and check_SYNOP[0][9][1] != '1':
                        dtmp = fv2
                        #raise ValueError('Unknown Td Code')
                else:
                    dtmp = fv
            else:
                dtmp = fv
        else:
            dtmp = fv

        # Tmax ----------------------------------------------------------------
        if check_SYNOP[0][18]:
            if check_SYNOP[0][18][2:5].isdigit():
                tmax = round(float(check_SYNOP[0][18][2:5]) / 10., 2)
                if check_SYNOP[0][18][1] == '1':
                    tmax = round(tmax*(-1), 2)
                elif check_SYNOP[0][18][1] != '0' and check_SYNOP[0][18][1] != '1':
                    tmax = fv2
            else:
                tmax = fv
        else:
            tmax = fv

        # Tmin ----------------------------------------------------------------
        if check_SYNOP[0][19]:
            if check_SYNOP[0][19][2:5].isdigit():
                tmin = round(float(check_SYNOP[0][19][2:5]) / 10., 2)
                if check_SYNOP[0][19][1] == '1':
                    tmin = tmin*(-1)
                elif check_SYNOP[0][19][1] != '0' and check_SYNOP[0][19][1] != '1':
                    tmin = fv2
            else:
                tmin = fv
        else:
            tmin = fv

        # Relative Humidity ----------------------------------------------------------------
        if check_SYNOP[0][9]:
            rh = check_SYNOP[0][6][2:5]
            if rh.isdigit():
                if check_SYNOP[0][9][1] == '9':
                    rh = round(float(check_SYNOP[0][9][2:5]) / 10., 2)
                else:
                    rh = fv
            else:
                rh = fv
        else:
            rh = fv

        # Wind Direction and Wind Speed----------------------------------------------------------------
        if check_SYNOP[0][5]:
            (wdir,wspd) = windsynop(check_SYNOP[0][5],check_SYNOP[0][2])
        else:
            wdir = fv
            wspd = fv

        # Precipitation -------------------------------------------------------------------------------
        if dummyvar:
            prec = fv
        else:
            prec = fv


        # Cloud height lowest -------------------------------------------------------------------------
        if check_SYNOP[0][4]:
            clhl = cloudheightlowestlist(check_SYNOP[0][4][2:3])
        else:
            clhl = fv

        # Cloud area fraction total ----------------------------------------------------------------
        if check_SYNOP[0][5]:
            if check_SYNOP[0][5][0:1].isnumeric():
                clft = check_SYNOP[0][5][0:1]
            else:
                clft = fv
        else:
            clft = fv

        # Cloud fraction and type ------------------------------------------------------------------
        if check_SYNOP[0][14]:
            # Cloud area fraction lowest
            if check_SYNOP[0][14][1:2].isnumeric():
                clfl = check_SYNOP[0][14][1:2]
            else:
                clfl = fv
            # Cloud genus low
            if check_SYNOP[0][14][2:3].isnumeric():
                clgl = check_SYNOP[0][14][2:3]
            else:
                clgl = fv
            # Cloud genus medium
            if check_SYNOP[0][14][3:4].isnumeric():
                clgm = check_SYNOP[0][14][3:4]
            else:
                clgl = fv
            # Cloud genus high
            if check_SYNOP[0][14][4:5].isnumeric():
                clgh = check_SYNOP[0][14][4:5]
            else:
                clgh = fv

        else:
            clfl = fv
            clgl = fv
            clgm = fv
            clgh = fv

        # Cloud altidute, fraction, and type up to 4 times(ascending order) ------------------------
        cl333 = { 'cl333'+str(n) : [fv, fv, fv] for n in range(1,5) }
        for n in range(0,4):
            if check_SYNOP[0][n+34]:
                # Cloud height
                if check_SYNOP[0][n+34][3:5].isnumeric():
                    cl333['cl333'+str(n)][0] = cloudheight333(check_SYNOP[0][n+34][3:5])
                # Cloud fraction
                if check_SYNOP[0][n+34][1:2].isnumeric():
                    cl333['cl333'+str(n)][1] = check_SYNOP[0][n+34][1:2]
                # Cloud type
                if check_SYNOP[0][n+34][2:3].isnumeric():
                    cl333['cl333'+str(n)][2] = check_SYNOP[0][n+34][2:3]

    # Write date, time, and coords
    outfile_syn.write('%9s %6s ' % (date,time))
    outfile_syn.write('%6s %6s ' % (lat,lon))
    # Write output to synop-file
    writeoutput(outfile_syn,tmp)
    writeoutput(outfile_syn,dtmp)
    writeoutput(outfile_syn,tmax)
    writeoutput(outfile_syn,tmin)
    writeoutput(outfile_syn,rh)
    writeoutput(outfile_syn,wdir)
    writeoutput(outfile_syn,wspd)
    writeoutput(outfile_syn,prec)
    writeoutput(outfile_syn,clhl)
    writeoutput(outfile_syn,clft)
    writeoutput(outfile_syn,clfl)
    writeoutput(outfile_syn,clgl)
    writeoutput(outfile_syn,clgm)
    writeoutput(outfile_syn,clgh)
    for n in range(1,5):
        for x in range(0,3):
            writeoutput(outfile_syn,cl333['cl333'+str(n)][x])

    outfile_syn.write('\n')

    return

def decodeisd(station,line,date,time,lat,lon,header_ISD,outfile_isd,synopdata,metardata):
    
    # Synop concatenate
    synopsta = '\s*('+station[0:5]+')?'
    synop_ex =  synoppre +synopmsk +synopgeo +synopsta +irixhvv  +nddff    +\
                oofff    +isnttt   +iisnttt  +iiipppp  +ivpppp   +vappp    +\
                virrrtr  +viiwww1w2+nhclcmch +ixgggg   +preiii   +prezero  +\
                isnttt2  +iisnttt2 +iiiesntgt+ivesss   +vvsss    +vvsss    +\
                vvsss    +vvsss    +iiffff   +iiiffff  +ivffff   +vviiiss  +\
                iiffff2  +iiiffff2 +ivffff2  +virrrtr2 +nschshs  +nschshs  +\
                nschshs  +nschshs  +ixspspsps #39

    # write output isd mandatory section
    wind_dir = line[60:63]
    wind_spd = line[65:69]
    lcl5_8 = line[70:75]
    cavok = line[77:78]
    visib = line[78:84]
    temp = line[87:92]
    dtemp = line[93:98]
    press = line[99:104]

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
    aa_out = { 'aa'+str(n) : [fv, fv] for n in range(1,5) }
    ga_out = { 'ga'+str(n) : [fv, fv, fv] for n in range(1,7) }

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
                        aa_out['aa'+str(n)][0] = str(round(float(prec) / float(prec_h) / 10., 2))
                        aa_out['aa'+str(n)][1] = prec_h
                    elif prec == '0000':
                        aa_out['aa'+str(n)][0] = prec
                        aa_out['aa'+str(n)][1] = prec_h
                    else:
                        aa_out['aa'+str(n)][0] = fv
                        aa_out['aa'+str(n)][1] = fv
                else:
                    aa_out['aa'+str(n)][0] = fv
                    aa_out['aa'+str(n)][1] = fv

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


    # Write date, time, and coords
    outfile_isd.write('%9s %6s ' % (date,time))
    outfile_isd.write('%6s %6s ' % (lat,lon))
    # Write variables into files
    writeoutput(outfile_isd,wind_dir)
    writeoutput(outfile_isd,wind_spd)
    writeoutput(outfile_isd,str(float(temp[1:5])/10.))
    writeoutput(outfile_isd,str(float(dtemp[1:5])/10.))
    writeoutput(outfile_isd,press)
    for n in range(1,5): 
        for x in range(0,2):
            writeoutput(outfile_isd,aa_out['aa'+str(n)][x])
    writeoutput(outfile_isd,clct)
    writeoutput(outfile_isd,clfl)
    writeoutput(outfile_isd,clgl)
    writeoutput(outfile_isd,clhl)
    writeoutput(outfile_isd,clgm)
    writeoutput(outfile_isd,clgh)
    for n in range(1,7):
        for x in range(0,3):
            writeoutput(outfile_isd,ga_out['ga'+str(n)][x])
    
    outfile_isd.write('\n')

    return


