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
        self.volume = 1  # Initial volume level

        # Tkinter UI elements
        self.label_current_song = ttk.Label(self.master, text="Current Song: None")
        self.label_current_song.pack(pady=10)

        self.label_countdown = ttk.Label(self.master, text="Countdown: --:--")
        self.label_countdown.pack(pady=5)

        self.button_start = ttk.Button(self.master, text="Start", command=self.start_queue)
        self.button_start.pack(pady=10)

        self.volume_scale = ttk.Scale(self.master, from_=0.0, to=1.0, orient="horizontal", length=200,
                                      variable=tk.DoubleVar(value=self.volume), command=self.update_volume)
        self.volume_scale.pack(pady=10)

        # Start button & Emergency switch off
        self.master.bind("<Return>", self.start_queue)
        self.master.bind("<Escape>", self.stop_queue)
        # Skip buttons
        self.master.bind("<Right>", self.play_next)
        self.master.bind("<Left>", self.play_previous)
        # Volume control
        self.master.bind("<Up>", self.increase_volume)
        self.master.bind("<Down>", self.decrease_volume)

        # Customized list of songs with timestamps (in seconds)
        self.queue = config.queue

        self.timer_id = None
        self.countdown_timer_id = None

    def start_queue(self, event=None):
        if not self.playing and self.current_index < len(self.queue):
            self.playing = True
            self.play_sound()
            # Hide the start button after it's been pressed
            self.button_start.pack_forget()
            # Start countdown timer
            self.start_countdown_timer()

    def start_countdown_timer(self):
        self.update_countdown()

    def update_countdown(self):
        if self.playing and self.current_index < len(self.queue):
            current_song = self.queue[self.current_index]
            start_time = current_song["start_time"]
            end_time = current_song["end_time"]
            clip_length = end_time - start_time
            remaining_time = int(clip_length - pygame.mixer.music.get_pos() / 1000)
            self.label_countdown.config(text=f"Fadeout in: {remaining_time // 60:02d}:{remaining_time % 60:02d}")
            self.countdown_timer_id = self.master.after(1000, self.update_countdown)

    def play_sound(self):
        if self.playing:
            current_song = self.queue[self.current_index]
            self.label_current_song.config(text=f"Playing: {current_song['file']}")

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
            if self.countdown_timer_id is not None:
                self.master.after_cancel(self.countdown_timer_id)  # Cancel the countdown timer
            self.current_index = (self.current_index + 1) % len(self.queue)
            self.play_sound()
            self.start_countdown_timer()

    def play_previous(self, event=None):
        if self.playing:
            pygame.mixer.music.unpause()
            pygame.mixer.music.stop()
            if self.timer_id is not None:
                self.master.after_cancel(self.timer_id)  # Cancel the timer for the current song
            if self.countdown_timer_id is not None:
                self.master.after_cancel(self.countdown_timer_id)  # Cancel the countdown timer
            self.current_index = (self.current_index - 1) % len(self.queue)
            self.play_sound()
            self.start_countdown_timer()

    def stop_queue(self, event=None):


        if self.playing:
            self.playing = False
            pygame.mixer.music.stop()
            self.label_current_song.config(text="Playing: //")
            if self.countdown_timer_id is not None:
                self.master.after_cancel(self.countdown_timer_id)  # Cancel the countdown timer
            if self.timer_id is not None:
                self.master.after_cancel(self.timer_id)  # Cancel the pause_at_end_time timer
        restart_app(self.master)

    def update_volume(self, event):
        self.volume = self.volume_scale.get()
        pygame.mixer.music.set_volume(self.volume)

    def increase_volume(self, event=None):
        # Increase volume by 0.1, but not beyond 1.0 (maximum volume)
        if self.volume < 1.0:
            self.volume = min(1.0, self.volume + 0.1)
            pygame.mixer.music.set_volume(self.volume)
            self.volume_scale.set(self.volume)

    def decrease_volume(self, event=None):
        # Decrease volume by 0.1, but not below 0.0 (minimum volume)
        if self.volume > 0.0:
            self.volume = max(0.0, self.volume - 0.1)
            pygame.mixer.music.set_volume(self.volume)
            self.volume_scale.set(self.volume)

def restart_app(root):
    # Close the current Tkinter window
    root.destroy()
    # Recreate the Tkinter window
    main()

def main():
    root = tk.Tk()

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y positions for the window to appear in the center
    x = (screen_width - 500) // 2  # Adjust 500 as the desired width of the window
    y = (screen_height - 200) // 2  # Adjust 200 as the desired height of the window

    root.geometry(f"500x200+{x}+{y}")  # Set the geometry with calculated position

    app = SoundboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
