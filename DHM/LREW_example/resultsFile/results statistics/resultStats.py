# -*- coding: utf-8 -*-
"""
This program is used to do statistics (coefficient of determination, Nash-Sutcliffe coefficient, and 
percent bias) comparing simulated and observed data.

Created on Wed, Apr 27, 2016, and modified on June 28, 2017
by Sisi Li
"""

import pandas as pd
import numpy as np

# Set the input simulated daily data file name
Sim_file = 'fOutput_baseline.txt'
# Set the file name of the observed data 
Obs_file = 'flow_obs.txt'
# Set the statistic period
startDay = '2005-1-1'
endDay = '2006-12-31'

"""
--------------------------------------------------------------------------------------
Above is input parameters, including data and parameters, below is analysis.
Generally, there is no need to change the content below, unless modifying the script.
--------------------------------------------------------------------------------------
"""
# Read in observed daily data
obs_read = pd.read_csv(Obs_file, sep='\t', skiprows=1, header=0, index_col=0, parse_dates=True)
obs = obs_read.dropna()
# Read in simulated daily data
sim = pd.read_csv(Sim_file, sep='\t', skiprows=1, header=0, index_col=0, parse_dates=True)
# Select periods for comparison
obs_d = obs[startDay:endDay]
sim_d = sim[startDay:endDay]
# Calculate monthly mean for simulated data
obs_m = obs_d.resample('M').mean()
sim_m = sim_d.resample('M').mean()
 
# Calculate Nash-Sutcliffe coefficient
ENS_m = 1 - np.sum((sim_m - obs_m)**2,axis=0) / np.sum((obs_m - obs_m.mean())**2,axis=0)
ENS_d = 1 - np.sum((sim_d - obs_d)**2,axis=0) / np.sum((obs_d - obs_d.mean())**2,axis=0)
# Calculate coefficient of determination
R2_m = (sim_m.corrwith(obs_m))**2
R2_d = (sim_d.corrwith(obs_d))**2
# Calculate percent of bias
PBIAS = 100*((obs_d - sim_d).mean())/(obs_d.mean())

print 'PBIAS'
print PBIAS
print 'R2_monthly'
print R2_m
print 'ENS_monthly'
print ENS_m
print 'R2_daily'
print R2_d
print 'ENS_daily'
print ENS_d


