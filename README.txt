README

It describes the uses of these scripts to download data.
Working directory is scripts/ and run scripts is always with main.py.
main.py offers options of usage. Use 'python main.py -h' for help.

REQUESTED PYTHON MODULES
pandas
numpy
datetime
xarray
ftplib
gzip
os
argparse
re

HOW-TO:
python main.py
-h		shows help stuff
-stat		MANDATORY: list of stations USE 6 DIGITS, not 5(add a 0 if necessary) e.g. -stat 645000 645500 645010
-yrs		MANDATORY: from which year to which year you want to handle isd data? e.g. -yrs 1950 1990
-dl True	OPTIONAL: Do you want to download data and store it in data/<year> first? Then pass -dl True
-dec True 	OPTIONAL: Do you want to decode data and store in data/output? Then pass -dec True
-kassd True	OPTIONAL: Do you want to decode data and create a for KASSD readable file? Then pass -kassd True
-mmo True	OPTIONAL: Do you want to make files only with METAR data in data/output/met_* when decoding? Then pass -mmo True Default False
-mso True	OPTIONAL: Do you want to make files only with SYNOP data in data/output/syn_* when decoding? Then pass -mso True Default False
-mall True	OPTIONAL: Do you want to make files with all available data from isd into data/output/isd_*? Then pass -mall True Default True
-zisd True	OPTIONAL: Do you want to zip the created isd files? They are very big. Then pass -zisd True Default True

VARIABLES DESCRIPTION
The output file with ISD-, SYNOP-, and METAR-data in, has several variables:
wind_dir		wind direction [degrees]
wind_spd		wind speed [meter per second]
temp			temperature [celsius]
dtemp			dewpoint temperature [celsius]
press			pressure [hectopascal]
Sundur			Sun shine duration [hours]
synwea			Synoptic weather phenomena from 7th group (see synop Code)
synweco1		Synoptic weather condition from 7th group (see synop Code)
synweco2		Synoptic weather condition from 7th group (see synop Code)
metwe			Metar weather condition (eg: TS = Thunderstorm, see metar Code)
preci1			precipitation measured during certain time period [milimeter per hour] (up to 4 times)
precih1			certain time period for precipitation [hour] (up to 4 times)
clct			cloud cover total [oktas]
clfl			cloud cover of the lowest clouds [oktas]
clgl			cloud genus of low clouds [number]
clhl			cloud height of the low clouds [meters]
clgm			cloud genus of the middle clouds [number]
clgh			cloud genus of the high clouds [number]
ga[1-6]clc		cloud cover of this cloud layer [oktas] (up to 6 times)
ga[1-6]clh		cloud height of this cloud layer [meters] (up to 6 times)
ga[1-6]clt		cloud type(genus) of this layer [number] (up to 6 times)

Source: ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-format-document.pdf
Cloud types table low:
00 = No low clouds
01 = Cumulus humulis or Cumulus fractus other than of bad weather or both
02 = Cumulus mediocris or congestus, with or without Cumulus of species fractus or humulis or Stratocumulus all having bases at the same level
03 = Cumulonimbus calvus, with or without Cumulus, Stratocumulus or Stratus
04 = Stratocumulus cumulogenitus
05 = Stratocumulus other than Stratocumulus cumulogenitus
06 = Stratus nebulosus or Stratus fractus other than of bad weather, or both
07 = Stratus fractus or Cumulus fractus of bad weather, both (pannus) usually below Altostratus or Nimbostratus.
08 = Cumulus and Stratocumulus other than Stratocumulus cumulogenitus, with bases at different levels
09 = Cumulonimbus capillatus (often with an anvil), with or without Cumulonimbus calvus, Cumulus, Stratocumulus, Stratus or pannus
99 = Missing

Cloud types table low:
00 = No middle clouds
01 = Altostratus translucidus
02 = Altostratus opacus or Nimbostratus
03 = Altocumulus translucidus at a single level
04 = Patches (often lenticulre) of Altocumulus translucidus, continually changing and occurring at one or more levels
05 = Altocumulus translucidus in bands, or one or more layers of Altocumulus translucidus or opacus, progressing invading the sky; these Altocumulus clouds generally thicken as a whole
06 = Altocumulus cumulogentis (or cumulonimbogentus)
07 = Altocumulus translucidus or opacus in two or more layers, or Altocumulus opacus in a single layer, not progressively invading the sky, or Altocumulus with Altostratus or Nimbostratus
08 = Altocumulus castellanus or floccus
09 = Altocumulus of a chaotic sky; generally at several levels
99 = Missing

Cloud types table high:
00 = No High Clouds
01 = Cirrus fibratus, sometimes uncinus, not progressively invading the sky
02 = Cirrus spissatus, in patches or entangled sheaves, which usually do not increase and sometimes seem to be the remains of the upper part of a Cumulonimbus; or Cirrus castellanus or floccus
03 = Cirrus spissatus cumulonimbogenitus
04 = Cirrus unicinus or fibratus, or both, progressively invading the sky; they generally thicken as a whole
05 = Cirrus (often in bands) and Cirrostratus, or Cirrostratus alone, progressively invading the sky; they generally thicken as a whole, but the continuous veil does not reach 45 degrees above the horizon
06 = Cirrus (often in bands) and Cirrostratus, or Cirrostratus alone, progressively invading the sky; they generally thicken as a whole; the continuous veil extends more than 45 degrees above the horizon, without the sky being totally covered.
07 = Cirrostratus covering the whole sky
08 = Cirrostratus not progressively invading the sky and not entirely covering it
09 = Cirrocumulus alone, or Cirrocumulus predominant among the High clouds
99 = Missing

Cloud types table of GA-group:
00 = Cirrus (Ci)
01 = Cirrocumulus (Cc)
02 = Cirrostratus (Cs)
03 = Altocumulus (Ac)
04 = Altostratus (As)
05 = Nimbostratus (Ns)
06 = Stratocumulus (Sc)
07 = Stratus (St)
08 = Cumulus (Cu)
09 = Cumulonimbus (Cb)
10 = Cloud not visible owing to darkness, fog, duststorm, sandstorm, or other analogous phenonomena/sky obcured
11 = Not used
12 = Towering Cumulus (Tcu)
13 = Stratus fractus (Stfra)
14 = Stratocumulus Lenticular (Scsl)
15 = Cumulus Fractus (Cufra)
16 = Cumulonimbus Mammatus (Cbmam)
17 = Altocumulus Lenticular (Acsl)
18 = Altocumulus Castellanus (Accas)
19 = Altocumulus Mammatus (Acmam)
20 = Cirrocumulus Lenticular (Ccsl)
21 = Cirrus and/or Cirrocumulus
22 = jenkins-content-114Stratus and/or Fracto-stratus
23 = Cumulus and/or Fracto-cumulus
99 = Missing
