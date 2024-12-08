import os
import re
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.easymp4 import EasyMP4
from mutagen.asf import ASF
from mutagen.oggvorbis import OggVorbis
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.wma', '.ogg', '.aac')

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
    exclude_instrumental = exclude_var.get()
    if not directory or not playlist_file or not base_directory:
        messagebox.showerror("Error", "Please select the music directory, base directory, and playlist file.")
        return
    progress_bar["value"] = 0
    progress_bar["maximum"] = len([os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(audio_extensions)])
    create_playlist(directory, playlist_file, base_directory, exclude_instrumental, update_progress)
    messagebox.showinfo("Success", f"Playlist created at {playlist_file}")

def update_progress(current, total):
    progress_bar["value"] = current
    progress_bar.update()

def launch_gui():
    global entry_directory, entry_playlist, entry_base_directory, progress_bar, exclude_var
    # Create the main window
    root = tk.Tk()
    root.title("Walkman Playlist Assistant Super Script (GUI)")

    # Create and place the widgets
    label_directory = tk.Label(root, text="Music Directory:")
    label_directory.grid(row=0, column=0, padx=10, pady=10)
    entry_directory = tk.Entry(root, width=50)
    entry_directory.grid(row=0, column=1, padx=10, pady=10)
    button_directory = tk.Button(root, text="Browse...", command=lambda: select_directory(entry_directory))
    button_directory.grid(row=0, column=2, padx=10, pady=10)

    label_base_directory = tk.Label(root, text="Base Directory:")
    label_base_directory.grid(row=1, column=0, padx=10, pady=10)
    entry_base_directory = tk.Entry(root, width=50)
    entry_base_directory.grid(row=1, column=1, padx=10, pady=10)
    button_base_directory = tk.Button(root, text="Browse...", command=lambda: select_directory(entry_base_directory))
    button_base_directory.grid(row=1, column=2, padx=10, pady=10)

    label_playlist = tk.Label(root, text="Playlist File:")
    label_playlist.grid(row=2, column=0, padx=10, pady=10)
    entry_playlist = tk.Entry(root, width=50)
    entry_playlist.grid(row=2, column=1, padx=10, pady=10)
    button_playlist = tk.Button(root, text="Browse...", command=select_playlist_file)
    button_playlist.grid(row=2, column=2, padx=10, pady=10)

    exclude_var = tk.BooleanVar()
    exclude_checkbox = tk.Checkbutton(root, text="Exclude 'Instrumental' and 'Karaoke' songs", variable=exclude_var)
    exclude_checkbox.grid(row=3, column=0, columnspan=3, pady=10)

    button_generate = tk.Button(root, text="Generate Playlist", command=generate_playlist)
    button_generate.grid(row=4, column=0, columnspan=3, pady=20)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.grid(row=5, column=0, columnspan=3, pady=10)

    # Run the main event loop
    root.mainloop()

def launch_command_line():
    music_directory = input("Enter the path to the music folder: ")
    base_directory = input("Enter the base directory to remove from paths: ")
    playlist_path = input("Enter the path for the output playlist file (e.g., playlist): ")
    exclude_instrumental = input("Exclude 'instrumental' and 'karaoke' songs? (yes/no): ").strip().lower() == 'yes'
    create_playlist(music_directory, playlist_path, base_directory, exclude_instrumental)
    print(f"Playlist created at {playlist_path}.m3u8")

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    if messagebox.askyesno("Choose Interface", "Do you want to use the GUI?"):
        root.destroy()
        launch_gui()
    else:
        root.destroy()
        launch_command_line()

if __name__ == "__main__":
    main()