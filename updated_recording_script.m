% Updated Script for Hydrophone Reception using Tascam Device 
% Script records for specified amount and loops on 5 minute increments
% The script saves separate .wav files for each hydrophone in a directory
% based on the time stamp

clear all 
clc
close all

fs = 44100;  % Sampling rate (Hz) -- match with TASCAM
frame_size = 2048; % larger frame size means fewer updates, more efficient T = framesize/fs
record_dur = 60; % 1 minute recording
cycle_dur = 300; % 5 minute cycle 
num_channels = 8; % 8 total sensors

window_size = 4096; % window_size/fs = T length
overlap = 3072; % 75 % overlap
nfft = 4096; % frequency spacing = fs/4096 = 10.7 Hz

%larger freq window ==> better for freq resolution, worse time resolution
%hop size = window size - overlap
main_folder = 'Hydrophone_Recordings_River_Testing_11-21-26'; % adjust to reflect actual testing date


% create directory for main folder if it doesnt exist
if ~exist(main_folder, 'dir')
    mkdir(main_folder);
end

% establishing setteings for device matching through USB connection
mic = audioDeviceReader('Device', 'US-16x08',...
    'ChannelMappingSource', 'Property', 'ChannelMapping', 1:num_channels, ...
    'SampleRate', fs, 'SamplesPerFrame', frame_size);

disp('Recording... Press Ctrl+C to stop.');



% Real-time FFT Display for channel 1 --> displaying mutliple channels at
% once seemed to cause significant lag
scope = spectrumAnalyzer('ViewType','spectrum',...
    'SampleRate', fs, 'FFTLength', nfft,...
    'PlotAsTwoSidedSpectrum', false, 'FrequencyScale','log',...
    'Title', 'Channel one only', 'ShowLegend',true,...
    'ChannelNames', {'Ch1'}, 'YLimits', [-60, 60]);

% Release audio reader if script exits or is interrupted
cleanupObj = onCleanup(@() release(mic));


while true

    % Start timing the 5 minute cycle
    cycle_start = tic;

    % Generate timestamp for this recording
    recording_session = datetime('now', ...
        'Format', 'yyyy-MM-dd_HHmmss');

    time_stamp = char(recording_session);

    fprintf('\nRecording session: %s\n', time_stamp);

    % Memory for 90 seconds of audio
    target_samples = round(record_dur * fs);

    recorded_audio = zeros(target_samples, num_channels);

    samples_captured = 0;

    recording_clock = tic; % separate clock for recording segment 

   % Record data from all eight sensors at once
    while samples_captured < target_samples

        % read the next frame from all eight channels
        audioFrame = mic();

        % update spectrum analyzer (channel 1)
        scope(audioFrame(:,1));

        % determine how many samples are still needed
        samples_copy = min(size(audioFrame, 1), target_samples - samples_captured);

        % store all eight channels simultaneously
        sample_indices = samples_captured + (1:samples_copy);

        recorded_audio(sample_indices, :) = audioFrame(1:samples_copy, :);

        samples_captured = samples_captured + samples_copy;

    end

    recording_elapsed = toc(recording_clock);

    fprintf('Recording complete. Elapsed time: %.2f seconds\n', ...
        recording_elapsed);


    % creates folder for each recording processed 
    session_folder = fullfile(main_folder, time_stamp);
    mkdir(session_folder);


    % separates each channel of data into a separate wav file
    for ch = 1:num_channels

        wav_name = sprintf('Ch%d.wav', ch);

        wav_path = fullfile(session_folder, wav_name);

        audiowrite(wav_path, recorded_audio(:, ch), fs);

    end

    fprintf('WAV files saved.\n');

% after running this there did appear to be anerror with how the time stamp
% was oriented but it is unclear why the formating is messed up

    fig = figure('Name', ['Hydrophone Spectrograms - ' time_stamp]); 

   % tiledlayout(num_rows, num_cols) --> compact helps lessen space between
   % plots and outer edges
    tiledlayout(2, 4,'TileSpacing', 'compact','Padding', 'compact');

    window = hann(window_size, 'periodic');

    % create a spectrigram of each channel of data and store all in a
    % subplot 
    for ch = 1:num_channels

        channel_data = recorded_audio(:, ch);

        [S, F, T] = spectrogram(channel_data, window, overlap, nfft, fs);

        magnitudeDB = 20 * log10(abs(S) + eps); % adding eps prevents any division by zero errors 

        magnitudeDB = magnitudeDB - max(magnitudeDB(:));

        nexttile;

        imagesc(T, F/1000, magnitudeDB);

        axis xy;

        ylim([0 10]);
        clim([-100 0]);
        colorbar;

        xlabel('Time (s)');
        ylabel('Frequency (kHz)');
% individual title for each spectrogram 
        title(sprintf('Hydrophone %d', ch)); % sprintf creates a formatted character string 

    end

    sgtitle(['Recording: ' time_stamp]); % creates a super title for entire figure 

    % save complete figure by establishing a pathname 
    plot_path = fullfile(session_folder, 'Spectrograms.png');

    % export png image of subplot 
    exportgraphics(fig, plot_path, 'Resolution', 200);

    fprintf('Spectrogram saved.\n');

    close(fig);



    elapsed_cycle = toc(cycle_start);

    remaining_time = cycle_dur - elapsed_cycle;

    if remaining_time > 0

        fprintf('Next recording in %.1f minutes.\n', ...
            remaining_time / 60);

        pause(remaining_time);

    else

        warning('Recording overrun 5 minute cycle. Starting next session instead.');

    end

end
