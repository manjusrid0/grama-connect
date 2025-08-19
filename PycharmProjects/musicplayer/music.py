import tkinter as tk
from tkinter import filedialog
from pygame import mixer

# Initialize Pygame mixer
mixer.init()
# Create the main window
root = tk.Tk()
root.title("Simple Music Player")
root.geometry("400x300")
root.configure(bg="lightblue")
# Global variable for music file path
music_file = ""
# Functions
def load_file():
    global music_file
    music_file = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if music_file:
        label_status.config(text="Loaded: " + music_file.split("/")[-1])
        mixer.music.load(music_file)
def play_music():
    if music_file:
        mixer.music.play()
        label_status.config(text="Playing")
def pause_music():
    mixer.music.pause()
    label_status.config(text="Paused")
def resume_music():
    mixer.music.unpause()
    label_status.config(text="Resumed")
def stop_music():
    mixer.music.stop()
    label_status.config(text="Stopped")
# GUI Buttons
btn_load = tk.Button(root, text="Load Music", command=load_file, width=15, bg="white")
btn_play = tk.Button(root, text="Play", command=play_music, width=15, bg="green", fg="white")
btn_pause = tk.Button(root, text="Pause", command=pause_music, width=15, bg="orange")
btn_resume = tk.Button(root, text="Resume", command=resume_music, width=15, bg="blue", fg="white")
btn_stop = tk.Button(root, text="Stop", command=stop_music, width=15, bg="red", fg="white")
# Status Label
label_status = tk.Label(root, text="No music loaded", bg="lightblue", fg="black")
# Layout
btn_load.pack(pady=10)
btn_play.pack(pady=5)
btn_pause.pack(pady=5)
btn_resume.pack(pady=5)
btn_stop.pack(pady=5)
label_status.pack(pady=20)
# Run the application
root.mainloop()
