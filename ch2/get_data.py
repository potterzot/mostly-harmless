#!/usr/bin/python
"""
Get NHIS survey data for use in MHE chapter 2. For each year from 1997 to present
the file must be downloaded and then unzipped and processed. For now only collects
1997 to present, since the 1996 and earlier are a different format.
"""

URL_BASE = "ftp.cdc.gov"
DIR_BASE = "pub/Health_Statistics/NCHS/Datasets/NHIS/"
LOCAL_BASE = "/home/potterzot/data/nhis/"
FILES = [
    "familyxx", #Family
    "househld", #Household
    "injpoiep", #Injury Episode
    "personsx", #Person file
    "samchild", #Child sample
    "childcam", #Child alternative medicine
    "samadult", #Adult sample
    "althealt", #Adult alternative medicine
]



def get_nhis(start_year=1997, end_year=2012):
    """Only works for 1997-present."""
    from ftplib import FTP
    #from urllib.request import urlretrieve

    for year in range(start_year, end_year):
        
        # Get a FTP connection and change to working directory
        ftp = FTP(URL_BASE)
        ftp.login()
        ftp.cwd(DIR_BASE+str(year))
        
        # get list of files at location
        filelist = []
        ftp.retrlines('LIST', filelist.append)

        for f in filelist:
            ## For each file, open a local file and save the file into it.
            fname = f.split(' ')[-1] # the file name is the last item in the parsed array
            lfname = str(year)+"_"+fname
            print('Saving file: '+lfname)
            local_file = LOCAL_BASE+lfname
            lf = open(local_file, "wb") #have to make sure to use "wb" for windows
            try:    
                ftp.retrbinary('RETR ' + fname, lf.write) #gets the file
            except:
                print(lfname+" not downloaded...")
            lf.close()


def main():
    get_nhis();

# This makes the program run when called from the command line but not when imported as a module
if __name__ == '__main__':
    main()



