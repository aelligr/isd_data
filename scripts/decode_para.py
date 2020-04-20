fv = -9999
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
            clc = '6'
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
                clt = '12'
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

def windsynop(check_synop1,check_synop2):
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
    if check_synop2:
        if check_synop2[-1] == '3' or check_synop2[-1] == '4':
            wspd = str(wspd * 0.514444)
    return (wdir,wspd)
            
