# --- Imports ---
import os
import json
import threading
import shutil
import sys
from PIL import Image
from datetime import datetime
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sounddevice as sd
import soundfile as sf
from google.cloud import texttospeech

# Interface

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller EXE """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

root = ctk.CTk(fg_color='#E1DEE8')
root.title("Moon TTS")
root.geometry("400x535")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.resizable(False, False)
root.iconbitmap(resource_path("icon.ico"))

frame_1 = ctk.CTkFrame(root, width=400, height=550)
frame_1.configure(fg_color='#E1DEE8')
frame_1.grid(sticky="nswe")
frame_1.grid_columnconfigure((0, 1), weight=1)
frame_1.grid_propagate(0)

# --- Usage Functions ---

def get_appdata_folder():
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
    else:
        appdata = os.path.expanduser("~/.config")
    app_folder = os.path.join(appdata, "MoonTTS")
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)
    return app_folder

output_path = os.path.join(get_appdata_folder(), "output.wav")
usage_file_path = os.path.join(get_appdata_folder(), "usage.json")

# --- Constants ---
USAGE_FILE = usage_file_path
CHARACTER_LIMIT = 5000
CHARACTER_LIMIT_PER_MONTH = 1000000

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                data = json.load(f)
                saved_month = data.get("month")
                current_month = datetime.now().strftime("%Y-%m")
                if saved_month != current_month:
                    print("New month detected. Resetting character usage.")
                    return 0, None, None, True, None, None
                else:
                    return (
                        data.get("characters_used", 0),
                        data.get("last_selected_device", None),
                        data.get("last_monitor_device", None),
                        data.get("monitor_enabled", True),
                        data.get("selected_language", "English-UK"),
                        data.get("selected_voice", "Leda")
                    )
        except json.JSONDecodeError:
            print("[Warning] usage.json is corrupted. Saving backup and resetting...")
            backup_path = os.path.join(get_appdata_folder(), "usage_corrupted.json")
            shutil.move(usage_file_path, backup_path)
            return 0, None, None, True, None, None
    return 0, None, None, True, None, None

def save_usage(characters_used, last_selected_device, last_monitor_device, monitor_enabled, selected_language, selected_voice):
    current_month = datetime.now().strftime("%Y-%m")
    with open(USAGE_FILE, "w") as f:
        json.dump({
            "characters_used": characters_used,
            "month": current_month,
            "last_selected_device": last_selected_device,
            "last_monitor_device": last_monitor_device,
            "monitor_enabled": monitor_enabled,
            "selected_language": selected_language,
            "selected_voice": selected_voice
        }, f)

# --- Load usage and initialize variables ---
default_language = "English-UK"
default_voice = "Leda"

(
    loaded_characters_used,
    loaded_last_selected_device,
    loaded_last_monitor_device,
    loaded_monitor_enabled,
    loaded_selected_language,
    loaded_selected_voice
) = load_usage()

characters_used = loaded_characters_used
selected_language = ctk.StringVar(value=loaded_selected_language or default_language)
selected_voice = ctk.StringVar(value=loaded_selected_voice or default_voice)
monitor_enabled = ctk.BooleanVar(value=loaded_monitor_enabled)
selected_device = ctk.StringVar(value=loaded_last_selected_device)
monitor_device = ctk.StringVar(value=loaded_last_monitor_device)

# --- TTS Function ---

def play_on_device(device_idx, data, fs):
    sd.play(data, fs, device=device_idx)
    sd.wait()

def update_voices():
    lang_name = selected_language.get()
    if lang_name in voice_data:
        voice_options = list(voice_data[lang_name]["voices"].keys())
        voice_combo.configure(values=voice_options)
        if selected_voice.get() not in voice_options:
            selected_voice.set(voice_options[0])

def text_to_speech(text):
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = resource_path("client_auth_moontts.json")
        try:
            client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print("Failed to load Google credentials:", e)
            ctk.CTkMessagebox(title="Google Auth Error", message=f"Could not authenticate with Google:\n{e}", icon="cancel")
            return

        lang_code = voice_data[selected_language.get()]["code"]
        voice_id = voice_data[selected_language.get()]["voices"][selected_voice.get()]

        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_id,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config,
        )

        with open(output_path, "wb") as out:
            out.write(response.audio_content)

        data, fs = sf.read(output_path, dtype='float32')

        # Main device
        device_index = device_indices.get(selected_device.get(), None)
        threading.Thread(target=play_on_device, args=(device_index, data, fs), daemon=True).start()

        # Monitor device
        if monitor_enabled.get() and monitor_device.get() in device_indices:
            monitor_index = device_indices.get(monitor_device.get(), None)
            threading.Thread(target=play_on_device, args=(monitor_index, data, fs), daemon=True).start()

    except Exception as e:
        print(f"Error: {e}")
        CTkMessagebox(title="Error", message=f"Something went wrong:\n{e}", icon="cancel")

def on_language_selected(event=None):
    update_voices()
    # Save all settings
    save_usage(
        characters_used,
        selected_device.get(),
        monitor_device.get(),
        monitor_enabled.get(),
        selected_language.get(),
        selected_voice.get()
    )

def on_voice_selected(event=None):
    save_usage(
        characters_used,
        selected_device.get(),
        monitor_device.get(),
        monitor_enabled.get(),
        selected_language.get(),
        selected_voice.get()
    )

def on_device_selected(event=None):
    save_usage(
        characters_used,
        selected_device.get(),
        monitor_device.get(),
        monitor_enabled.get(),
        selected_language.get(),
        selected_voice.get()
    )

def toggle_monitor():
    if monitor_enabled.get():
        device_combo2.configure(state="readonly")
    else:
        device_combo2.configure(state="disabled")
    save_usage(
        characters_used,
        selected_device.get(),
        monitor_device.get(),
        monitor_enabled.get(),
        selected_language.get(),
        selected_voice.get()
    )

# --- Exit Function ---
def on_closing():
    print("Exiting application...")
    root.destroy()
    sys.exit(0)

# --- Pin Toggle ---
def toggle_topmost():
    current = root.wm_attributes("-topmost")
    root.wm_attributes("-topmost", not current)
    if not current:
        topmost_button.configure(text="Unpin from Top", fg_color="#393648", text_color="#fff", hover_color="#393648")
    else:
        topmost_button.configure(text="Pin on Top", fg_color="#fff", text_color="#393648", hover_color="#fff")

# --- Speak Function ---
def speak_in_thread():
    global characters_used
    text = text_entry.get("1.0", "end").strip()
    if not text:
        ctk.CTkMessagebox(title="Warning", message="Please enter some text.", icon="warning")
        return
    if len(text) > CHARACTER_LIMIT:
        ctk.CTkMessagebox(title="Warning", message=f"Text is too long! Max {CHARACTER_LIMIT} characters.", icon="warning")
        return
    threading.Thread(target=text_to_speech, args=(text,), daemon=True).start()
    characters_used += len(text)
    save_usage(
        characters_used,
        selected_device.get(),
        monitor_device.get(),
        monitor_enabled.get(),
        selected_language.get(),
        selected_voice.get()
    )
    update_total_characters_used_label()

def update_total_characters_used_label():
    usage_percentage = (characters_used / CHARACTER_LIMIT_PER_MONTH) * 100
    total_used_label.configure(text=f"Total used this month: {characters_used} / 1,000,000 ({usage_percentage:.2f}%)")

# --- GUI Setup ---

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Title
banner = ctk.CTkImage(light_image=Image.open(resource_path("banner.png")), size=(400, 90))
banner_label = ctk.CTkLabel(frame_1, text="", image=banner, width=400, height=90)
banner_label.grid()

# Config frame
config_frame = ctk.CTkFrame(frame_1)
config_frame.configure(height=24, fg_color='#E1DEE8')
config_frame.grid(sticky="wne", pady=(0, 10))
config_frame.grid_columnconfigure((0, 1), weight=1)
config_frame.grid_rowconfigure(0, weight=0)

with open(resource_path("voices.json"), "r", encoding="utf-8") as f:
    voice_data = json.load(f)

# Language Selection
language_frame = ctk.CTkFrame(config_frame)
language_frame.configure(height=24, fg_color='#E1DEE8')
language_frame.grid(sticky="wne", column=0, row=0)
language_frame.grid_columnconfigure((0, 1), weight=1)
language_frame.grid_rowconfigure(0, weight=1)

language_label = ctk.CTkLabel(language_frame, text="Language:", font=("Inter", 20, "bold"), text_color="#393648")
language_label.grid(column=0, row=0, sticky='w', padx=(10, 0))

language_combo = ctk.CTkComboBox(
    language_frame,
    width=110,
    variable=selected_language,
    values=list(voice_data.keys()),
    command=on_language_selected,
    border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff"
)
language_combo.grid(column=1, row=0, pady=0, padx=(0, 10))

# Voice Selection
voice_frame = ctk.CTkFrame(config_frame)
voice_frame.configure(height=24, fg_color='#E1DEE8')
voice_frame.grid(sticky="wne", column=1, row=0)
voice_frame.grid_columnconfigure((0, 1), weight=1)
voice_frame.grid_rowconfigure(0, weight=1)

voice_label = ctk.CTkLabel(voice_frame, text="Voice:", font=("Inter", 20, "bold"), text_color="#393648")
voice_label.grid(column=0, row=0, sticky='w', padx=0)

voice_combo = ctk.CTkComboBox(
    voice_frame,
    width=90,
    state="readonly",
    variable=selected_voice,
    command=on_voice_selected,
    border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff"
)
voice_combo.grid(column=1, row=0, pady=0, padx=(0, 10))

# --- Set initial language & voice in widgets ---
language_combo.set(selected_language.get())
update_voices()
voice_combo.set(selected_voice.get())

# Text Entry
text_entry = ctk.CTkTextbox(frame_1, height=160, width=380, font=("Inter", 15))
text_entry.grid(column=0, pady=(0, 10), padx=10)

def on_enter(event):
    speak_in_thread()
    return "break"

text_entry.bind("<Return>", on_enter)

# Character Usage Label
total_used_label = ctk.CTkLabel(frame_1, text="", fg_color="#fff", height=30, corner_radius=5, font=("Inter", 14))
total_used_label.grid(column=0, padx=10, sticky='we')

# Device Selection
device_label = ctk.CTkLabel(frame_1, text="Audio Output:", font=("Inter", 20, "bold"), text_color="#393648")
device_label.grid(column=0, pady=(15, 0), sticky='w', padx=10)

device_combo = ctk.CTkComboBox(
    frame_1,
    width=400,
    state="readonly",
    variable=selected_device,
    command=on_device_selected,
    border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff"
)
device_combo.grid(column=0, pady=0, padx=10)

# Monitor Section
checkbox_frame = ctk.CTkFrame(frame_1)
checkbox_frame.configure(height=24, fg_color='#E1DEE8')
checkbox_frame.grid(sticky="wn", pady=(5, 0))
checkbox_frame.grid_columnconfigure((0, 1), weight=1)
checkbox_frame.grid_rowconfigure(0, weight=1)

monitor_label = ctk.CTkLabel(checkbox_frame, text="Monitoring:", font=("Inter", 20, "bold"), text_color="#393648")
monitor_label.grid(column=0, row=0, sticky='w', padx=10)

monitor_checkbox = ctk.CTkCheckBox(
    checkbox_frame, text=None, checkbox_width=18, checkbox_height=18,
    variable=monitor_enabled, border_width=9, fg_color="#fff",
    checkmark_color="#393648", border_color="#fff", hover_color="#fff",
    command=toggle_monitor
)
monitor_checkbox.grid(column=1, row=0, sticky='w', padx=10)

device_combo2 = ctk.CTkComboBox(
    frame_1, width=400, variable=monitor_device, command=on_device_selected,
    border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff"
)
device_combo2.grid(column=0, pady=0, padx=10)

# Frame for Buttons
buttons_frame = ctk.CTkFrame(frame_1)
buttons_frame.configure(height=20, fg_color="#E1DEE8")
buttons_frame.grid(sticky="n", pady=10)
buttons_frame.grid_columnconfigure((0, 1), weight=1)
buttons_frame.grid_rowconfigure(0, weight=0)

# Speak Button
speak_button = ctk.CTkButton(
    buttons_frame, text="Speak", command=speak_in_thread,
    font=("Inter", 24, "bold"), width=135, height=55, fg_color="#fff",
    text_color="#393648", hover_color="#fff"
)
speak_button.grid(column=0, row=0, padx=10)

# Pin Button
topmost_button = ctk.CTkButton(
    buttons_frame, text="Pin on Top", command=toggle_topmost,
    font=("Inter", 24, "bold"), width=235, height=55, fg_color="#fff",
    text_color="#393648", hover_color="#fff"
)
topmost_button.grid(column=1, row=0, padx=(0, 10))

# --- Load Devices ---
device_indices = {}
devices = sd.query_devices()
output_devices = []
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
device_combo.configure(values=output_devices)
device_combo2.configure(values=output_devices)

# Set default or loaded device selections
if selected_device.get() and selected_device.get() in device_indices:
    device_combo.set(selected_device.get())
else:
    if output_devices:
        selected_device.set(output_devices[0])
        device_combo.set(output_devices[0])

if monitor_device.get() and monitor_device.get() in device_indices:
    device_combo2.set(monitor_device.get())
else:
    if output_devices:
        monitor_device.set(output_devices[0])
        device_combo2.set(output_devices[0])

toggle_monitor()
update_total_characters_used_label()

root.protocol("WM_DELETE_WINDOW", on_closing)

# --- Mainloop ---
root.mainloop()