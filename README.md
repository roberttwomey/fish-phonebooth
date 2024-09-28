# fish-phonebooth
Code for WOW 2024 Project

# Install

some of these 
```zsh
conda create -n fishphone python
conda activate fishphone
brew install portaudio
pip install pyaudio soundfile twilio pyserial pyautogui python-dotenv pygame numpy opencv-python
```

if that won't install, add `--break-system-packages`.

Create an automator application and save it on the desktop as **Run Fish Phonebooth**: 
```zsh
cd ~/fish-phonebooth/phoneCalls
conda activate fishphone
/opt/homebrew/opt/python@3.12/libexec/bin/python runFishPhoneBooth.py
```

Add this to login items (System Settings -> General -> Login Items)

on mac m3
```zsh
cd ~/Desktop/fish-phonebooth/phoneCalls
conda activate fishphone
/opt/homebrew/anaconda3/envs/fishphone/bin/python runFishPhoneBooth.py
```

## Env file info

add twilio

also...

```bash
TWILIO_ACCOUNT_SID="put yours here"
TWILIO_AUTH_TOKEN="put yours here"
TWILIO_PHONE="put yours here"

USB_ONAIR="usb port for on air and door switch arduino"
USB_KEYPAD="usb port for screen arduino"

CAM1 = "/Volumes/Work/Projects/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-13_20.17.02_27.mp4"
VIDEO_FILE = "/Volumes/Work/Projects/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-13_20.17.02_27.mp4"
NETWORK_CAMERA = "rtsp://admin:YOUR-PASSWORD@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"

DEBUG_ARDUINO = True
DEBUG_PHONECALL = True
DEBUG_AUDIO = False
DEBUG_LIGHTS = True
DEBUG_STORAGE = True

MIC_DEVICE = 0
HEADPHONE_DEVICE = 1
OCEAN_DEVICE = 3
ALL_DEVICE = -1

FIRST_CALL_DELAY = 191#181 # first phone call delay in seconds
END_CALL_DELAY =  650#401 # end phone call delay in seconds
```

## Leftovers

from the old phoneCalls readme.md

```zsh
brew install portaudio
cd Desktop/fish-phonebooth
conda create -n fishphone python
conda activate fishphone
pip install pyaudio soundfile twilio pyserial pyautogui
```
