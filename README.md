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
CAM1 = "rtsp://admin:CameraRed@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"
VIDEO_FILE = "/Volumes/Work/Projects/housemachine/data/ceiling/livingroom/livingroom_motion_2017-08-13_20.17.02_27.mp4"
NETWORK_CAMERA = "rtsp://admin:CameraRed@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"
DEBUG_ARDUINO = False
DEBUG_PHONECALL = False
DEBUG_AUDIO = False
DEBUG_LIGHTS = False
DEBUG_STORAGE = False
```