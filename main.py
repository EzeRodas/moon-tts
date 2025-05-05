from gui import MoonTTSApp
import customtkinter as ctk
import os

def get_credentials_path():
    # Check GOOGLE_APPLICATION_CREDENTIALS environment variable
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        return cred_path

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = MoonTTSApp(root)
    root.mainloop()