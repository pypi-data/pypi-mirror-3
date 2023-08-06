from scipy.io import loadmat
import ISIpy as ISIpy

use_real_data = False
filename = 'yourdata.mat' if use_real_data else 'simulated.mat'


ISI_record = ISIpy.ISIpy(data_location = filename)