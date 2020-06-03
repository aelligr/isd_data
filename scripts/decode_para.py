import pandas as pd
import numpy as np
import urllib.request
fv = np.nan
################################################################################
################# Decode parameters from METAR #################################
################################################################################
def windmetar(check_metar1,check_metar2):
    # Wind Speed and Wind Gust and  Wind direction ----------------------------------------------------------------
    if len(check_metar1) < 8:             # case for wind speed 
        METwspd = check_metar1[3:5]       # higher than 100 KN
    else:
        METwspd = check_metar1[3:6]
    METwdir = check_metar1[:3]

    if METwspd.isdigit():
        if check_metar1[5:7] == 'KT':
            METwspd = str(float(METwspd) * 0.514444)
    else:
        METwspd = fv

    if METwdir.isdigit():
        pass
    elif METwdir == 'VRB':
        METwdir = -1
        pass
    else:
        METwdir = fv

    if len(check_metar2) > 7:
        if not re.match(check_metar2, 'G\d{3}'):
            METwgst = check_metar2[5:-2]
        else:
            METwgst = check_metar2[5:-3]
        if METwgst.isdigit():
            pass
        else:
            METwgst = fv
    else:
        METwgst = fv
    return (METwdir,METwspd,METwgst)

def skycondition(check_metar):
    try:
        if check_metar[0:3] == 'SKC':
            clc = '0'
            clh = str(round(float(check_metar[3:6])*100*0.3048,2))
        elif check_metar[0:3] == 'FEW':
            clc = '2'
            clh = str(round(float(check_metar[3:6])*100*0.3048,2))
        elif check_metar[0:3] == 'SCT':
            clc = '4'
            clh = str(round(float(check_metar[3:6])*100*0.3048,2))
        elif check_metar[0:3] == 'BKN':
            clc = '7'
            clh = str(round(float(check_metar[3:6])*100*0.3048,2))
        elif check_metar[0:3] == 'OVC':
            clc = '8'
            clh = str(round(float(check_metar[3:6])*100*0.3048,2))
        elif check_metar[0:5] == 'CAVOK':
            clc = '0'
            clh = str(round(float(check_metar[3:6])*100*0.3048,2))
        else:
            clc = fv
            clh = fv
        if len(check_metar) > 6:
            if check_metar[6:8] == 'CB':
                clt = '09'
            elif check_metar[6:8] == 'TC':
                clt = '02'
            else:
                clt = fv
        else:
            clt = fv
    except:
        clc = fv
        clh = fv
        clt = fv
    return (clc,clh,clt)


################################################################################
################# Decode parameters from SYNOP #################################
################################################################################
def cloudheight333(clhe):
    if int(clhe) < 51:
        for i in range(0,51):
            if str(i).zfill(2) == clhe:
                return str(i*30)
                break
            else:
                continue
    elif int(clhe) < 80 and int(clhe) > 49:
        for i in range(56,80):
            if str(i) == clhe:
                return str((i-55)*300+1500)
                break
            else:
                continue
    elif int(clhe[0:1]) == 8:
        for i in range(80,90):
            if str(i) == clhe:
                return str((i-80)*1500+9000)
                break
            else:
                continue
    elif int(clhe[0:1]) == 9:
        if int(clhe) < 93:
            return str((int(clhe)-90)*50)
        elif int(clhe) > 92 and int(clhe) < 95:

            return str((int(clhe)-91)*100)
        elif int(clhe) == 95:
            return '600'
        elif int(clhe) > 95:
             return str((int(clhe)-94)*500)
        else:
            return fv
    else:
        return fv
        
def cloudheightlowestlist(var):
    if var.isnumeric():
        hn = int(var)
        if hn == 0:
            return '0'
        if hn == 1:
            return '50'
        if hn == 2:
            return '100'
        if hn == 3:
            return '200'
        if hn == 4:
            return '300'
        if hn == 5:
            return '600'
        if hn == 6:
            return '1000'
        if hn == 7:
            return '1500'
        if hn == 8:
            return '2000'
        if hn == 9:
            return '2500'
    else:
        return fv

