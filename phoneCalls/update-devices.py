import pyaudio
import json
import os
import re

ENV_PATH = ".env"

def find_device_idx(audio, name, exact_inputs=None, exact_outputs=None):
    for i in range(audio.get_device_count()):
        dev = audio.get_device_info_by_index(i)
        if name not in dev['name']:
            continue
        if exact_inputs is not None and dev['maxInputChannels'] != exact_inputs:
            continue
        if exact_outputs is not None and dev['maxOutputChannels'] != exact_outputs:
            continue
        return i
    return None

def update_env_var(var, value, env_path=ENV_PATH):
    with open(env_path, "r") as f:
        lines = f.readlines()
    pattern = re.compile(rf"^{var}\s*=\s*.*$", re.IGNORECASE)
    found = False
    for i, line in enumerate(lines):
        if pattern.match(line):
            lines[i] = f"{var} = {value}\n"
            found = True
            break
    if not found:
        lines.append(f"{var} = {value}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)

def main():
    audio = pyaudio.PyAudio()
    print("Detected devices:")
    for i in range(audio.get_device_count()):
        dev = audio.get_device_info_by_index(i)
        print(json.dumps(dev, indent=2))

    mic_idx = find_device_idx(audio, "SoundForm Adapt", exact_inputs=1)
    headphone_idx = find_device_idx(audio, "SoundForm Adapt", exact_outputs=2)
    ocean_idx = find_device_idx(audio, "UltraLite-mk5")
    all_idx = find_device_idx(audio, "M133Q01", exact_outputs=2)

    print(f"\nSelected indices:\nMIC_DEVICE: {mic_idx}\nHEADPHONE_DEVICE: {headphone_idx}\nOCEAN_DEVICE: {ocean_idx}\nALL_DEVICE: {all_idx}")

    update_env_var("MIC_DEVICE", mic_idx)
    update_env_var("HEADPHONE_DEVICE", headphone_idx)
    update_env_var("OCEAN_DEVICE", ocean_idx)
    update_env_var("ALL_DEVICE", all_idx)

    print("\n.env updated.")
    audio.terminate()

if __name__ == "__main__":
    main()

try:
    audio = pyaudio.PyAudio()
    stream = audio.open(format              = pyaudio.paInt16,
                        channels            = 1,
                        rate                = 48000,
                        input               = True,
                        output              = True,
                        input_device_index  = 1,
                        output_device_index = 2,
                        frames_per_buffer   = 1024)
    frames = []
    print("* echoing")
    print("Press CTRL+C to stop")
    while True:
        data = stream.read(1024)
        frames.append(data)
        if len(frames)>0:
            stream.write(frames.pop(0),1024)
    print("* done echoing")
except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    audio.terminate()