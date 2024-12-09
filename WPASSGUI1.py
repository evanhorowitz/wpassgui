import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.easymp4 import EasyMP4
from mutagen.asf import ASF
from mutagen.oggvorbis import OggVorbis

audio_extensions = ('.mp3', '.flac', '.wav', '.m4a', '.wma', '.ogg', '.aac')

def get_audio_length(file_path):
    try:
        if file_path.endswith('.mp3'):
            audio = MP3(file_path)
        elif file_path.endswith('.flac'):
            audio = FLAC(file_path)
        elif file_path.endswith('.wav'):
            audio = WAVE(file_path)
        elif file_path.endswith('.m4a'):
            audio = EasyMP4(file_path)
        elif file_path.endswith('.wma'):
            audio = ASF(file_path)
        elif file_path.endswith('.ogg'):
            audio = OggVorbis(file_path)
        elif file_path.endswith('.aac'):
            audio = mutagen.File(file_path)
        else:
            return None
        return int(audio.info.length)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def create_playlist(directory, playlist_file, base_directory, exclude_instrumental, progress_callback=None):
    if not playlist_file.endswith('.m3u8'):
        playlist_file += '.m3u8'
    files_to_process = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(audio_extensions)]
    total_files = len(files_to_process)
    
    with open(playlist_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for index, file_path in enumerate(files_to_process):
            print(f"Processing file: {file_path}")
            duration = get_audio_length(file_path)
            if duration is not None:
                artist = "Unknown Artist"
                title = os.path.splitext(os.path.basename(file_path))[0]
                try:
                    audio = mutagen.File(file_path)
                    if audio and audio.tags:
                        artist = audio.tags.get('TPE1', [artist])[0]
                        title = audio.tags.get('TIT2', [title])[0]
                except Exception as e:
                    print(f"Error reading tags from {file_path}: {e}")
                if exclude_instrumental and (re.search(r'instrumental', title, re.IGNORECASE) or re.search(r'karaoke', title, re.IGNORECASE)):
                    continue
                relative_path = os.path.relpath(file_path, base_directory)
                f.write(f"#EXTINF:{duration},{artist} - {title}\n")
                f.write(f"{relative_path}\n")
            if progress_callback:
                progress_callback(index + 1, total_files)

def select_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

def select_playlist_file():
    playlist_file = filedialog.asksaveasfilename(defaultextension=".m3u8", filetypes=[("M3U8 files", "*.m3u8")])
    if playlist_file:
        entry_playlist.delete(0, tk.END)
        entry_playlist.insert(0, playlist_file)

def generate_playlist():
    directory = entry_directory.get()
    playlist_file = entry_playlist.get()
    base_directory = entry_base_directory.get()
    exclude_instrumental = exclude_instrumental_var.get()
    create_playlist(directory, playlist_file, base_directory, exclude_instrumental, update_progress)

def update_progress(current, total):
    progress.set(f"Processed {current} of {total} files")
    progress_bar['value'] = (current / total) * 100
    percentage.set(f"{(current / total) * 100:.2f}%")

# GUI setup
root = tk.Tk()
root.title("Walkman Playlist Assistant Super Script (GUI Edition) v0.2")

# Use ttk for modern themed widgets
style = ttk.Style()
style.theme_use('clam')  # You can try 'clam', 'alt', 'default', or 'classic'

# Get the background color from the current theme
bg_color = style.lookup('TLabel', 'background')

# Define custom styles
style.configure('Custom.TLabel', background=bg_color)
style.configure('Custom.TCheckbutton', background=bg_color)

padding = {'padx': 10, 'pady': 5}

ttk.Label(root, text="Music Path:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, **padding)
entry_directory = ttk.Entry(root, width=50)
entry_directory.grid(row=0, column=1, sticky=tk.EW, **padding)
ttk.Button(root, text="Browse", command=lambda: select_directory(entry_directory)).grid(row=0, column=2, sticky=tk.EW, **padding)

ttk.Label(root, text="Base Playlist Directory:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, **padding)
entry_base_directory = ttk.Entry(root, width=50)
entry_base_directory.grid(row=1, column=1, sticky=tk.EW, **padding)
ttk.Button(root, text="Browse", command=lambda: select_directory(entry_base_directory)).grid(row=1, column=2, sticky=tk.EW, **padding)

ttk.Label(root, text="Playlist File Name:", style='Custom.TLabel').grid(row=2, column=0, sticky=tk.W, **padding)
entry_playlist = ttk.Entry(root, width=50)
entry_playlist.grid(row=2, column=1, sticky=tk.EW, **padding)
ttk.Button(root, text="Browse", command=select_playlist_file).grid(row=2, column=2, sticky=tk.EW, **padding)

exclude_instrumental_var = tk.BooleanVar()
ttk.Checkbutton(root, text="Exclude Instrumental/Karaoke Tracks", variable=exclude_instrumental_var, style='Custom.TCheckbutton').grid(row=3, columnspan=3, sticky=tk.W, **padding)

ttk.Button(root, text="Generate Playlist", command=generate_playlist).grid(row=4, columnspan=3, sticky=tk.EW, **padding)

progress = tk.StringVar()
ttk.Label(root, textvariable=progress, style='Custom.TLabel').grid(row=5, columnspan=3, sticky=tk.EW, **padding)

# Add progress bar and percentage label
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=2, sticky=tk.EW, **padding)

percentage = tk.StringVar()
ttk.Label(root, textvariable=percentage, style='Custom.TLabel').grid(row=6, column=2, sticky=tk.E, **padding)

# Make the window scalable
for i in range(3):
    root.grid_columnconfigure(i, weight=1)
for i in range(7):
    root.grid_rowconfigure(i, weight=1)

root.mainloop()