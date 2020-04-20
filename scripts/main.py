from download_isd import download
from isd_read import split_isd_data
from isd_kassd import isd_into_kassd
from argparse import ArgumentParser
import os

def switchtobool(var,default):
    if var == None:
        return default
    if var == 'False':
        return False
    elif var == 'True':
        return True
    else:
        return default

parser = ArgumentParser()

# This part handlies the input arguments. Add more options if you like.
parser.add_argument('-stat','--stations', dest='stations', action='append', help='MANDATORY: list of stations USE 6 DIGITS, not 5(add a 0 if necessary) e.g. -stat 645000 645500 645010', required=True, nargs='+')
parser.add_argument('-yrs','--years', dest='years', help='MANDATORY: from which year to which year you want to handle isd data? e.g. -yrs 1950 1990', required=True, nargs=2)
parser.add_argument('-dl','--download', dest='download', help='OPTIONAL: Do you want to download data and store it in data/<year> first? Then pass -dl True')
parser.add_argument('-dec','--decode', dest='decode', help='OPTIONAL: Do you want to decode data and store in data/output? Then pass -dec True')
parser.add_argument('-kassd', dest='kassd', help='OPTIONAL: Do you want to decode data and create a for KASSD readable file? Then pass -kassd True')
parser.add_argument('-mmo','--makemetaronly', dest='mmo', help='OPTIONAL: Do you want to make files only with METAR data in data/output/met_* when decoding? Then pass -mmo True Default False')
parser.add_argument('-mso','--makesynoponly', dest='mso', help='OPTIONAL: Do you want to make files only with SYNOP data in data/output/syn_* when decoding? Then pass -mso True Default False')
parser.add_argument('-mall','--makeall', dest='mall', help='OPTIONAL: Do you want to make files with all available data from isd into data/output/isd_*? Then pass -mall True Default True')
parser.add_argument('-zisd','--zipisd', dest='zisd', help='OPTIONAL: Do you want to zip the created isd files? They are very big. Then pass -zisd True Default True')

# Pass input variables to variables
args            = parser.parse_args()
stations        = args.stations[0]
yearstr         = int(args.years[0])
yearend         = int(args.years[1])+1
download_files  = args.download
split_data      = args.decode
mk_kassd        = args.kassd
metar           = args.mmo
synop           = args.mso
isd             = args.mall
zisd            = args.zisd

download_files = switchtobool(download_files,False)
split_data = switchtobool(split_data,False)
mk_kassd = switchtobool(mk_kassd,False)
metar = switchtobool(metar,False)
synop = switchtobool(synop,False)
isd = switchtobool(isd,True)
zisd = switchtobool(zisd,True)

# Download files
for station in stations:
    if download_files:
        for year in range(yearstr,yearend):
            print('Downlaod: ',year, station)
            download(str(year), station)

# Split and decode data into readable files -> data/output
for station in stations:
    if split_data:
        split_isd_data(station=station, yearstr=yearstr, yearend=yearend, mk_isd=isd, mk_synop=synop, mk_metar=metar)
        if os.path.isfile('../data/output/isd_'+str(station)+'_'+str(yearstr)+'_'+str(yearend-1)+'.txt') and zisd:
            os.system('gzip -f ../data/output/isd_'+str(station)+'_'+str(yearstr)+'_'+str(yearend-1)+'.txt')

# convert isd, synop, and Metar data into kassd readable files
if mk_kassd:
    for station in stations:
        print(station)
        isd_into_kassd(station=station, yearstr=yearstr, yearend=yearend)

