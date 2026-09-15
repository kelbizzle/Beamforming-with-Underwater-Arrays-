clear all 
clc
close all

%% Array testing file
% File records and saves data from 8 channels. File computes live FFT for
% channel four in first part (doing all seemed to be too costly).
% Part two plots spectrograms of all channels and the k omega plot.

% current naming convention for files appends the date & time to each
% channel.


%% First section --> recording data


%important variables --> used thorughout file
fs = 44100;  % Sampling rate (Hz) -- match with TASCAM
frameSize = 512; % used in part 1
nfft = 2048;  % FFT points, used in part 1
nt = 512; % samples per time block
ns = 256; % sensor samples
d = 0.30; % distance between hydrophones
c = 1496.8; % speed of sound in chlorinated water (approximate)

%% function for computing 2d FFT--> used in part two
% function matrix = compute_2d_fft(x)
%     nt = 1024;  % samples per time block
%     ns = 256;   % number of sensors samples
% 
%    % total number of time samples
%     total_samples = size(x, 1);
% 
%     % Calculate number of complete non-overlapping blocks
%     num_blocks = floor(total_samples / nt);
% 
%     % add values for averaged power spectrum
%     p_accum = zeros(ns, nt); 
% 
%     for b = 1:num_blocks
%         % Extract current block
%         start_idx = (b - 1) * nt + 1;
%         end_idx = b * nt;
%         x_block = x(start_idx:end_idx, :);  % [nt x ns]
% 
%         % 2D FFT
%         first_fft = fftshift(fft(x_block, nt, 1),1); % FFT over time --> only use fftshift if you want both pos and negative frequencies
%         second_fft = fftshift(fft(first_fft, ns, 2), 2);  % FFT over sensors
%         p_block = abs(second_fft).^2;  % Power spectrum
%         p_accum = p_accum + p_block.';  % Transpose and accumulate
%     end
% 
%     % Average across blocks
%     matrix = 10*log10(p_accum/num_blocks);
% end


tmstmp= string(datetime('now'));

name1 = strcat(tmstmp, 'ch1.wav'); % add time for each data set to name
name2 = strcat(tmstmp, 'ch2.wav');
name3 = strcat(tmstmp, 'ch3.wav');
name4 = strcat(tmstmp, 'ch4.wav');
name5 = strcat(tmstmp, 'ch5.wav');
name6 = strcat(tmstmp, 'ch6.wav');
name7 = strcat(tmstmp, 'ch7.wav');
name8 = strcat(tmstmp, 'ch8.wav');

%% Capture from eight channels
mic = audioDeviceReader('Device', 'US-16x08',...
    'ChannelMappingSource', 'Property', 'ChannelMapping', [1, 2, 3, 4, 5, 6, 7, 8], ...
    'SampleRate', fs, 'SamplesPerFrame', frameSize);


% Writers for each channel
audioWriter1 = dsp.AudioFileWriter(name1, 'SampleRate', fs);
audioWriter2 = dsp.AudioFileWriter(name2, 'SampleRate', fs);
audioWriter3 = dsp.AudioFileWriter(name3, 'SampleRate', fs);
audioWriter4 = dsp.AudioFileWriter(name4, 'SampleRate', fs);
audioWriter5 = dsp.AudioFileWriter(name5, 'SampleRate', fs);
audioWriter6 = dsp.AudioFileWriter(name6, 'SampleRate', fs);
audioWriter7 = dsp.AudioFileWriter(name7, 'SampleRate', fs);
audioWriter8 = dsp.AudioFileWriter(name8, 'SampleRate', fs);

% Real-time FFT Display for channel 4
% when calling for only one channel: scope(audioFrame(:, 4)); --> Only sends channel 4 to the scope
scope = spectrumAnalyzer('ViewType','spectrum',...
    'SampleRate', fs, 'FFTLength', nfft,... 
    'PlotAsTwoSidedSpectrum', false, 'FrequencyScale','log',...
    'Title', 'Channel one only', 'ShowLegend',true,... 
    'ChannelNames', {'Ch1'}, 'YLimits', [-60, 60]);

% Initialize storage
storedFFT1 = []; storedFFT2 = [];
storedFFT3 = []; storedFFT4 = [];
storedFFT5 = []; storedFFT6 = [];
storedFFT7 = []; storedFFT8 = [];

timeStamps = [];
recordedAudio1 = []; recordedAudio2 = []; 
recordedAudio3 = []; recordedAudio4 = [];
recordedAudio5 = []; recordedAudio6 = [];
recordedAudio7 = []; recordedAudio8 = [];

freqAxis = linspace(0, fs/2, nfft/2); % Frequency axis

disp('Recording... Press Ctrl+C to stop.');

