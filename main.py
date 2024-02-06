import pygame
import tkinter as tk
from tkinter import ttk
import os
import config

class SoundboardApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Star's Soundboard")

        # Set the directory path where your MP3 files are located
        self.directory_path = config.directory_path

        # Get a list of all MP3 files in the directory
        self.sound_files = [f for f in os.listdir(self.directory_path) if f.endswith(".mp3")]

        # Initialize pygame and set up the initial song index
        pygame.init()
        self.current_index = 0
        self.playing = False
        self.volume = 0.5  # Initial volume level

        # Tkinter UI elements
        self.label_current_song = ttk.Label(self.master, text="Current Song: None")
        self.label_current_song.pack(pady=10)

        self.button_start = ttk.Button(self.master, text="Start", command=self.start_queue)
        self.button_start.pack(pady=10)

        self.volume_scale = ttk.Scale(self.master, from_=0.0, to=1.0, orient="horizontal", length=200,
                                      variable=tk.DoubleVar(value=self.volume), command=self.update_volume)
        self.volume_scale.pack(pady=10)

        self.master.bind("<Right>", self.play_next)
        self.master.bind("<Left>", self.play_previous)
        self.master.bind("<Escape>", self.stop_queue)

        # Customized list of songs with timestamps (in seconds)
        self.queue = config.queue

        self.timer_id = None

    def start_queue(self):
        if not self.playing and self.current_index < len(self.queue):
            self.playing = True
            self.play_sound()

    def play_sound(self):
        if self.playing:
            current_song = self.queue[self.current_index]
            self.label_current_song.config(text=f"Current Song: {current_song['file']}")

            full_path = os.path.join(self.directory_path, current_song["file"])
            pygame.mixer.music.load(full_path)

            start_time = current_song["start_time"]
            end_time = current_song["end_time"]

            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(start=start_time)

            # Set a timer to pause the song at the specified end time
            self.timer_id = self.master.after(int((end_time - start_time) * 1000), self.pause_at_end_time)

    def pause_at_end_time(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.timer_id = None

    def play_next(self, event=None):
        if self.playing:
            pygame.mixer.music.unpause()
            pygame.mixer.music.stop()
            if self.timer_id is not None:
                self.master.after_cancel(self.timer_id)  # Cancel the timer for the current song
            self.current_index = (self.current_index + 1) % len(self.queue)
            self.play_sound()

    def play_previous(self, event=None):
        if self.playing:
            pygame.mixer.music.unpause()
            pygame.mixer.music.stop()
            if self.timer_id is not None:
                self.master.after_cancel(self.timer_id)  # Cancel the timer for the current song
            self.current_index = (self.current_index - 1) % len(self.queue)
            self.play_sound()

    def stop_queue(self, event=None):
        if self.playing:
            self.playing = False
            pygame.mixer.music.stop()
            self.label_current_song.config(text="Current Song: None")

    def update_volume(self, event):
        self.volume = self.volume_scale.get()
        pygame.mixer.music.set_volume(self.volume)

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundboardApp(root)
    root.mainloop()
