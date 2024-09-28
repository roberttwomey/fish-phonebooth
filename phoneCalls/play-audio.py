"""PyAudio Example: Play a wave file (callback version)."""
import wave
import time
import sys
from datetime import datetime
import pyaudio
import os
from dotenv import load_dotenv

# load variables from .env file: 
load_dotenv()

# OCEAN INPUT
oceanfile = "media/day2_lower_16.wav"
speechfile = "media/day2_vocal_16.wav"
audiencefile = "media/day2_all_16.wav"

# MIC RECORDING
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 48000  # Record at 44100 samples per second
seconds = 3
# filename = "output.wav"

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
MIC_DEVICE = int(os.getenv('MIC_DEVICE'))
HEADPHONE_DEVICE = int(os.getenv('HEADPHONE_DEVICE'))
OCEAN_DEVICE = int(os.getenv('OCEAN_DEVICE'))
ALL_DEVICE = int(os.getenv('ALL_DEVICE'))

# MIC_DEVICE = 2#2#1
# HEADPHONE_DEVICE = 3#2
# OCEAN_DEVICE = 1
# screen_device = 0#3

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
                                output_device_index=OCEAN_DEVICE,
                                output=True,
                                stream_callback=callback)
                
                # Open stream using callback (3)
                speechstream = p.open(format=p.get_format_from_width(wf2.getsampwidth()),
                                channels=wf2.getnchannels(),
                                rate=wf2.getframerate(),
                                output_device_index=HEADPHONE_DEVICE,
                                output=True,
                                stream_callback=callback2)

                if ALL_DEVICE > 1:
                    # Open stream using callback (3)
                    audiencestream = p.open(format=p.get_format_from_width(wf3.getsampwidth()),
                                    channels=wf3.getnchannels(),
                                    rate=wf3.getframerate(),
                                    output_device_index=ALL_DEVICE,
                                    output=True,
                                    stream_callback=callback3)

                print('Recording')

                micstream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input_device_index=MIC_DEVICE,
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

if ALL_DEVICE > 0:
    if wf3._i_opened_the_file:
        audiencestream.close()

# Stop and close the stream
micstream.stop_stream()
micstream.close()

# Release PortAudio system resources (6)
p.terminate()

print('Finished recording')

print('Writing to disk...')
sys.stdout.flush()
# Save the recorded data as a WAV file
current_timestamp = datetime.now()
formatted_timestamp = current_timestamp.strftime('%Y%m%d-%H%M%S')
filename = f"recordings/{formatted_timestamp}-mic.wav"

wf4 = wave.open(filename, 'wb')
wf4.setnchannels(channels)
wf4.setsampwidth(p.get_sample_size(sample_format))
wf4.setframerate(fs)
wf4.writeframes(b''.join(frames))
wf4.close()

print(f"wrote {filename} to disk")