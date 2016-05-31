"""
This file contains all the functions for ExoTRed Package

@author: Walter Martins-Filho
e-mail: walter at on.br
        waltersmartinsf at gmail.com

"""


"""
Loading packges and python useful scritps
"""
from pyraf import iraf #loading iraf package
from login import * #loading login.cl parameters for iraf
from ExoSetupTaskParameters import * #loading setup from PyExoDRPL
import useful_functions as use
import glob #package for list files
import os #package for control bash commands
import yaml #input data without any trouble
import string
import numpy as np
from astropy.io import fits
from astropy.time import Time #control time in fits images
from astropy.coordinates import SkyCoord,get_sun,ICRS #get the Sun position from a instant of time
from pandas import DataFrame, read_csv
from string import split #use to unconcanated a string in parts
#import string #transform a list in a string of caracters
#from pandas import HDFStore #save data in a database


def input_info(path_input):
    """
    Obtain information about the files that will be reduced or analised.
    ___
    Input:

    path_input: string, path of your yaml file directory with the information of the data

    Return:

    save_path: string, path where is your data to be reduced.
    data_path: string, path where the data reduced will be saved.
    input_file: dictionary, information from YAML file.

    """
    #path for your data directory, path for your data save, and names for the lists
    #Import with yaml file: input path and prefix information for files
    input_file = glob.glob(path_input+'*.yaml')
    if input_file: #if exist the input file, the code will obtain all information We need to run all tasks
        if len(input_file) == 1: #if there is only one yaml file, obtain data and save paths, and return that with a dictionary with information
            print 'reading input file ... \n'
            file = yaml.load(open(input_file[0])) #creating our dictionary of input variables
            data_path = file['data_path']
            save_path = file['save_path']
            print '....  done! \n'
            if len(input_file) > 1: #if are more than one yaml file,. the code will ask to you remove the others.
                print 'reading input file ... \n'
                print '.... there is more than 1 input_path*.yaml.\n \nPlease, remove the others files that you do not need. \n'
                raise SystemExit
    else:
        #if aren't a yaml file, the code ask for you to put a valid yaml file path.
        print 'There is no input_path*.yaml. \nPlease, create a input file describe in INPUT_PARAMETERS.'
        raise SystemExit
    input_file = file #creating a better name to our dictionary info
    return data_path, save_path, input_file

def masterbias(data_path, save_path, input_file):
    """
    Obtain the masterbias.fits image.
    ___
    Input:
    For obtain this parameters, use the input_info function.

    data_path: string, path where are the images data.
    save_path: string, path where will save all reduced images.
    input_file: dict, with information describe in the YAML file.

    Output:
    It is possible that the function return some of these values:

    0. Create the masterbias image on the save_path.
    1. It do not create the masterbias image, because of some error
    ___
    """
    #Set original directory
    original_path = os.getcwd()
    #Change your directory to data diretory
    os.chdir(data_path)
    #list all bias images
    bias = glob.glob('bias*.fits')
    print 'Loading bias images \nTotal of bias files = ',len(bias),'\nFiles = \n'
    print bias
    print '\nCreating superbias \n'
    #if save_path exist, continue; if not, create.
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #copy bias images to save_path
    os.system('cp bias*.fits '+save_path)
    #change to sabe_path
    os.chdir(save_path)
    #verify if previous superbias exist
    if os.path.isfile('superbias.fits') == True:
        os.system('rm superbias.fits')
    #create the list of bias images
    bias_list = string.join(bias,',')
    #combine the bias image and create the superbias
    iraf.imcombine(bias_list,'superbias.fits')
    iraf.imstat('superbias.fits')
    #clean previos bias files
    print '\n Cleaning bias*.fits images ....\n'
    os.system('rm bias*.fits')
    print '\n.... done.'
    #print output
    #test of outpu value
    #os.remove('superbias.fits')
    #Verify if the image was created:
    output = glob.glob('superbias*.fits')
    if len(output) != 0:
        output = 0
    else:
        output = 1
    #Return to original directory
    os.chdir(original_path)
    #END of the masterbias reduction messsage
    print '\nsuperbias.fits created!\n'
    print '\nEND of superbias reduction!\n'
    #obtain the value of return
    if output == 1:
        print '!!! ERROR/WARNING !!!'
        print 'Check if the superbias was created or if there is more than one superbias image.'
    return output