%% Store + FFts
tic;
fixedDur= 15;
while toc<fixedDur
    audioFrame = mic(); % Capture input
    scope(audioFrame(:, 1)); % Display channel 1 on real time plot

    channel1 = audioFrame(:,1); % Extract Channel 1
    channel2 = audioFrame(:,2); % Extract Channel 2
    channel3 = audioFrame(:,3); % Extract Channel 3
    channel4 = audioFrame(:,4); % Extract Channel 4
    channel5 = audioFrame(:,5); % Extract Channel 1
    channel6 = audioFrame(:,6); % Extract Channel 2
    channel7 = audioFrame(:,7); % Extract Channel 3
    channel8 = audioFrame(:,8); % Extract Channel 4


    % Store audio data
    recordedAudio1 = [recordedAudio1; channel1];
    recordedAudio2 = [recordedAudio2; channel2];
    recordedAudio3 = [recordedAudio3; channel3];
    recordedAudio4 = [recordedAudio4; channel4];
    recordedAudio5 = [recordedAudio5; channel5];
    recordedAudio6 = [recordedAudio6; channel6];
    recordedAudio7 = [recordedAudio7; channel7];
    recordedAudio8 = [recordedAudio8; channel8];

    % Audiowriter for each channel
    audioWriter1(channel1);
    audioWriter2(channel2);
    audioWriter3(channel3);
    audioWriter4(channel4);
    audioWriter5(channel5);
    audioWriter6(channel6);
    audioWriter7(channel7);
    audioWriter8(channel8);

    % Compute FFT
    % Ch1
    windowedFrame1 = channel1 .* hamming(frameSize);
    fftData1 = fft(windowedFrame1, nfft);
    magnitude1 = 20*log10(abs(fftData1(1:nfft/2))); % Convert to dB
    
    % Ch2
    windowedFrame2 = channel2 .* hamming(frameSize);
    fftData2 = fft(windowedFrame2, nfft);
    magnitude2 = 20*log10(abs(fftData2(1:nfft/2))); % Convert to dB

    %Ch3
    windowedFrame3 = channel3 .* hamming(frameSize);
    fftData3 = fft(windowedFrame3, nfft);
    magnitude3 = 20*log10(abs(fftData3(1:nfft/2))); % Convert to dB

    %Ch4
    windowedFrame4 = channel4 .* hamming(frameSize);
    fftData4 = fft(windowedFrame4, nfft);
    magnitude4 = 20*log10(abs(fftData4(1:nfft/2))); % Convert to dB

    %Ch5
    windowedFrame5 = channel5 .* hamming(frameSize);
    fftData5 = fft(windowedFrame5, nfft);
    magnitude5 = 20*log10(abs(fftData5(1:nfft/2))); % Convert to dB

    %Ch6
    windowedFrame6 = channel6 .* hamming(frameSize);
    fftData6 = fft(windowedFrame6, nfft);
    magnitude6 = 20*log10(abs(fftData6(1:nfft/2))); % Convert to dB

    %Ch7
    windowedFrame7 = channel7 .* hamming(frameSize);
    fftData7 = fft(windowedFrame7, nfft);
    magnitude7 = 20*log10(abs(fftData7(1:nfft/2))); % Convert to dB

    %Ch8
    windowedFrame8 = channel8 .* hamming(frameSize);
    fftData8 = fft(windowedFrame8, nfft);
    magnitude8 = 20*log10(abs(fftData8(1:nfft/2))); % Convert to dB


    % Store FFT data
    storedFFT1 = [storedFFT1, magnitude1];
    storedFFT2 = [storedFFT2, magnitude2];
    storedFFT3 = [storedFFT3, magnitude3];
    storedFFT4 = [storedFFT4, magnitude4];
    storedFFT5 = [storedFFT5, magnitude5];
    storedFFT6 = [storedFFT6, magnitude6];
    storedFFT7 = [storedFFT7, magnitude7];
    storedFFT8 = [storedFFT8, magnitude8];

    %Store time data
    
    timeStamps = [timeStamps, toc];
end

ffts = {storedFFT1, storedFFT2, storedFFT3, storedFFT4, storedFFT5, storedFFT6, storedFFT7, storedFFT8};

%% Second section --> saving an plotting data

% Release audio writers
release(audioWriter1);
release(audioWriter2);
release(audioWriter3);
release(audioWriter4);
release(audioWriter5);
release(audioWriter6);
release(audioWriter7);
release(audioWriter8);

% Save recorded audio as WAV
audiowrite(name1, recordedAudio1, fs);
audiowrite(name2, recordedAudio2, fs);
audiowrite(name3, recordedAudio3, fs);
audiowrite(name4, recordedAudio4, fs); 
audiowrite(name5, recordedAudio5, fs);
audiowrite(name6, recordedAudio6, fs);
audiowrite(name7, recordedAudio7, fs);
audiowrite(name8, recordedAudio8, fs);

%% Spectrograms

% File names for each channel
names = {name1, name2, name3, name4, name5, name6, name7, name8};

for ch = 1:8
    figure;

    imagesc(timeStamps, freqAxis/1000, ...
        ffts{ch} - max(ffts{ch}, [], 'all'));

    axis xy;
    colorbar;
    clim([-40 0]);
    ylim([0 20]);
    xlabel('Time (s)');
    ylabel('Frequency (kHz)');
    title(sprintf('Spectrogram of Channel %d', ch));

    saveas(gcf, sprintf('spec_%s.png', names{ch}));
end
