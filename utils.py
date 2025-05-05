import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller EXE """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_appdata_folder():
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
    else:
        appdata = os.path.expanduser("~/.config")
    app_folder = os.path.join(appdata, "MoonTTS")
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)
    return app_folder

def get_audio_devices():
    import sounddevice as sd
    devices = sd.query_devices()
    output_devices = []
    device_indices = {}
    seen_device_keys = {}
    for idx, device in enumerate(devices):
        if device['max_output_channels'] > 0 and device['hostapi'] == 1:
            original_name = device['name'].strip()
            clean_key = original_name.lower()
            if clean_key not in seen_device_keys:
                output_devices.append(original_name)
                device_indices[original_name] = idx
                seen_device_keys[clean_key] = idx
    output_devices.sort()
    return output_devices, device_indices