def masterflat(data_path,save_path,input_file):
    """
    Obtain the masterflat image for calibration.
    ___
    INPUT:
    For obtain this parameters, use the input_info function.

    data_path: string, path where are the images data.
    save_path: string, path where will save all reduced images.
    input_file: dict, with information describe in the YAML file.

    OUTPUT:
    It is possible that the function return some of these values:

    0. Create the masterflat image on the save_path.
    1. It do not create the masterflat image, because of some erros.
    """
    #set original directory
    original_path = os.getcwd()
    #Change your directory to data diretory
    os.chdir(data_path)
    #list all flat images
    flat = glob.glob('flat*.fits')
    print 'Loading flat images \nTotal of flat files = ',len(flat),'\nFiles = \n'
    print flat
    #if save_path exist, continue; if not, create.
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #create a list of bias images and copy images to save_path
    os.system('cp flat*.fits '+save_path)
    #creating the names of flat with bias subctracted
    bflat = []
    for i in flat:
        bflat.append('B'+i)
    print '\n Names os flat images with bias subtracted: \n \n',bflat
    #change for save_path directory
    os.chdir(save_path)
    #verify if previous superbias exist
    if os.path.isfile('superflat.fits') == True:
        os.system('rm superflat.fits')
    #verify if exits previous bflat*.fits files and remove then.
    for i in bflat:
        if os.path.isfile(i) == True:
            os.system('rm -f '+i)
    print '\nCreating superflat .... \n'
    #create the list of flat images  and bflat images
    #flat = string.join(flat,',')
    #bflat = string.join(bflat,',')
    print '\n Subtracting bias from flat images and creating bflat images.... \n'
    #iraf.imarith()
    for i in range(len(flat)):
        iraf.imarith(flat[i],'-','superbias.fits',bflat[i])
        #print statistics from bflat*.fits images
        iraf.imstat(bflat[i])
    print '\n .... done \n'
    #clean previos flat*.fits files
    print '\n Clean flat*.fits images .... \n'
    os.system('rm flat*.fits')
    print '\n .... done. \n'
    #normalizing each flat
    print '\nNormalizing each flat ....\n'
    #checking if mean from numpy is the same from your bflat images using imstat
    #take the mean of each bflat image
    bflat_mean = np.zeros(len(bflat))
    for i in range(len(bflat)):
        image = fits.getdata(bflat[i])
        image = np.array(image,dtype='Float64')
        bflat_mean[i] = round(np.mean(image))
    image = 0 #clean image allocate to this variable
    print 'The mean of each bflat image, respectivaly ...'
    print bflat_mean
    #creating the names of bflat images after the normalization:
    abflat = []
    for i in bflat:
        abflat.append('A'+i)
    print '\n Names os bflat images with bias subtracted and normalizad: \n \n',abflat
    #verify if exist previous ABflat*.fits images and remove then.
    for i in abflat:
        if os.path.isfile(i) == True:
            os.system('rm -f '+i)
    for i in range(len(abflat)):
        iraf.imarith(bflat[i],'/',bflat_mean[i],abflat[i])
    print '\n.... done!\n'
    print '\n Cleaning bflat*.fits images ....\n'
    os.system('rm Bflat*.fits')
    print '\n.... done.\n'
    print 'Statistics of the abflat*.fits images .... \n'
    for i in range(len(abflat)):
        iraf.imstat(abflat[i])
    print '\n Combining abflat images ....\n'
    ablist = string.join(abflat,',')
    iraf.imcombine(ablist,'superflat.fits')
    iraf.imstat('superflat.fits')
    print '\n .... done. \n'
    print '\nCleaning ABflat*.fits images ....\n'
    os.system('rm ABflat*.fits')
    print '\n.... done!'
    #Verify if the image was created:
    output = glob.glob('superflat*.fits')
    if len(output) != 0:
        output = 0
    else:
        output = 1
    #Return to original directory
    os.chdir(original_path)
    #last mensage
    print '\n MASTERFLAT.FITS created! \n'
    print '\n END of Data Reduction for create a masterflat.fits file. \n'
    #obtain the value of return
    if output == 1:
        print '!!! ERROR/WARNING !!!'
        print 'Check if the superbias was created or if there is more than one superbias image.'
    return output

