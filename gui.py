import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import threading
from tts import TTSWorker
from settings import SettingsManager
from utils import resource_path, get_audio_devices

class MoonTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moon TTS v1.0.0")
        self.root.geometry("400x570")
        self.root.resizable(False, False)
        self.root.iconbitmap(resource_path("assets\\icon.ico"))

        # App state
        self.settings = SettingsManager()
        self.tts_worker = TTSWorker(self)
        self.voice_data = self.settings.load_voice_data()
        self.audio_devices, self.device_indices = get_audio_devices()

        # --- GUI Layout ---
        self._build_gui()
        self._load_settings_to_gui()
        self.update_voices()

    def _build_gui(self):
        frame_1 = ctk.CTkFrame(self.root, width=400, height=600, fg_color='#E1DEE8')
        frame_1.grid(sticky="nswe")
        frame_1.grid_columnconfigure((0, 1), weight=1)
        frame_1.grid_propagate(0)

        # Banner
        banner = ctk.CTkImage(light_image=Image.open(resource_path("assets\\banner.png")), size=(400, 90))
        banner_label = ctk.CTkLabel(frame_1, text="", image=banner, width=400, height=90)
        banner_label.grid(row=0, column=0, columnspan=2, pady=(0, 4))

        # Credentials selector
        credentials_frame = ctk.CTkFrame(frame_1, fg_color="#E1DEE8")
        credentials_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        self.select_credentials_button = ctk.CTkButton(
            credentials_frame, text="Select Google API Credentials",
            command=self.select_google_api_json, font=("Inter", 14, "bold"),
            width=180, height=28, fg_color="#fff", text_color="#393648", hover_color="#fff"
        )
        self.select_credentials_button.grid(row=0, column=0, sticky="w")

        self.credentials_label = ctk.CTkLabel(
            credentials_frame, text="", font=("Inter", 12), text_color="#393648"
        )
        self.credentials_label.grid(row=0, column=1, sticky="e", padx=(10,0))

        # Config frame
        config_frame = ctk.CTkFrame(frame_1, fg_color="#E1DEE8", height=24)
        config_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        config_frame.grid_columnconfigure((0, 1), weight=1)

        # Language
        language_frame = ctk.CTkFrame(config_frame, fg_color="#E1DEE8", height=24)
        language_frame.grid(sticky="wne", column=0, row=0)
        language_frame.grid_columnconfigure((0, 1), weight=1)
        self.language_var = ctk.StringVar()
        language_label = ctk.CTkLabel(language_frame, text="Language:", font=("Inter", 20, "bold"), text_color="#393648")
        language_label.grid(column=0, row=0, sticky='w', padx=(10, 0))
        self.language_combo = ctk.CTkComboBox(
            language_frame, width=110, variable=self.language_var,
            values=list(self.voice_data.keys()), command=self.on_language_selected,
            border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff"
        )
        self.language_combo.grid(column=1, row=0, pady=0, padx=(0, 10))

        # Voice
        voice_frame = ctk.CTkFrame(config_frame, fg_color="#E1DEE8", height=24)
        voice_frame.grid(sticky="wne", column=1, row=0)
        voice_frame.grid_columnconfigure((0, 1), weight=1)
        self.voice_var = ctk.StringVar()
        voice_label = ctk.CTkLabel(voice_frame, text="Voice:", font=("Inter", 20, "bold"), text_color="#393648")
        voice_label.grid(column=0, row=0, sticky='w', padx=0)
        self.voice_combo = ctk.CTkComboBox(
            voice_frame, width=90, state="readonly", variable=self.voice_var,
            command=self.on_voice_selected, border_color="#fff", fg_color="#fff",
            dropdown_fg_color="#fff", border_width=0, button_color="#fff"
        )
        self.voice_combo.grid(column=1, row=0, pady=0, padx=(0, 10))

        # Text Entry
        self.text_entry = ctk.CTkTextbox(frame_1, height=120, width=380, font=("Inter", 15), wrap="word")
        self.text_entry.grid(row=3, column=0, columnspan=2, pady=(0, 10), padx=10)
        self.text_entry.bind("<Return>", self.on_enter)
        self.text_entry.bind("<Control-v>", self._on_ctrl_v)
        self.text_entry.bind("<Button-1>", self._on_text_click)

        def select_all(event):
            event.widget.tag_add("sel", "1.0", "end-1c")
            return "break"

        self.text_entry.bind("<Control-a>", select_all)
        self.text_entry.bind("<Control-A>", select_all)

        # Character Usage Label
        self.total_used_label = ctk.CTkLabel(frame_1, text="", fg_color="#fff", height=30, corner_radius=5, font=("Inter", 14))
        self.total_used_label.grid(row=4, column=0, columnspan=2, padx=10, sticky='we')

        # Device selection
        device_label = ctk.CTkLabel(frame_1, text="Audio Output:", font=("Inter", 20, "bold"), text_color="#393648")
        device_label.grid(row=5, column=0, columnspan=2, pady=(5, 0), sticky='w', padx=10)
        self.selected_device_var = ctk.StringVar()
        self.device_combo = ctk.CTkComboBox(
            frame_1, width=400, state="readonly", variable=self.selected_device_var,
            command=self.on_device_selected, border_color="#fff", fg_color="#fff",
            dropdown_fg_color="#fff", border_width=0, button_color="#fff"
        )
        self.device_combo.grid(row=6, column=0, columnspan=2, pady=0, padx=10)
        self.device_combo.configure(values=self.audio_devices)

        # Monitor Section
        checkbox_frame = ctk.CTkFrame(frame_1, fg_color="#E1DEE8", height=24)
        checkbox_frame.grid(row=7, column=0, columnspan=2, sticky="w", pady=(5, 0))
        checkbox_frame.grid_columnconfigure((0, 1), weight=1)
        self.monitor_var = ctk.BooleanVar()
        monitor_label = ctk.CTkLabel(checkbox_frame, text="Monitoring:", font=("Inter", 20, "bold"), text_color="#393648")
        monitor_label.grid(column=0, row=0, sticky='w', padx=10)
        monitor_checkbox = ctk.CTkCheckBox(
            checkbox_frame, text=None, checkbox_width=18, checkbox_height=18,
            variable=self.monitor_var, border_width=9, fg_color="#fff",
            checkmark_color="#393648", border_color="#fff", hover_color="#fff",
            command=self.toggle_monitor
        )
        monitor_checkbox.grid(column=1, row=0, sticky='w', padx=10)

        self.monitor_device_var = ctk.StringVar()
        self.device_combo2 = ctk.CTkComboBox(
            frame_1, width=400, variable=self.monitor_device_var, command=self.on_device_selected,
            border_color="#fff", fg_color="#fff", dropdown_fg_color="#fff", border_width=0, button_color="#fff"
        )
        self.device_combo2.grid(row=8, column=0, columnspan=2, pady=0, padx=10)
        self.device_combo2.configure(values=self.audio_devices)

        # Volume slider
        volume_frame = ctk.CTkFrame(frame_1, fg_color="#E1DEE8")
        volume_frame.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 0))
        ctk.CTkLabel(volume_frame, text="Volume:", font=("Inter", 14), text_color="#393648").grid(row=0, column=0, sticky="w")

        self.volume_var = ctk.DoubleVar(value=1.0)
        self.volume_slider = ctk.CTkSlider(
            volume_frame, from_=0.0, to=1.0, variable=self.volume_var, width=180, command=self.on_volume_change, button_color="#393648", button_hover_color="#6f6a84", progress_color="#393648"
        )
        self.volume_slider.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Volume percentage label
        self.volume_percent_label = ctk.CTkLabel(volume_frame, text="100%", font=("Inter", 14), text_color="#393648")
        self.volume_percent_label.grid(row=0, column=2, padx=(10, 0), sticky="w")

        # Progress bar for audio playback
        self.progress_var = ctk.DoubleVar(value=0.0)
        self.progress_bar = ctk.CTkProgressBar(frame_1, variable=self.progress_var, width=350)
        self.progress_bar.grid(row=10, column=0, columnspan=2, pady=(8, 0), padx=20)

        self.progress_bar.configure(fg_color="#C0BEC6", progress_color="#C0BEC6")

        # Buttons
        buttons_frame = ctk.CTkFrame(frame_1, fg_color="#E1DEE8", height=20)
        buttons_frame.grid(row=11, column=0, columnspan=2, sticky="n", pady=(10, 0))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        self.speak_button = ctk.CTkButton(
            buttons_frame, text="Speak", command=self.speak_in_thread,
            font=("Inter", 24, "bold"), width=135, height=55, fg_color="#fff",
            text_color="#393648", hover_color="#fff"
        )
        self.speak_button.grid(column=0, row=0, padx=10)
        self.topmost_button = ctk.CTkButton(
            buttons_frame, text="Pin on Top", command=self.toggle_topmost,
            font=("Inter", 24, "bold"), width=235, height=55, fg_color="#fff",
            text_color="#393648", hover_color="#fff"
        )
        self.topmost_button.grid(column=1, row=0, padx=(0, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_settings_to_gui(self):
        cred_path = self.settings.google_api_json

        if cred_path and os.path.exists(cred_path):
            display_text = os.path.basename(cred_path)
        else:
            display_text = "No credentials selected"

        self.credentials_label.configure(text=display_text)
        
        self.language_var.set(self.settings.selected_language)
        self.voice_var.set(self.settings.selected_voice)
        if self.settings.selected_device in self.audio_devices:
            self.selected_device_var.set(self.settings.selected_device)
        else:
            self.selected_device_var.set(self.audio_devices[0] if self.audio_devices else "")
        if self.settings.monitor_device in self.audio_devices:
            self.monitor_device_var.set(self.settings.monitor_device)
        else:
            self.monitor_device_var.set(self.audio_devices[0] if self.audio_devices else "")
        self.monitor_var.set(self.settings.monitor_enabled)
        self.volume_var.set(self.settings.volume)
        self.volume_percent_label.configure(text=f"{int(self.volume_var.get() * 100)}%")
        self.toggle_monitor()
        self.update_total_characters_used_label()

    def update_voices(self):
        lang_name = self.language_var.get()
        if lang_name in self.voice_data:
            voice_options = list(self.voice_data[lang_name]["voices"].keys())
            self.voice_combo.configure(values=voice_options)
            if self.voice_var.get() not in voice_options:
                self.voice_var.set(voice_options[0])

    def update_total_characters_used_label(self):
        usage_percentage = (self.settings.characters_used / self.settings.character_limit_per_month) * 100
        self.total_used_label.configure(text=f"Total used this month: {self.settings.characters_used} / 1,000,000 ({usage_percentage:.2f}%)")

    def on_language_selected(self, event=None):
        self.update_voices()
        self._save_gui_settings()

    def on_voice_selected(self, event=None):
        self._save_gui_settings()

    def on_device_selected(self, event=None):
        self._save_gui_settings()

    def select_google_api_json(self):
        file_path = filedialog.askopenfilename(
            title="Select Google API Credentials JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            self.settings.google_api_json = file_path
            self.credentials_label.configure(text=os.path.basename(file_path))
            self._save_gui_settings()

    def toggle_monitor(self):
        if self.monitor_var.get():
            self.device_combo2.configure(state="readonly")
        else:
            self.device_combo2.configure(state="disabled")
        self._save_gui_settings()

    def toggle_topmost(self):
        current = self.root.wm_attributes("-topmost")
        self.root.wm_attributes("-topmost", not current)
        if not current:
            self.topmost_button.configure(text="Unpin from Top", fg_color="#393648", text_color="#fff", hover_color="#393648")
        else:
            self.topmost_button.configure(text="Pin on Top", fg_color="#fff", text_color="#393648", hover_color="#fff")

    def speak_in_thread(self):
        self.speak_button.configure(state="disabled")
        text = self.text_entry.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text.")
            self.speak_button.configure(state="normal", text="Speak")
            return
        if len(text) > self.settings.character_limit:
            messagebox.showwarning("Warning", f"Text is too long! Max {self.settings.character_limit} characters.")
            self.speak_button.configure(state="normal", text="Speak")
            return

        # CHECK FREE QUOTA LIMIT!

        self.safety_margin = 10000

        if (self.settings.characters_used + len(text)) > self.settings.character_limit_per_month or (self.settings.characters_used + len(text)) > (self.settings.character_limit_per_month - self.safety_margin):
            messagebox.showwarning(
                "Limit reached",
                "You are about to exceed your monthly free quota for Google TTS.\n"
                "No further requests will be sent to avoid charges."
            )
            self.speak_button.configure(state="normal", text="Speak")
            return

        threading.Thread(target=self._tts_and_play, args=(text,), daemon=True).start()

    def _tts_and_play(self, text):
        self.tts_worker.synthesize_and_play(
            text,
            lang=self.language_var.get(),
            voice=self.voice_var.get(),
            output_device=self.selected_device_var.get(),
            monitor_device=self.monitor_device_var.get() if self.monitor_var.get() else None,
            volume=self.volume_var.get()
        )

    def on_tts_finished(self, text_len, count_characters=True):
        if count_characters:
            self.settings.characters_used += text_len
        self.root.after(0, lambda: [
            self.speak_button.configure(state="normal", text="Speak"),
            self.update_total_characters_used_label()
        ])
        self._save_gui_settings()

    def on_volume_change(self, value):
        self.settings.volume = value
        percent = int(float(value) * 100)
        self.volume_percent_label.configure(text=f"{percent}%")
        self._save_gui_settings()

    def on_enter(self, event):
        self.speak_in_thread()
        return "break"

    def _on_ctrl_v(self, event):
        try:
            text = self.root.clipboard_get()
            self.text_entry.insert("insert", text)
        except Exception:
            pass
        return "break"

    def _on_text_click(self, event):
        self.text_entry.focus_set()

    def _save_gui_settings(self):
        self.settings.selected_language = self.language_var.get()
        self.settings.selected_voice = self.voice_var.get()
        self.settings.selected_device = self.selected_device_var.get()
        self.settings.monitor_device = self.monitor_device_var.get()
        self.settings.monitor_enabled = self.monitor_var.get()
        self.settings.volume = self.volume_var.get()
        self.settings.save()

    def update_progress(self, value):
        if value > 0:
            # Active: set to color
            self.progress_bar.configure(progress_color="#393648", fg_color="#C0BEC6")
        else:
            # Idle: set to gray
            self.progress_bar.configure(progress_color="#C0BEC6", fg_color="#C0BEC6")
        self.root.after(0, lambda: self.progress_var.set(value))

    def on_closing(self):
        self.settings.save()
        self.root.destroy()