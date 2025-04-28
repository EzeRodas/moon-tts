# --- Imports ---
import os
import json
import threading
import shutil
import sys
from PIL import Image
from datetime import datetime
import customtkinter as ctk
import sounddevice as sd
import soundfile as sf
from google.cloud import texttospeech

# Interface

root = ctk.CTk(fg_color='#E1DEE8')
root.title("Demo-TTS")
root.geometry("400x500")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.resizable(False, False)
root.iconbitmap("icon.ico")

frame_1 = ctk.CTkFrame(root, width=400, height=500)

frame_1.configure(fg_color='#E1DEE8')
frame_1.grid(sticky="nswe")
frame_1.grid_columnconfigure((0, 1), weight=1)
frame_1.grid_propagate(0)

# --- Constants ---
USAGE_FILE = "usage.json"
CHARACTER_LIMIT = 5000
CHARACTER_LIMIT_PER_MONTH = 1000000

# --- Usage Functions ---
def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                data = json.load(f)
                saved_month = data.get("month")
                current_month = datetime.now().strftime("%Y-%m")

                if saved_month != current_month:
                    print("New month detected. Resetting character usage.")
                    return 0, None, None, True
                else:
                    return (
                        data.get("characters_used", 0),
                        data.get("last_selected_device", None),
                        data.get("last_monitor_device", None),
                        data.get("monitor_enabled", True)
                    )
        except json.JSONDecodeError:
            print("[Warning] usage.json is corrupted. Saving backup and resetting...")
            shutil.move(USAGE_FILE, USAGE_FILE.replace(".json", "_corrupted.json"))
            return 0, None, None, True
    return 0, None, None, True

def save_usage(characters_used, last_selected_device, last_monitor_device, monitor_enabled):
    current_month = datetime.now().strftime("%Y-%m")
    with open(USAGE_FILE, "w") as f:
        json.dump({
            "characters_used": characters_used,
            "month": current_month,
            "last_selected_device": last_selected_device,
            "last_monitor_device": last_monitor_device,
            "monitor_enabled": monitor_enabled
        }, f)

def on_device_selected(event=None):
    save_usage(
        characters_used,
        selected_device.get(),
        monitor_device.get(),
        monitor_enabled.get()
    )

# --- Initialize Usage ---
characters_used, last_selected_device, last_monitor_device, monitoring_state = load_usage()

# --- TTS Function ---
def text_to_speech(text):
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "F:\\Documents\\Programming\\Proyects\\Moon-TTS\\client_auth_moontts.json"
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Chirp3-HD-Leda",
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config,
        )

        with open("output.wav", "wb") as out:
            out.write(response.audio_content)


        if monitor_enabled.get() and monitor_device.get() in device_indices:
            device_index = device_indices.get(selected_device.get(), None)
            monitor_index = device_indices.get(monitor_device.get(), None)
            data, fs = sf.read('output.wav', dtype='float32')
            sd.play(data, fs, device=device_index)
            sd.play(data, fs, device=monitor_index)
            sd.wait()
        else:
            device_index = device_indices.get(selected_device.get(), None)
            data, fs = sf.read('output.wav', dtype='float32')
            sd.play(data, fs, device=device_index)
            sd.wait()


    except Exception as e:
        print(f"Error: {e}")
        ctk.CTkMessagebox(title="Error", message=f"Something went wrong:\n{e}", icon="cancel")

# --- Exit Function ---

def on_closing():
    print("Exiting application...")
    root.destroy()  # Destroy the window
    sys.exit(0)     # Force quit all threads

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
    save_usage(characters_used, selected_device.get(), monitor_device.get(), monitor_enabled.get())
    update_total_characters_used_label()

# --- Update Character Usage Label ---
def update_total_characters_used_label():
    usage_percentage = (characters_used / CHARACTER_LIMIT_PER_MONTH) * 100
    total_used_label.configure(text=f"Total used this month: {characters_used} / 1,000,000 ({usage_percentage:.2f}%)")

# --- GUI Setup ---

ctk.set_appearance_mode("Light")  # Light or Dark
ctk.set_default_color_theme("blue")  # Theme

# Title

