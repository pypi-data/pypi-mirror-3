from numpy.random import randint
from numpy import sort
from scipy.io import savemat

neuron_count = 10
spike_count = 10
duration = 1000

#Assuming data is in ms
simulated_data = randint(duration, size=(neuron_count,spike_count))
simulated_data = sort(simulated_data,axis=1)
filename = 'simulated.mat'
savemat(filename,mdict={'data':simulated_data})