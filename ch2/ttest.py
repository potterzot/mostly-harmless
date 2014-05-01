#!/usr/bin/python

"""
Open the 2005 data and get the file
"""

##########
## MODULES
import sys
import zipfile
import os
import os.path
import getopt

#data analysis modules
import pandas as p
import numpy as np
import matplotlib.pyplot as plt
import stats as s
import scipy.stats as stats

########
##GLOBALS
FILE_LOC = "/home/potterzot/data/nhis/"
FILE_NAMES = [
    "2005_personsx.exe"
]



########
## For each file, open it and extract into a data frame
for f in FILE_NAMES:
    # open the zipped file, then extract the data we want
    zf = zipfile.ZipFile(FILE_LOC+f)
    for i, name in enumerate(zf.namelist()):
        # open the file and read the necessary data
        of = zf.open(name)

        # list to fill with data
        li = []
        
        for line in of:
            data = line.decode('utf-8')
            # have to read the codebook for these fixed-width data.
            # phospyr is in hospital that year, column 519
            # phstat is reported health status, column 516
            li.append({"in_hospital": int(data[518]), "health_status": int(data[515])})
        
        # generate the data frame
        df = p.DataFrame(li, columns=["in_hospital", "health_status"])
        
        # value codes are as follows:
        # health_status: 1-5 is poor,fair, good, very good, excellent 
        # in_hospital: 1=yes, 2=no
        # 7-9 are refused, not ascertained, don't know

        # remove the records with invalid responses
        df2 = df[(df['in_hospital']<=2) & (df['health_status']<=5)]

        health_h1 = df2['health_status'][df2['in_hospital']==1]
        health_h0 = df2['health_status'][df2['in_hospital']==2]

        # First, count number of records to make sure we match MHE. Should be
        # 07774 hospital
        # 90049 no hospital
        n = len(df2)
        n_h1 = len(health_h1)
        n_h0 = len(health_h0)
        mean_h1 = s.mean(health_h1)
        mean_h0 = s.mean(health_h0)
        stdev_h1 = s.stdev(health_h1)
        stdev_h0 = s.stdev(health_h0)
        sterr_h1 = s.sterrmean(stdev_h1, n_h1)
        sterr_h0 = s.sterrmean(stdev_h0, n_h0)

        # calculate two-sample t-test to test if means are significantly different
        tt = (mean_h1 - mean_h0)/np.sqrt((stdev_h1**2/float(n_h1)) + (stdev_h0**2/float(n_h0)))
        pval = stats.t.sf(np.abs(tt), n-1)*2 # two sided t-value, prob(abs(t))>tt
       
        # do the same using scipy.stats canned routine
        # unequal variance
        tt2 = float(stats.ttest_ind(health_h1, health_h0, equal_var=0)[0])
        pval2 = stats.t.sf(np.abs(tt2), n-1)*2 # two sided t-value, prob(abs(t))>tt

        print("Total Sample: {0}".format(n))
        print("Group\t\tSample Size\t\tMean\t\tStd. Err")
        print("Hospital\t\t {0} \t\t {1} \t\t {2}".format(n_h1, round(mean_h1,2), round(sterr_h1,3)))
        print("No Hospital\t\t {0} \t\t {1} \t\t {2}".format(n_h0, round(mean_h0,2), round(sterr_h0,3)))
        print("By Hand: T-value: {0}, P-value: {1}".format(tt, pval))
        print("Canned: T-value: {0}, P-value: {1}".format(tt2, pval2))
