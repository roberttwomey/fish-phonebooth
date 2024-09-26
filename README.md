# fish-phonebooth
Code for WOW 2024 Project

# Install

some of these 
```zsh
conda create -n fishphone python
conda activate fishphone
brew install portaudio
pip install pyaudio soundfile twilio pyserial pyautogui python-dotenv pygame numpy
```

if that won't install, add `--break-system-packages`.

Create an automator application and save it on the desktop: 
```zsh
cd ~/fish-phonebooth/phoneCalls
conda activate fishphone
/opt/homebrew/opt/python@3.12/libexec/bin/python runFishPhoneBooth.py
```