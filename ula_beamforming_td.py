# -----------------------------------------------------------------------------------------------------
# *** Beamforming Code for Time Domain Processing ***
# * ULA geometry places N sensors equal distances apart along straight line
# * To prevent spatial aliasing d <= lambda_min / 2
# * When a wavefront hits the array at an angle, each sensor receives it at sligtly different times
#      * This time delay can be accounted for and adjusted to enable constructive interfernece 
#        through the use of beamforming! 
# ------------------------------------------------------------------------------------------------------
# * Description of Assumptions for Processing:

# * ULA arrangement: left endfire = 0 deg, broadside = 90 deg, and right endfire = 180 deg
# * Advancement in time equates to a negative shift value in samples 

# * Delay (in time) = dist_between_sensors*cos(theta_rad)/speed_sound 
# --> using cosine assumes horizontal azimuth convention; cos(90 degrees) = 0 ==> zero delay for broadside
# * Delays: H1 = 0, H2 = dt, H3 = 2dt, H4 = 3dt, ...
# * Shift later sensors by sample amounts to build constructive interference for particular angle
# * Subtraction = advancement in time

# Example:
# [1,2,3,4,5, 0,0,0,0,0] delay in time by 3 (advance) samples --> [0,0,0,1,2,3,4,5,0,0] --> positive shift
# [0,0,0,1,2,3] delay in time by -3 samples --> [1,2,3,0,0,0] --> negative shift
# what about fractional delays ?? How best to implment ??
#  ---> Maybe: interpolation, lagrange methods (to be continued)

# * Speed of sound underwater: approximated as 1500 m/s
# * Inter element spacing approximated as d = 0.3 m, approx. 11.75 inches

# * For TD processing, integer sample shifts are used. This means not all indiviudal angles can be resolved
#   - For Fs = 44.1 kHz and d = 0.3 m, each integer sample value corresponds to an approx. range of 9 degrees.
#   - Thus there is limited frequency resolution.
#   - To change this you would have to increase distance between sensors (but watch out for spatial aliasing!)
#       --> Larger aperature length creates narrower main lobes.
#   - Or increase sampling rate to decrease the range of degrees associated with each integer sample value.

# imports
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from tqdm import tqdm # used to show progress bar in terminal while script is running

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
fs, x_data = assemble_data_matrix(8,"path_to_file_name")

# *** Time Domain Beamforming ***
def apply_time_shifts(x_data, integer_shifts):
    '''
    Function purpose: apply time delay shifts to each sensor of data according to scanned angle

    Inputs: 
            name: dataype, description
            xdata: np.ndarray, matrix of data from sensors xdata.shape(sensors,samples)
            integer_shifts: int, sample amount computed by rounding sample shift values
    Outputs:
            name: datatype, description
            shifted_data: np.array, shifted data of same shape as x_data

    '''
    shifted_data = np.zeros_like(x_data)
    for i,shift in enumerate(integer_shifts):
        if shift > 0: # advance samples in time (earliest signal from right)
            shifted_data[i][shift:] = x_data[i][:-shift]
        elif shift < 0: # delay samples in time (earliest signal from left)
            shifted_data[i][:shift] = x_data[i][-shift:]
        else: # no delay (broadside)
            shifted_data[i][:] = x_data[i]
    return shifted_data

c = 1500 # m/sec

# angles to scan
degree_angles2scan = np.arange(0,180,5)
rad_angles2scan = np.deg2rad(degree_angles2scan)

d = 0.3 # meters --> fmax = 2.5 kHz
hydro_locations = np.arange(8)*d # 8 sensors uniformly spaced 
rms_results = {}

for angle in tqdm(rad_angles2scan, desc="Scanning Angles", unit="angle"):
    arrival_delays = hydro_locations*np.cos(angle)/c # in seconds
    earliest_delays = np.min(arrival_delays)
   
    # Compensation = how much later in time each signal arrived compared to the earliest sensor
    # --> need to advance each signal by the respective amount
    compensation_delays = arrival_delays - earliest_delays
    #print("angle:", np.rad2deg(angle), "delays:", compensation_delays)

    delay_samples = (-1*compensation_delays)*fs # delays in terms of samples, advances signals in time (negative), (sensor 8 receives wavefront last)
    integer_shifts = np.round(delay_samples).astype(int) # integer shifts means frequency resolution between angles diminishes

    delayed_hydro_data = apply_time_shifts(x_data, integer_shifts)
    summed_coherence = np.sum(delayed_hydro_data, axis=0) # collapses rows and adds sample value at each location from all columns of data
    #print('summed: ', type(summed_coherence))
    
    # roots mean square (RMS) power calculates the average signal energy 
    # the angle that produces the largest RMS output = source location
    rms_val = np.sqrt(np.mean(summed_coherence**2))
    rms_results[np.rad2deg(angle)] = rms_val

def write_beamformed__audio(summed_coherence, angle, fs):
    '''
    Function purpose: write out beamformed data as .wav file. Would be helpful for data w/ interferers.

    Inputs:
            name: datatype, description
            summed_coherence: 1d array, beamformed data matrix
            angle: radian, value for desired scanned angle
            fs: float, sampling rate
    Outputs:
            name: datatype, description
            no return value, writes file directly to current working directory
    '''
    file_name = "beamformed_data_" + str(np.rad2deg(angle) + ".wav")
    wavfile.write(file_name, fs, summed_coherence.astype(np.float32))
    
# Creating plot to show various RMS power values per angle scanned
angles = list(rms_results.keys())
power = list(rms_results.values())

plt.figure(figsize=(10, 6))
plt.plot(angles, power, color='m', linewidth=2, label="Beamforming Output")

true_angle = 130
resolution_half_width = 9

# Laytex hack for showing stacked + and - is $\pm$
# For degree symbol: ^\circ$C or \degree (must be r string if not using f strings) or pass in unicode: \u00B0
plt.axvline( # add vertical line through "true" expected angle
    x=true_angle,
    color='b',
    linestyle='--',
    label=f'True Source ({true_angle}\u00B0)',
)
plt.axvspan( # adds a rectangular spanning line over region of angle resolution ambiguity 
    true_angle - resolution_half_width,
    true_angle + resolution_half_width,
    color='blue',
    alpha=0.3,
    label='Array Resolution Window ($\pm 9^\circ$)',
)
plt.xlabel("Scan Angle (degrees)")
plt.ylabel("RMS Power")
plt.title("Beamformer Scan: RMS Power vs. Angle")
plt.grid(True)
plt.legend()
plt.show()
