import sounddevice as sd
import soundfile as sf
import os
import threading
from CTkMessagebox import CTkMessagebox
from google.cloud import texttospeech
from utils import get_appdata_folder


class TTSWorker:
    def __init__(self, app):
        self.app = app
        # --- Caching attributes for last TTS request ---
        self._last_text = None
        self._last_language = None
        self._last_voice = None
        self._last_audio_path = None
        self._last_volume = None
        self._playback_lock = threading.Lock()  # Ensure only one playback at a time

    def synthesize_and_play(self, text, lang, voice, output_device, monitor_device=None, volume=1.0):
        with self._playback_lock:
            cache_hit = (
                self._last_text == text and
                self._last_language == lang and
                self._last_voice == voice and
                os.path.exists(self._last_audio_path)
            )
            if cache_hit:
                data, fs = sf.read(self._last_audio_path, dtype='float32')
                data = data * float(volume)
                # Stop any previous playback before starting new one
                sd.stop()
                self._play_with_progress(data, fs, output_device, monitor_device, text_len=len(text), count_characters=False)
                self._last_volume = volume
                return

            try:
                cred_path = self.app.settings.google_api_json
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
                client = texttospeech.TextToSpeechClient()

                lang_code = self.app.voice_data[lang]["code"]
                voice_id = self.app.voice_data[lang]["voices"][voice]

                input_text = texttospeech.SynthesisInput(text=text)
                voice_params = texttospeech.VoiceSelectionParams(
                    language_code=lang_code,
                    name=voice_id,
                )
                audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

                response = client.synthesize_speech(
                    input=input_text,
                    voice=voice_params,
                    audio_config=audio_config,
                )

                output_path = os.path.join(get_appdata_folder(), "output.wav")
                with open(output_path, "wb") as out:
                    out.write(response.audio_content)

                data, fs = sf.read(output_path, dtype='float32')
                data = data * float(volume)  # Apply volume

                # Update cache
                self._last_text = text
                self._last_language = lang
                self._last_voice = voice
                self._last_audio_path = output_path
                self._last_volume = volume

                # Stop any previous playback before starting new one
                sd.stop()
                self._play_with_progress(data, fs, output_device, monitor_device, text_len=len(text), count_characters=True)
            except Exception as e:
                self.app.root.after(0, lambda: self.app.speak_button.configure(state="normal", text="Speak"))
                self.app.root.after(0, lambda: self.app.progress_var.set(0.0))
                from tkinter import messagebox
                self.app.root.after(0, lambda: messagebox.showerror("TTS Error", f"Error: {e}"))

    
    def _play_with_progress(self, data, fs, output_device, monitor_device, text_len, count_characters):
        duration = len(data) / fs
        device_indices = self.app.device_indices
        main_idx = device_indices.get(output_device)
        mon_idx = device_indices.get(monitor_device) if monitor_device else None

        def is_valid_output_device(dev_idx):
            try:
                info = sd.query_devices(dev_idx)
                return info['max_output_channels'] > 0
            except Exception:
                return False

        def playback(dev_idx):
            try:
                sd.stop()
                sd.play(data, fs, device=dev_idx)
                sd.wait()
            except Exception as e:
                self.app.root.after(0, lambda: CTkMessagebox(
                    title="Playback Error",
                    message=f"Playback failed on device {dev_idx}: {e}",
                    icon="cancel",
                    master=self.app.root
                ))

        threads = []
        if main_idx is not None and is_valid_output_device(main_idx):
            threads.append(threading.Thread(target=playback, args=(main_idx,)))
        if mon_idx is not None and is_valid_output_device(mon_idx):
            threads.append(threading.Thread(target=playback, args=(mon_idx,)))
        for t in threads:
            t.start()

        def progress_updater():
            import time
            update_interval = 0.1
            total_steps = int(duration / update_interval)
            for i in range(total_steps):
                self.app.update_progress(i / total_steps)
                time.sleep(update_interval)
            self.app.update_progress(1.0)
            self.app.on_tts_finished(text_len, count_characters)
            self.app.update_progress(0.0)
        threading.Thread(target=progress_updater, daemon=True).start()

        for t in threads:
            t.join()