def science_reduction(data_path,save_path,input_file):
    """
    Calibrate science images with masterflat (or superflat) and masterbias (or superbias) images.
    ___
    INPUT:
    For obtain this parameters, use the input_info function.

    data_path: string, path where are the images data.
    save_path: string, path where will save all reduced images.
    input_file: dict, with information describe in the YAML file.

    OUTPUT:
    It is possible that the function return some of these values:

    0. Create the masterflat image on the save_path.
    1. It do not create the masterflat image, because of some erros.
    """
    #name of the planet
    planet = input_file['exoplanet']
    #set original directory
    original_path = os.getcwd()
    #Change your directory to data diretory
    os.chdir(data_path)
    #list all flat images
    exoplanet = glob.glob(planet+'*.fits')
    print '\nLoading exoplanet images \nTotal of '+planet+'*.fits  files = ',len(exoplanet),'\nFiles = \n'
    print exoplanet
    #if save_path exist, continue; if not, create.
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #create a list of bias images and copy images to save_path
    print '\nCopy science images to save_path directory to main reduction: ....'
    os.system('cp '+planet+'*.fits '+save_path)
    print '\n .... done. \n'
    #change to save_path
    os.chdir(save_path)
    #create the names for exoplanet science mages with bias subtracted
    bexoplanet = []
    for i in exoplanet:
        bexoplanet.append('B'+i)
        #verify if previous superbias exist
        if os.path.isfile('B'+i) == True:
            os.system('rm B'+i)
    print '\n Will be create this images: \n'
    print bexoplanet
    #exoplanet = string.join(exoplanet,',') #create the list string of exoplanet science images
    #bexoplanet = string.join(bexoplanet,',')#create the list string of bexoplanet science images
    print '\nSubtracting superbias.fits from all '+planet+'*.fits images ....\n'
    for i in range(len(exoplanet)):
        iraf.imarith(exoplanet[i],'-','superbias.fits',bexoplanet[i])
        use.update_progress((i+1.)/len(bexoplanet))
    print '\n.... cleaning '+planet+'*.fits images\n'
    os.system('rm '+planet+'*.fits')
    print '\n Statistics of B'+planet+'*.fits images: \n'
    for i in range(len(bexoplanet)):
        iraf.imstat(bexoplanet[i])
    print '\nFlatfielding the B'+planet+'*.fits ....\n'
    #create the names for exoplanet science images with bias subtracted and flatfielding
    abexoplanet = []
    for i in bexoplanet:
        abexoplanet.append('A'+i)
        #verify if previous superbias exist
        if os.path.isfile('A'+i) == True:
            os.system('rm A'+i)
    print '\n Will be create this images: \n'
    print abexoplanet
    #flatifielding images
    for i in range(len(abexoplanet)):
        iraf.imarith(bexoplanet[i],'/','superflat.fits',abexoplanet[i])
        use.update_progress((i+1.)/len(abexoplanet))
    print '\n.... cleaning B'+planet+'*.fits images\n'
    os.system('rm B'+planet+'*.fits')
    print '\n Statistics of AB'+planet+'*.fits images: \n'
    for i in range(len(abexoplanet)):
        iraf.imstat(abexoplanet[i])
    os.chdir(original_path) #change to save_path
    return

def time_info(data_path,save_path,input_file):
    """
    Obtain the Sideral Time and the Heliocentric Jullian Date from the header of the images.
    ___
    INPUT:
    For obtain this parameters, use the input_info function.

    data_path: string, path where are the images data.
    save_path: string, path where will save all reduced images.
    input_file: dict, with information describe in the YAML file.

    OUTPUT:
    It is possible that the function return some of these values:

    0. Create the masterflat image on the save_path.
    1. It do not create the masterflat image, because of some erros.
    """
    original_path = os.getcwd() #set original directory
    planet = input_file['exoplanet'] #set exoplanet name
    print '\nObtain the images .... \n'
    print 'Change to ', save_path
    os.chdir(save_path) #change to save directory where is our scvience images
    images = sorted(glob.glob('AB'+input_file['exoplanet']+'*.fits'))
    print '\nImages = \n',images
    tempo_loc = [] #time object
    SUN = [] #Sun coordinate object
    ra_sun, dec_sun, dsun = np.zeros(len(images)),np.zeros(len(images)),np.zeros(len(images)) #sun coordinates
    JD = np.zeros(len(images)) #julian date from time object
    ST = np.zeros(len(images))
    HJD = np.zeros(len(images))
    #create the exoplanet object coordianate
    exoplanet = SkyCoord(dec=input_file['DEC'],ra=input_file['RA'],unit=('deg','deg'),frame=input_file['frame'])
    print '\nObtain data info from header ....\n'
    for i in range(len(images)):
        hdr = fits.getheader(images[i])
        UTC = hdr['date-obs']+'T'+hdr['UT'] #string that contain the time in UTC in isot format
        tempo_loc.append(Time(UTC,scale=input_file['scale-time'],format='isot',location=(input_file['lon-obs'],input_file['lat-obs'])))#,input_data['altitude'])))
        JD[i] = tempo_loc[i].jd
        ST[i] = tempo_loc[i].sidereal_time('apparent').hour
        SUN.append(get_sun(tempo_loc[i]))
        ra_sun[i],dec_sun[i] = SUN[i].ra.deg, SUN[i].dec.deg
        dsun[i] = SUN[i].distance.value
        HJD[i] = use.hjd_date(JD[i],dsun[i],dec_sun[i],ra_sun[i],exoplanet.dec.deg,exoplanet.ra.deg,circular_orbit=input_file['circular_orbit'])
        use.update_progress((i+1.)/len(images))
    print '\n.... done.\n'
    print '\n Time from header = \n'
    #print '\nImages ** UTC (YYYY-MM-DDTHH:MM:SS) ** JD (7d.5d) ** ST (hours) ** ST (HH:MM:SS) ** Sun Coordinate (epoch,RA,DEC,Distance) (deg,deg,AU) \n'
    ST_string = []
    for i in range(len(images)):
        ST1 = int(ST[i])
        ST2 = int((ST[i]-ST1)*60.)
        ST3 = (((ST[i]-ST1)*60.)-ST2)*60
        ST_string.append(str(ST1)+':'+str(ST2)+':'+str(ST3))
        tempo_loc[i] = tempo_loc[i].value
        use.update_progress((i+1.)/len(images))
        #print images[i], ' ** ',tempo_loc[i], ' ** ', JD[i], ' ** ', ST[i],' ** ',ST_string[i],' ** ',sun_loc[i],' ** ',HJD[i]
    print '\nSave data file ... \n'
    data = DataFrame([images,tempo_loc,list(JD),list(ST),list(ST_string),list(ra_sun),list(dec_sun),list(dsun),list(HJD)]).T
    data.columns=['images','UTC','JD','ST','ST_isot','RA_SUN','DEC_SUN','D_SUN','HJD']
    print data
    data.to_csv('results.csv')
    os.chdir(original_path)
    return

