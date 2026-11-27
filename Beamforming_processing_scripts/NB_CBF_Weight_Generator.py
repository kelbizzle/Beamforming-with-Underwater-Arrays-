import numpy as np

#Environmental parameters
temp = 12 #water temp. in celsius
depth = 1/.016 #assuming pressure is negligible for application, setting to reciporical of weight
salinity = 0.0005 #set to .05%, max salinity for freshwater
#approximation for sound velocity in m/s based on environmental parameters
#sound_velocity = 1449.2 + 4.6*temp - (0.055* temp)**2 + (0.00029 * temp)**3 + (1.34- 0.01 * temp) * (salinity-35) + 0.016*depth


sound_velocity = 1500 #simple c assumption
#RCV Arry parameters
el_space = .298
num_els = 8

#narrowband frequency of interest
f_of_interest = 2400 # beam pattern changes with frequency

#method that builds a num_els row matrix of weights for the chosen angle
def build_weights(angle,freq,num_els,el_spacing,c):
    weights = np.zeros(num_els, dtype=complex)
    for elem in range(num_els):
        tau_d = (elem*el_spacing*np.cos(((180-angle)*np.pi)/180))/c
        weights[elem] = np.exp(1j*2*np.pi*freq*tau_d)
    return weights

#define angle to steer to and angles to null
steering_angle =90
null_angles = ([45])

# steering weights
steer_weights=build_weights(steering_angle,f_of_interest,num_els,el_space,sound_velocity)

# nulling weights
#build matrix with a column for each null angle
null_matrix = np.zeros((num_els,len(null_angles)), dtype=complex)
#build the individual null weight vectors
for null in range(len(null_angles)):
    null_matrix[:,null]=build_weights(null_angles[null],f_of_interest,num_els,el_space,sound_velocity)


#combine nulls with steering vector:
#identity matrix, num_els x num_els:
iden = np.eye(num_els)
#interferer matrix, beams steered towards null angles
interferers = null_matrix @ np.linalg.pinv(null_matrix)
#combine matrecies, subtract interferers from identity matrix to make them nulls instead of beams
comb_matrix = (iden - interferers)@steer_weights;

print(*null_matrix, sep=",\n")