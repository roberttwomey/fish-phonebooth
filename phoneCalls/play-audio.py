"""PyAudio Example: Play a wave file (callback version)."""
import wave
import time
import sys
from datetime import datetime

import pyaudio

# OCEAN INPUT
oceanfile = "media/day2_lower.wav"
speechfile = "media/day2_vocal.wav"
audiencefile = "media/day2_All.wav"

# MIC RECORDING
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 48000  # Record at 44100 samples per second
seconds = 3
# filename = "output.wav"

microphone_device = 2
headphone_device = 3
motu_device = 1
screen_device = 0

def stop():
    return

try: 

    with wave.open(oceanfile, 'rb') as wf:
        # Define callback for playback (1)

        with wave.open(speechfile, 'rb') as wf2:

            with wave.open(audiencefile, 'rb') as wf3:

                def callback(in_data, frame_count, time_info, status):
                    if not wf._i_opened_the_file:
                        return (None, pyaudio.paContinue)
                    
                    data = wf.readframes(frame_count)
                    # If len(data) is less than requested frame_count, PyAudio automatically
                    # assumes the stream is finished, and the stream stops.
                    return (data, pyaudio.paContinue)

                def callback2(in_data, frame_count, time_info, status):
                    if not wf2._i_opened_the_file:
                        return ( None, pyaudio.paContinue)
                    
                    data = wf2.readframes(frame_count)
                    # If len(data) is less than requested frame_count, PyAudio automatically
                    # assumes the stream is finished, and the stream stops.
                    return (data, pyaudio.paContinue)
                
                def callback3(in_data, frame_count, time_info, status):
                    if not wf3._i_opened_the_file:
                        return ( None, pyaudio.paContinue)
                    
                    data = wf3.readframes(frame_count)
                    # If len(data) is less than requested frame_count, PyAudio automatically
                    # assumes the stream is finished, and the stream stops.
                    return (data, pyaudio.paContinue)
                
                # Instantiate PyAudio and initialize PortAudio system resources (2)
                p = pyaudio.PyAudio()

                # Open stream using callback (3)
                oceanstream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output_device_index=motu_device,
                                output=True,
                                stream_callback=callback)
                
                # Open stream using callback (3)
                speechstream = p.open(format=p.get_format_from_width(wf2.getsampwidth()),
                                channels=wf2.getnchannels(),
                                rate=wf2.getframerate(),
                                output_device_index=headphone_device,
                                output=True,
                                stream_callback=callback2)

                # Open stream using callback (3)
                audiencestream = p.open(format=p.get_format_from_width(wf3.getsampwidth()),
                                channels=wf3.getnchannels(),
                                rate=wf3.getframerate(),
                                output_device_index=screen_device,
                                output=True,
                                stream_callback=callback3)

                print('Recording')

                micstream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input_device_index=microphone_device,
                    input=True)

                frames = []  # Initialize array to store frames

                # Wait for stream to finish (4)
                while oceanstream.is_active() and speechstream.is_active():
                    # Store data in chunks for 3 seconds
                    # for i in range(0, int(fs / chunk * seconds)):
                    #     data = micstream.read(chunk)
                    #     frames.append(data)
                    data = micstream.read(chunk)
                    frames.append(data)            

except (KeyboardInterrupt):
    print("exiting...")
    pass



# Close the stream (5)
if wf._i_opened_the_file:
    oceanstream.close()

if wf2._i_opened_the_file:
    speechstream.close()

if wf3._i_opened_the_file:
    audiencestream.close()

# Stop and close the stream
micstream.stop_stream()
micstream.close()

# Release PortAudio system resources (6)
p.terminate()

print('Finished recording')

# Save the recorded data as a WAV file
current_timestamp = datetime.now()
formatted_timestamp = current_timestamp.strftime('%Y%m%d-%H%M%S')
filename = f"recordings/{formatted_timestamp}-mic.wav"

wf3 = wave.open(filename, 'wb')
wf3.setnchannels(channels)
wf3.setsampwidth(p.get_sample_size(sample_format))
wf3.setframerate(fs)
wf3.writeframes(b''.join(frames))
wf3.close()

print(f"wrote {filename} to disk")