def time_calibration(data_path,save_path,input_file):
    """
    Obtain the calibration for time (hjd) by pyraf and the airmass for each image. Include in the header all information.
    """
    original_path = os.getcwd()
    #change to save data reduction directory
    os.chdir(save_path)
    print '\n Reading the list of images ....\n'
    planet = input_file['exoplanet'] #set exoplanet name
    images = sorted(glob.glob('AB'+planet+'*.fits'))
    print images
    #include de RA,DEC and epoch of the exoplanet
    RA,DEC,epoch = input_file['RA'],input_file['DEC'],input_file['epoch']
    #obtain ST JD using iraf task and introduce in the header
    for i in range(len(images)):
        hdr = fits.getheader(images[i])
        if int(split(hdr['UT'],':')[0]) < int(hdr['timezone']):
            new_date = use.yesterday(hdr['date-obs'])
            #print images[i], new_date
        else:
            new_date = hdr['date-obs']
        year,month,day = split(new_date,'-')
        iraf.asttimes(year=year,month=month,day=day,time=hdr['loctime'],obs=input_file['observatory'])
        JD = iraf.asttimes.jd #obtain julian date
        LMST = iraf.asttimes.lmst #obtain the sideral time
        LMST = use.sexagesimal_format(LMST) #convert sideral time in sexagesimal format
        iraf.hedit(images[i],'ST',LMST,add='yes',verify='no',show='no',update='yes') #create the ST keyword in the header
        iraf.ccdhedit(images[i],'LMST',LMST,type='string') #include the mean sideral time in the header
        iraf.ccdhedit(images[i],'JD',JD,type='string') #include de julian date in the header
        #include RA, and DEC of the object in your header
        iraf.ccdhedit(images[i],"RA",RA,type="string") #include right ascention in the header
        iraf.ccdhedit(images[i],"DEC",DEC,type="string")  #include declination in the header
        iraf.ccdhedit(images[i],"epoch",epoch,type="string") #include epoch in the header
        # use.update_progress((i+1.)/len(images))
    print '\n Setting airmass ....\n'
    for i in range(len(images)):
        print '# ',images[i]
        #iraf.hedit(images[i],'airmass',airmass,add='yes')
        #iraf.hedit(images[i],'HJD',HJD,add='yes')
        iraf.setairmass.observatory = input_file['observatory']
        iraf.setairmass(images[i])
        iraf.setjd.time = 'ut'
        iraf.setjd(images[i])
    print '\n.... done.\n'
    #export information
    hjd, jd, airmass, st = [],[],[],[]
    for i in range(len(images)):
        hdr = fits.getheader(images[i])
        hjd.append(hdr['HJD'])
        jd.append(hdr['JD'])
        airmass.append(hdr['airmass'])
        st.append(hdr['st'])
    #saving the data
    data = DataFrame([list(hjd),list(jd),list(st),list(airmass)]).T
    data.columns = ['HJD','JD','ST','Airmass']
    data.to_csv('results_iraf_calibrations.csv')
    #change to workings directory
    os.chdir(original_path)
    return
