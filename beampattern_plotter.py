import numpy as np
import matplotlib.pyplot as plt
import scipy as sci
from scipy.fft import fft, fftfreq, ifft, fftshift, ifftshift

#Environmental parameters
temp = 12 #water temp. in celsius
depth = 1/.016 #assuming pressure is negligible for application, setting to reciporical of weight
salinity = 0.0005 #set to .05%, max salinity for freshwater
#approximation for sound velocity in m/s based on environmental parameters
#sound_velocity = 1449.2 + 4.6*temp - (0.055* temp)**2 + (0.00029 * temp)**3 + (1.34- 0.01 * temp) * (salinity-35) + 0.016*depth
sound_velocity = 1500 #simple c assumption

#Sampling parameters
fs = 40000 # sample freq
T = 1/fs #sample period
t_to_sample = 2; #time in seconds to sample for
N = fs * t_to_sample #num samples

#RCV Arry parameters
el_space = .298

#Sin wave to shift for beampattern
f_sin = 2400 # beam pattern changes with frequency
t = np.linspace(0,N*T,N, endpoint=False)
s1 = np.sin(2*np.pi*f_sin*t) #simple sin wave

# Set sin wave as received signal for each element
rcv_matrix = np.zeros((8, len(s1)))
for n in range(0,7):
    rcv_matrix[n] = s1

#define azimuth range
min_az = 0
max_az = 180
az_fidelity = 1
az_matrix = np.arange(min_az,max_az + az_fidelity,az_fidelity)
beam_power = []

#for each azimuth
for az_i in range(len(az_matrix)):
    # only care about frequency bin at sin freq.
    bins = ([f_sin])
    time_data = np.zeros_like(rcv_matrix[0]).astype(complex)
    
    # For each element, apply freq domain shift then ifft
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
fig = plt.figure()

plt1 = fig.add_subplot(1,2,1)
plt1.set_xlabel("Scan Angle (degrees)")
plt1.set_ylabel("Power dB//W")
plt1.set_title("ULA Beampattern 2400 Hz")
plt1.grid(True)
plt1.plot(az_matrix,20*np.log10(beam_power))

plt2 = fig.add_subplot(1,2,2,projection='polar')
plt2.set_xlabel("Scan Angle (degrees)")
plt2.set_ylabel("Power dB//W")
plt2.set_title("ULA Beampattern 2400 Hz")
plt2.plot(az_matrix*np.pi/180,20*np.log10(beam_power))

plt.show()