#!/usr/bin/python
"""
Analyze the STAR data to reproduce tables 2.2.1 and 2.2.2 from MHE

"""

##########
## Modules
import pandas as p
import numpy as np
import stats as s

###########
# Functions

# interpolate missing reading scores
def interpolate(data_to_interpolate, using=False, extrapolate=False):
    """
    Replicate stata's ipolate command. 
    If one variable is provided, then just fill with the linear average over missing values
    If two variables are provided, use the second to provide the interpolation weights for the first
    If extrapolate, then also fill in missing data that is not enclosed on both ends
    """
    


    return result


# data downloaded from: http://economics.mit.edu/files/3827
# pandas has a read_stata definition that lets us access the data
star = p.read_stata('/home/potterzot/data/star/webstar.dta')

# Krueger made some modifications, but fortunately he was kind enough
# to put his stata do files on the web, so we can easily follow along in python

## create some variables for regression
# white/asian dummy
star['wa'] = (star['srace'] == 'white')| (star['srace'] == 'asian')

# age in 1985
star['age85'] = 1985 - star['sbirthy']
#star['age85'][star['sbirthq']=='1st qtr - jan,feb,march'] += 1
#star['age85'][star['sbirthq']=='2nd qtr - april,may,june'] += 1
#star['age85'][star['sbirthq']=='3rd qtr - july,aug,sept'] += 1
star['age85'][star['sbirthq']=='4th qtr - oct,nov,dec'] += 1

# female
star['female'] = (star['ssex']==2)

# nwhite...
star['nwhite'] = ((star['srace']!='white'))

# constant
star['n'] = 1

# free lunch
star['fl'] = None
star['fl'][star['sesk']=='free lunch'] = 1
star['fl'][star['sesk']=='non-free lunch'] = 0

# attrition rate
star['attr'] = None
star['attr'][star['stark']=='yes'] = 0
star['attr'][(star['stark']=='yes') & (star['star3']=='yes')] = 1

## scaled reading score, keeping regular classes and valid scores
# keep only regular classes with a positive score
treadssk = star[(star['treadssk']>0) & ((star['cltypek']=='regular + aide class') | (star['cltypek']=='regular class'))]['treadssk'].copy()

# sort by score
treadssk.sort()

# make a data frame
read = p.DataFrame(treadssk)

# add the row number
read['n'] = range(0,len(read))

# create percentage
read['pread0'] = 100*read['n']/len(read)

# create the percentage grouped by score
pread = read.groupby('treadssk').mean()


## Scaled math score
tmathssk = star[(star['tmathssk']>0) & ((star['cltypek']=='regular + aide class') | (star['cltypek']=='regular class'))]['tmathssk'].copy()

# sort by score
tmathssk.sort()

# make a data frame
math = p.DataFrame(tmathssk)

# add the row number
math['n'] = range(0,len(math))

# create percentage
math['pmath0'] = 100*math['n']/len(math)

# create the percentage grouped by score
pmath = math.groupby('tmathssk').mean()


## Add scaled scores back to data set
# just kindergarten
stark = star[star['stark']=='yes'].copy()

# merge on reading scores
stark_read = p.merge(stark, pread, left_on='treadssk', right_index=True, how='left')

# merge on math scores
stark2 = p.merge(stark_read, pmath, left_on='tmathssk', right_index=True, how='left')

# TODO: interpolate missing values
stark3 = stark2.sort(['pread0'])
#stark2.inerpolate


# replace 0s
stark3['pread0'][stark3['pread0']<0] =  0
stark3['pmath0'][stark3['pmath0']<0] =  0

# average test score
stark3['pscore'] = (stark3['pread0']+stark3['pmath0'])/2

# Generate class ids
stark3['classid1'] = stark3.groupby(['schidkn', 'cltypek']).



class_size = p.DataFrame(stark3.groupby(['schidkn', 'cltypek'])['newid'].count())
class_size['clsize'] = class_size[0]

stark4 = p.merge(stark3, class_size, left_on=['schidkn', 'cltypek'], right_index=True)


##############
## Table 2.2.1
star221 = stark4[stark4['stark']=='yes']
means = {'fl':{}, 'wa':{}, 'age85':{}, 'attr': {}, 'clsize': {}, 'pscore': {}}
for cltype in ['small class', 'regular class', 'regular + aide class']:
    for var in means.keys():
        # we test for NaN with (star[var]==star[var])
        # sample is 
        means[var][cltype] = s.mean(star221[var][(star221[var]==star221[var]) & (star221['cltypek'] == cltype)])

# F statistic of difference between means of 3 class types
fstats = {}
fstats['fl'] = 1
fstats['wa'] = 1
fstats['age85'] = 1
fstats['attr'] = 1
fstats['clsize'] = 1
fstats['pscore'] = 1

# Print out results:
print("Replication of Table 2.2.1 Values")
print("Variable\t\tSmall\tRegular\t\tReg.+Aide\tF-stat")
print("Free Lunch:\t\t{0}\t{1}\t\t{2}\t\t{3}".format(round(means['fl']['small class'],2), round(means['fl']['regular class'],2), round(means['fl']['regular + aide class'],2), round(fstats['fl'],2)))
print("White/Asian:\t\t{0}\t{1}\t\t{2}\t\t{3}".format(round(means['wa']['small class'],2), round(means['wa']['regular class'],2), round(means['wa']['regular + aide class'],2), round(fstats['wa'],2)))
print("Age in 1985:\t\t{0}\t{1}\t\t{2}\t\t{3}".format(round(means['age85']['small class'],2), round(means['age85']['regular class'],2), round(means['age85']['regular + aide class'],2), round(fstats['age85'],2)))
print("Attrition Rate:\t\t{0}\t{1}\t\t{2}\t\t{3}".format(round(means['attr']['small class'],2), round(means['attr']['regular class'],2), round(means['attr']['regular + aide class'],2), round(fstats['attr'],2)))
print("Class Size:\t\t{0}\t{1}\t\t{2}\t\t{3}".format(round(means['clsize']['small class'],2), round(means['clsize']['regular class'],2), round(means['clsize']['regular + aide class'],2), round(fstats['clsize'],2)))
print("Percentile Score:\t{0}\t{1}\t\t{2}\t\t{3}".format(round(means['pscore']['small class'],2), round(means['pscore']['regular class'],2), round(means['pscore']['regular + aide class'],2), round(fstats['pscore'],2)))


##############
## Table 2.2.2