def windsynop(check_synop1):
    wdir = check_synop1[1:3]
    wspd = check_synop1[3:5]
    if wdir.isdigit():
        wdir = int(wdir) * 10
    else:
        wdir = fv
    if wspd.isdigit():
        wspd = int(wspd)
    else:
        wspd = fv
    try:
        wspd = str(wspd * 0.514444)
    except:
        pass
    return (wdir,wspd)
            
def rh2dewpoint(temp,rh):
    es = 6.11*10.0**(7.5*temp/(237.7+temp))
    e = (rh*es)/100
    dtemp = (-430.22+237.7*(np.log(e))/(-np.log(e)+19.08))
    return dtemp

def synoprain(var):
    try:
        rain = float(var[1:4])
        n = var[5]
        if rain >= 900.:
            rain = (rain-990)/10.
    except:
        return fv
    if n == '1':
        return rain/6.
    elif n == '2':
        return rain/12.
    elif n == '3':
        return rain/18.
    elif n == '4':
        return rain/24.
    elif n == '5':
        return rain/1.
    elif n == '6':
        return rain/2.
    elif n == '7':
        return rain/3.
    elif n == '8':
        return rain/9.
    elif n == '9':
        return rain/15.
    else:
        return rain/1.


def fusedata(prio1,prio2,prio3,index,priority):
    mask = pd.Series(np.nan,index)
    series = pd.Series(np.nan,index)
    
    for var in index:
        # mask for values priority 1 and assign priority 1 values
        series[var] = prio1[var] if ~np.isnan(prio1[var]) else series[var]
        mask[var] = priority[0] if ~np.isnan(prio1[var]) else mask[var]
        # update values with priority 2 if missing and update according mask
        mask[var] = priority[1] if (np.isnan(series[var]) and ~np.isnan(prio2[var])) else mask[var]
        series[var] = prio2[var] if (np.isnan(series[var]) and ~np.isnan(prio2[var])) else series[var]
        # update values with priority 3 if missing and update according mask
        mask[var] = priority[2] if (np.isnan(series[var]) and ~np.isnan(prio3[var])) else mask[var]
        series[var] = prio3[var] if (np.isnan(series[var]) and ~np.isnan(prio3[var])) else series[var]

    return (series, mask)


def fuse_diff_timesteps(prio1,prio2,mask1,mask2,index):
    mask = pd.Series(np.nan,index)
    series = pd.Series(np.nan,index)

    for var in index:
        # mask for values priority 1 and assign priority 1 values
        mask[var] = mask1[var] if ~np.isnan(prio1[var]) else mask[var]
        series[var] = prio1[var] if ~np.isnan(prio1[var]) else series[var]
        # update values with priority 2 if missing and update according mask
        mask[var] = mask2[var] if (np.isnan(series[var]) and ~np.isnan(prio2[var])) else mask[var]
        series[var] = prio2[var] if (np.isnan(series[var]) and ~np.isnan(prio2[var])) else series[var]

    return (series, mask)


def writeoutput(outfile,var,csv):
    if csv:
        if str(var) == str(np.nan):
            outfile.write(',')
        else:
            outfile.write(',')
            outfile.write(str(var))
    else:
        if len(str(var).split(sep=' ')) > 1:
            outfile.write('%9s ' % fv)
        else:
            outfile.write('%9s ' % var)

#def bufrfromogi(station,date,time):
#    check_SYNOP = urllib.request.urlopen('https://www.ogimet.com/cgi-bin/getsynop?block='+station+'&begin='+date+time+'&end='+date+time)
#    print(check_SYNOP.read(100).decode('utf-8'))


#bufrfromogi('64500','20180921','1800')

