import numpy as np
import matplotlib.pyplot as plt
import scipy as sci
from scipy.fft import fft, fftfreq, ifft

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
el_space = .2  # measured in m TODO actually measure spacing, this is a guess
positions = np.arange(0,8)*el_space

#Simulated data parameters
f_sin = 8000 # sin freq.
t = np.linspace(0,N*T,N, endpoint=False)
s1 = np.sin(2*np.pi*f_sin*t) #simple sin wave

theta_deg = 30
theta_rad = (30*np.pi)/180

rcv_matrix = np.zeros((8, len(s1)))

#i think this is just inverse beamforming???
for n in range(0,7):
    tau = (n*el_space*np.sin(theta_rad))/sound_velocity
    s1_f = fft(s1)
    bins = fftfreq(N, T)[0:N//2]
    s1_f_shifted = np.zeros_like(s1_f)
    for i in range(len(bins)):
        s1_f_shifted[i] = s1_f[i] * np.exp(-1j*2*np.pi*bins[i]*tau)
    rcv_matrix[n] = ifft(s1_f_shifted)
    #plt.plot(t,rcv_matrix[n])

#let's get noisy!!!!
for n in range(0,7):
    rcv_matrix[n] += np.random.normal(0,0.1,N)

#beamforming time!
#define azimuth range
min_az = -90
max_az = 90
az_fidelity = 1
az_matrix = np.arange(min_az,max_az + az_fidelity,az_fidelity)

#output_matrix = np.zeros((len(az_matrix),int(N/2))).astype(complex)
output_matrix = []
beam_power = []

#for each azimuth
for az_i in range(len(az_matrix)):
    #print("checking azimuth: ",az_matrix[az_i],"\n")
    #form beam
    bins = fftfreq(N, T)[0:N//2]
    time_data = np.zeros_like(rcv_matrix[0]).astype(complex)
    for num in range(0,7):
        tau_d = (num*el_space*np.sin((az_matrix[az_i]*np.pi)/180))/sound_velocity
        freq_data = fft(rcv_matrix[num])
        freq_data_shifted = np.zeros_like(freq_data)
        for i in range(len(bins)):
            freq_data_shifted[i] = freq_data[i] * np.exp(1j*2*np.pi*bins[i]*tau_d)
        #output_matrix[az_i] += freq_data_shifted[0:N//2]
        time_data += ifft(freq_data_shifted)
    
    power = np.var(time_data)
    #plot beam
    #plt.plot(bins,output_matrix[az_i])
    #plt.show
    #beam power:
    #power = np.sum(output_matrix[az_i]**2)/len(output_matrix[az_i])
    beam_power.append(power)

beam_power = np.array(beam_power)
beam_power /= np.max(beam_power)
plt.plot(az_matrix,10*np.log10(beam_power))
plt.show()

    

#plt.show()


# s = s1+s2 #combine signals (thanks superposition)

# sf = fft(s)
# xf = fftfreq(N, T)[0:N//2] #args: (windowlength, sample spacing) || [0:N//2] truncates negative frequencies
# sf = 2/N * np.abs(sf[0:N//2]) # take abs and normalize
# pf = np.angle(sf)

# fig, plots = plt.subplots(1,2)
# plots[0].plot(xf, sf)

# plots[1].plot(xf, pf)

# plt.show()