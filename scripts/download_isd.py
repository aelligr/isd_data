import urllib.request
import os
import gzip
from ftplib import FTP

# This scripts downloads isd files
# Arguments are year, station number.

def download(year, station):

    # path, url, concate filename
    path = '../data/'
    url = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/'
    filename = station+'-99999-'+str(year)

    # prepare for enter ftp server, login anonymous
    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    try:
        ftp.cwd('/pub/data/noaa/'+year)
    except:
        print('This year('+str(year)+') is not on isd.')
        return

    # download files if they exist on ftp server and not in local directory
    try:
        ftp.retrlines('LIST '+filename+'.gz')
        if os.path.exists(path+year+'/'+filename):
            return
        else:
            if os.path.exists(path+year):
                fhandle = open(path+year+'/'+filename+'.gz', 'wb')
                ftp.retrbinary("RETR " + filename+'.gz' ,fhandle.write)
            else:
                os.mkdir(path+year)
                fhandle = open(path+year+'/'+filename+'.gz', 'wb')
                ftp.retrbinary("RETR " + filename+'.gz' ,fhandle.write)
            fhandle.close()
            os.system('gunzip '+path+year+'/'+filename+'.gz')
            return
    except:
        return

    return

