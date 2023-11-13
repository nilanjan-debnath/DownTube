import os
import sys
import threading
import subprocess
from pathlib import Path
from tkinter import *
from tkinter.ttk import *
import tkinter as tk
from tkinter import ttk
from pytube import YouTube, Playlist

loc = str(Path.home() / "Downloads")
loc = loc + '\DownTube'
if not os.path.exists(loc):
    os.makedirs(loc)

def ytvideo(link):
    video = YouTube(link)
    progress_label.config(text = video.title+'\nVideo Downloading....')
    if dropdown_var.get() == "720p":
        video = video.streams.filter(type='video',progressive=True, res="720p").first()
    elif dropdown_var.get() == "360p":
        video = video.streams.filter(type='video',progressive=True, res="360p").first()
    elif dropdown_var.get() == "144p":
        video = video.streams.filter(type='video',progressive=True, res="144p").first()
    try:
        video.download(loc+"\Video/")
        progress_label.config(text ="Video: "+ video.title +"\nDownlad Completed!")
    except:
        progress_label.config(text = "Video may not be downloaded, try again!")

def ytaudio(link):
    audio = YouTube(link)
    progress_label.config(text = audio.title+'\nAudio Downloading....')
    try:
        file = audio.streams.filter(type='audio').order_by('abr').desc().first().download(loc+"\Audio/")
        base, ext = os.path.splitext(file) 
        new_file = base + '.mp3'
        os.rename(file, new_file)
        progress_label.config(text ="Audio: "+audio.title+"\nDownlad Completed!")
    except:
        progress_label.config(text = "Audio may not be downloaded, try again!")

def ytplaylist(link):
    playlist = Playlist(link)
    progress_label.config(text = playlist.title+'\nVideo Count:  '+str(len(playlist.video_urls)))
    i = 0
    playlist_name = playlist.title
    characters_to_replace = r'\/:*?"<>|'
    for char in characters_to_replace:
        playlist_name = playlist_name.replace(char, ' ')
    for url in playlist.video_urls:
        i+=1
        video = YouTube(url)
        progress_label.config(text ='Playlist: '+ playlist.title+'\n'+str(i)+': '+video.title+'\nVideo Downloading....')
        if dropdown_var.get() == "720p":
            video = video.streams.filter(type='video',progressive=True, res="720p").first()
        elif dropdown_var.get() == "360p":
            video = video.streams.filter(type='video',progressive=True, res="360p").first()
        elif dropdown_var.get() == "144p":
            video = video.streams.filter(type='video',progressive=True, res="144p").first()
        try:
            video.download(loc+"\Video/"+playlist_name)
            progress_label.config(text =playlist.title+' : Playlist\n'+str(i)+': '+video.title+'\nCompleted')
        except:
            progress_label.config(text = "Video may not be downloaded, try again!")
    progress_label.config(text ="Download is completed successfully")

def ytplaylistaudio(link):
    playlist = Playlist(link)
    progress_label.config(text = playlist.title+'\nAudio Count:  '+str(len(playlist.video_urls)))
    i = 0
    playlist_name = playlist.title
    characters_to_replace = r'\/:*?"<>|'
    for char in characters_to_replace:
        playlist_name = playlist_name.replace(char, ' ')
    for url in playlist.video_urls:
        i += 1
        audio = YouTube(url)
        progress_label.config(text ='Playlist: '+ playlist.title+'\n'+str(i)+': '+audio.title+'\nAudio Downloading....')
        try:
            file = audio.streams.filter(type='audio').order_by('abr').desc().first().download(loc+"\Audio/"+playlist_name)
            base, ext = os.path.splitext(file) 
            new_file = base + '.mp3'
            os.rename(file, new_file)
            progress_label.config(text =playlist.title+' : Playslist\n'+str(i)+': '+audio.title+'\nCompleted')
        except:
            progress_label.config(text = "Audio may not be downloaded, try again!")
    progress_label.config(text ="Download is completed successfully")

# Create the main window
root = tk.Tk()
root.title("DownTube v0.1.2")
root.geometry('600x400')
root.minsize(500,300)
root.maxsize(700, 500)

current_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
icon_path = os.path.join(current_dir, 'downB.ico')
root.iconbitmap(icon_path)

def download():
    progress_label.config(text="Loading....")
    url = str(input_entry.get())
    if '/playlist' in url:
        if radio_var.get() == 1:
            threading.Thread(target=ytplaylist(url)).start()
        else:
            threading.Thread(target=ytplaylistaudio(url)).start()
    else:
        if radio_var.get() == 1:
            threading.Thread(target=ytvideo(url)).start()
        else:
            threading.Thread(target=ytaudio(url)).start()

def download_threading():
    threading.Thread(target=download).start()

def open_folder():
    subprocess.Popen(r'explorer "{}"'.format(loc))
def open_folder_threading():
    threading.Thread(target=open_folder).start()

# Title bar
title_label = ttk.Label(root, text="Paste YouTube link below", font=("Arial", 20))
title_label.pack(pady=20)

# Input space and button
input_frame = ttk.Frame(root)
input_frame.pack(pady=20)

input_entry = ttk.Entry(input_frame, width=40, font=('Arial 12'))
input_entry.pack(side=tk.LEFT, padx=5)

button = ttk.Button(input_frame, text="Download", width=10, command=download_threading)
button.pack(side=tk.LEFT)

folder_button = ttk.Button(input_frame, text="Folder", width=10, command=open_folder_threading)
folder_button.pack(side=tk.LEFT)

def enable_redio():
    dropdown_menu.configure(state="normal")
def disable_redio():
    dropdown_menu.configure(state="disabled")

# Radio buttons and drop-down menu
radio_frame = ttk.Frame(root)
radio_frame.pack(pady=15)

radio_var = tk.IntVar(value=1)
radio1 = ttk.Radiobutton(radio_frame, text="Video", variable=radio_var, value=1, command=enable_redio)
radio1.pack(side=tk.LEFT, padx=5)
radio2 = ttk.Radiobutton(radio_frame, text="Audio", variable=radio_var, value=2, command=disable_redio)
radio2.pack(side=tk.LEFT, padx=5)

options = ["720p", "360p", "144p"]
dropdown_var = tk.StringVar(value="720p")
dropdown_menu = ttk.Combobox(root, textvariable=dropdown_var, values=options, width=15)
dropdown_menu.pack(pady=10)

progress_label = ttk.Label(root, text="Download is not started", width=40, font=("Arial", 12))
progress_label.pack(pady=20, anchor='center')

# Run the application
root.mainloop()

# Compiler Command
# pyinstaller --onefile --windowed --add-data "downB.ico;." --icon="downW.ico" --name="DownTube v0.1.2" DownTube.py