import numpy as np
import matplotlib.pyplot as plt
import scipy as sci
from scipy.fft import fft, fftfreq, ifft, fftshift, ifftshift
from scipy.io import wavfile

# read in data files
def assemble_data_matrix(num_sensors, path_name):
    '''
    Function Purpose: assemble matrix of hydrophone data where row = hydrophone
    and column = samples from respective sensor

    Inputs: 
            name: datatype, description 
            num_sensors: int, Total # of hydrophones colecting data
            path_name: str, exepects entire pathname including file name up to (not including)
            sensor number, i.e, "/Users/Downloads/Experiment_data/tone1_18/18-Jul-2026 12_03_31ch"
                --> the sensor # and .wav will be appended within the function
    Outputs:
            name: datatype, description
            xdata: np.ndarray, vertically assembled data into a matrix where the shape is # sensors, # of samples per sensor
                i.e xdata.shape(8, 1000)
            fs: float, sampling frequency for data samples (should be the same for all sensors)
    '''
    sensor_data_channels = []
    for sensor in range(num_sensors):
        fs, x = wavfile.read(path_name + str(sensor+1) + ".wav")
        sensor_data_channels.append(x)
    x_data = np.vstack(sensor_data_channels)
    return fs, x_data

# Call function
fs, rcv_matrix = assemble_data_matrix(8,"filepathhere")

#Environmental parameters
temp = 12 #water temp. in celsius
depth = 1/.016 #assuming pressure is negligible for application, setting to reciporical of weight
salinity = 0.0005 #set to .05%, max salinity for freshwater
#approximation for sound velocity in m/s based on environmental parameters
#sound_velocity = 1449.2 + 4.6*temp - (0.055* temp)**2 + (0.00029 * temp)**3 + (1.34- 0.01 * temp) * (salinity-35) + 0.016*depth
sound_velocity = 1500 #simple c assumption

#Sampling parameters
T = 1/fs #sample period

#RCV Arry parameters
el_space = .298
positions = np.arange(0,8)*el_space

#define azimuth range
min_az = 0
max_az = 180
az_fidelity = 5
az_matrix = np.arange(min_az,max_az + az_fidelity,az_fidelity)
#az_matrix = np.array([2.721661288,2.496388992,2.325177267,2.178152043,2.04491944,1.920286501,1.801106206,1.685185239,1.570796327,1.456407415,1.340486448,1.221306152,1.096673214,0.9634406105,0.816415387,0.6452036621,0.4199313654])
#az_matrix = np.array([155.9397051,143.0325532,133.222844,124.7989192,117.1652534,110.024312,103.195784,96.55400189,90,83.44599811,76.80421596,69.97568802,62.83474665,55.2010808,46.777156,36.96744676,24.06029492])
beam_power = []

#for each azimuth
for az_i in range(len(az_matrix)):
    #do delay and sum
    bins = fftshift(fftfreq(len(rcv_matrix[0]), T))
    time_data = np.zeros_like(rcv_matrix[0]).astype(complex)
    for num in range(0,7):
        tau_d = (num*el_space*np.cos((az_matrix[az_i]*np.pi)/180))/sound_velocity
        freq_data = fftshift(fft(rcv_matrix[num]))
        freq_data_shifted = np.zeros_like(freq_data)
        for i in range(len(bins)):
            freq_data_shifted[i] = freq_data[i] * np.exp(1j*2*np.pi*bins[i]*tau_d)
        time_data += ifft(ifftshift(freq_data_shifted))
    
    #calculate power of delay and sum data
    power = np.var(time_data)
    #add to beam array
    beam_power.append(power)

beam_power = np.array(beam_power)
#normalize
beam_power /= np.max(beam_power)
#plot
plt.xlabel("Scan Angle (degrees)")
plt.ylabel("Power dB//W")
plt.title("Beamformer Scan: Power vs. Angle")
plt.grid(True)
plt.plot(az_matrix,20*np.log(beam_power))
#plt.polar(az_matrix*np.pi/180,beam_power)
plt.show()