banner = ctk.CTkImage(light_image=Image.open("banner.png"), size=(400, 90))
banner_label = ctk.CTkLabel(frame_1, text="", image=banner, width=400, height=90)
banner_label.grid()

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

selected_device = ctk.StringVar()

device_combo = ctk.CTkComboBox(frame_1, width=400, state="readonly", variable=selected_device, command=on_device_selected, border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff")
device_combo.grid(column=0, pady=0, padx=10)

# Monitor Section
monitor_enabled = ctk.BooleanVar(value=monitoring_state)

def toggle_monitor():
    if monitor_enabled.get():
        device_combo2.configure(state="readonly")
    else:
        device_combo2.configure(state="disabled")
    save_usage(characters_used, selected_device.get(), monitor_device.get(), monitor_enabled.get())

checkbox_frame = ctk.CTkFrame(frame_1)

checkbox_frame.configure(height=24, fg_color='#E1DEE8')
checkbox_frame.grid(sticky="wn", pady=(5, 0))
checkbox_frame.grid_columnconfigure((0, 1), weight=1)
checkbox_frame.grid_rowconfigure(0, weight=1)

monitor_label = ctk.CTkLabel(checkbox_frame, text="Monitoring:", font=("Inter", 20, "bold"), text_color="#393648")
monitor_label.grid(column=0, row=0, sticky='w', padx=10)

monitor_checkbox = ctk.CTkCheckBox(checkbox_frame, text=None, checkbox_width=18, checkbox_height=18, variable=monitor_enabled, border_width=9, fg_color="#fff", checkmark_color="#393648", border_color="#fff", hover_color="#fff", command=toggle_monitor)
monitor_checkbox.grid(column=1, row=0, sticky='w', padx=10)

monitor_device = ctk.StringVar()

device_combo2 = ctk.CTkComboBox(frame_1, width=400, variable=monitor_device, command=on_device_selected, border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff")
device_combo2.grid(column=0, pady=0, padx=10)

# Frame for Buttons

buttons_frame = ctk.CTkFrame(frame_1)

buttons_frame.configure(height=20, fg_color="#E1DEE8")
buttons_frame.grid(sticky="n", pady=10)
buttons_frame.grid_columnconfigure((0, 1), weight=1)
buttons_frame.grid_rowconfigure(0, weight=0)

# Speak Button
speak_button = ctk.CTkButton(buttons_frame, text="Speak", command=speak_in_thread, font=("Inter", 24, "bold"), width=135, height=55, fg_color="#fff", text_color="#393648", hover_color="#fff")
speak_button.grid(column=0, row=0, padx=10)

# Pin Button
topmost_button = ctk.CTkButton(buttons_frame, text="Pin on Top", command=toggle_topmost, font=("Inter", 24, "bold"), width=235, height=55, fg_color="#fff", text_color="#393648", hover_color="#fff")
topmost_button.grid(column=1, row=0, padx=(0, 10))


# --- Load Devices ---
device_indices = {}
devices = sd.query_devices()
output_devices = []
seen_device_keys = {} # Track already added names

for idx, device in enumerate(devices):
    # Only real output devices
    if device['max_output_channels'] > 0 and device['hostapi'] == 1:
        original_name = device['name'].strip()
        clean_key = original_name.lower()

        # Only add if this clean name hasn't been added yet
        if clean_key not in seen_device_keys:
            output_devices.append(original_name)  # Show clean visible name
            device_indices[original_name] = idx  # Save first matching index
            seen_device_keys[clean_key] = idx  # Track cleaned name

output_devices.sort()

device_combo.configure(values=output_devices)
device_combo2.configure(values=output_devices)

if last_selected_device and last_selected_device in device_indices:
    selected_device.set(last_selected_device)
else:
    if output_devices:
        selected_device.set(output_devices[0])

if last_monitor_device and last_monitor_device in device_indices:
    monitor_device.set(last_monitor_device)
else:
    if output_devices:
        monitor_device.set(output_devices[0])

monitor_enabled.set(monitoring_state)
toggle_monitor()

update_total_characters_used_label()

root.protocol("WM_DELETE_WINDOW", on_closing)

# --- Mainloop ---
root.mainloop()