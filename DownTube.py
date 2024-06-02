import os
import sys
import requests
import threading
# import webbrowser
import subprocess
from PIL import Image
from pathlib import Path
import customtkinter as ctk
from pytube import YouTube, Playlist, request

loc = str(Path.home() / "Downloads")
loc = loc + '\DownTube'
if not os.path.exists(loc):
    os.makedirs(loc)

def progressUpdate(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    total = total_size / 1048567
    download = bytes_downloaded / 1048567
    live_progress = (bytes_downloaded / total_size)
    global downloadedLabel
    downloadedLabel.configure(text=str('%.2f'%download)+"/"+str('%.2f'%total)+"MB")
    global progress
    progress.set('%.2f'%live_progress)
    global percentage
    percentage.configure(text=str(int(progress.get()*100))+"%")


# def callback(url):
#     webbrowser.open_new(url)

def update(yt, url):
    global errorLabel
    errorLabel.configure(text="")
    global downloadedLabel
    downloadedLabel.configure(text="0.00/0.00 MB")
    global progress
    progress.set(0)
    global percentage
    percentage.configure(text="0%")
    thumbnail = Image.open(requests.get(yt.thumbnail_url, stream=True).raw)
    thumbnailImg = ctk.CTkImage(thumbnail, size=(178, 100))
    global image_label
    image_label.configure(image=thumbnailImg)
    # image_label.bind("<Button-1>", lambda e: callback(url))
    global ytTitleLable
    ytTitleLable.configure(text=yt.title)

def complete(size):
    global downloadedLabel
    downloadedLabel.configure(text=f"{size}/{size} MB")
    global progress
    progress.set(1)
    global percentage
    percentage.configure(text="100%")

def downloadVideo(url, quality, playlist_name=None, error=False):
    global titleLabel
    yt = YouTube(url, on_progress_callback=progressUpdate)
    update(yt, url)
    if quality == "720p":
        video = yt.streams.filter(type='video',progressive=True, res="720p").first()
    else:
        video = yt.streams.filter(type='video',progressive=True, res="360p").first()

    try:
        global downloadedLabel
        downloadedLabel.configure(text=str(0.00)+"/"+str('%.2f'%video.filesize_mb)+" MB")
        if playlist_name==None:
            video.download(loc+"\Video/")
        else:
            video.download(loc+"\Video/"+playlist_name)
        complete('%.2f'%video.filesize_mb)

    except Exception as e: 
        print(e)
        global errorLabel
        errorLabel.configure(text=f"{quality} isn't available")
        if not error:
            if quality == "720p":
                downloadVideo(url, "360p", playlist_name, True)
            else:
                downloadVideo(url, "360p", playlist_name, True)
        else:
            print(f'{yt.title} is not downloadable.')

def downloadVideoPlaylist(url, quality):
    global titleLabel
    playlist = Playlist(url)
    i = 0
    playlist_name = playlist.title
    characters_to_replace = r'\/:*?"<>|'
    for char in characters_to_replace:
        playlist_name = playlist_name.replace(char, ' ')
    for url in playlist.video_urls:
        i+=1
        video = downloadVideo(url, quality, playlist_name)
      

def downloadAudio(url, playlist_name=None):
    global titleLabel
    yt = YouTube(url, on_progress_callback=progressUpdate)
    update(yt, url)
    audio = yt.streams.filter(type='audio', abr="128kbps").first()
    try:
        global downloadedLabel
        downloadedLabel.configure(text=str(0.00)+"/"+str('%.2f'%audio.filesize_mb)+" MB")
        if playlist_name==None:
            file = audio.download(loc+"\Audio/")
        else:
            file = audio.download(loc+"\Audio/"+playlist_name)
        complete('%.2f'%audio.filesize_mb)
        base, ext = os.path.splitext(file) 
        new_file = base + '.mp3'
        os.rename(file, new_file)
    except Exception as e:
        print(e)
    

def downloadAudioPlaylist(url):
    global titleLabel
    playlist = Playlist(url)
    i = 0
    playlist_name = playlist.title
    characters_to_replace = r'\/:*?"<>|'
    for char in characters_to_replace:
        playlist_name = playlist_name.replace(char, ' ')
    for url in playlist.video_urls:
        i+=1
        audio = downloadAudio(url, playlist_name)

def check(url, filetype, quality):
    if '/playlist' in url:
        playlist = True
    else:
        playlist = False

    if filetype=="Video":
        if playlist:
            titleLabel.configure(text="Downloading : YouTube Video Playlist")
            video = downloadVideoPlaylist(url, quality)
            titleLabel.configure(text="Download Completed : YouTube Video Playlist")
        else:
            titleLabel.configure(text="Downloading : YouTube Video")
            downloadVideo(url, quality)
            titleLabel.configure(text="Download Completed : YouTube Video")
    else:
        if playlist:
            titleLabel.configure(text="Downloading : YouTube Audio Playlist")
            downloadAudioPlaylist(url)
            titleLabel.configure(text="Download Completed : YouTube Audio Playlist")
        else:
            titleLabel.configure(text="Downloading : YouTube Audio")
            downloadAudio(url)
            titleLabel.configure(text="Download Completed : YouTube Audio")


class downloadDetails(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        font1 = ctk.CTkFont(family='Helvetica', size=18, weight='bold')
        font2 = ctk.CTkFont(family='Helvetica', size=14)

        global titleLabel
        titleLabel = ctk.CTkLabel(self, text="Not Downloading anything", bg_color="transparent", text_color="White", font=font1, anchor="center")
        titleLabel.grid(row=0, column=0, columnspan=6, padx=100, pady=10, sticky="ew")

        yt = YouTube("https://www.youtube.com/watch?v=j9irZhdfxLk")
        thumbnail = Image.open(requests.get(yt.thumbnail_url, stream=True).raw)
        thumbnailImg = ctk.CTkImage(thumbnail, size=(178, 100))

        global image_label
        image_label = ctk.CTkLabel(self, image=thumbnailImg, text="", corner_radius=25)
        image_label.grid(row=1, column=0, rowspan=3, columnspan=2, padx=10, pady=10, sticky="we")

        global ytTitleLable
        ytTitleLable = ctk.CTkLabel(self, text=yt.title, text_color="White", bg_color="transparent", font=font2)
        ytTitleLable.grid(row=1, column=2, columnspan=5, padx=5, pady=5, sticky="w")
        
        global errorLabel
        errorLabel = ctk.CTkLabel(self, text="")
        errorLabel.grid(row=2, column=2, columnspan=3, sticky="w")

        # def cancelDownload():
        #     global downlaodThread
        #     downlaodThread.raise_exception()
        #     downlaodThread.join()

        # cancelBtn = ctk.CTkButton(self, text="Cancel Downloading", command=cancelDownload)
        # cancelBtn.grid(row=2, column=6, sticky="w")

        global downloadedLabel
        downloadedLabel = ctk.CTkLabel(self, text="0.00/00.0 MB")
        downloadedLabel.grid(row=3, column=2, sticky="e")

        global progress
        progress = ctk.DoubleVar(value=0.00)
        progressbar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", variable=progress)
        progressbar.grid(row=3, column=3, columnspan=2, padx=10, sticky="ew")

        global percentage
        percentage = ctk.CTkLabel(self, text="0%")
        percentage.grid(row=3, column=6, sticky="w")


class mainFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        font0 = ctk.CTkFont(family='Times New Roman', size=30, weight='bold')

        def sendDetails():
            details = {
                'url' : linkInput.get(),
                'filetype' : typeVar.get(),
                'quality' : qualityVar.get()
            }
            linkInput.delete(0, 'end')
            global downlaodThread
            downlaodThread = threading.Thread(target=check, kwargs=details)
            downlaodThread.start()
            # downlaodThred.join()
            
        def open_folder():
            subprocess.Popen(r'explorer "{}"'.format(loc))

        def open_folder_threading():
            threading.Thread(target=open_folder).start()

        titleLabel = ctk.CTkLabel(self, text="Welcome to DownTube", bg_color="transparent", text_color="White", font=font0, anchor="center")
        titleLabel.grid(row=0, column=0, columnspan=7, padx=265, pady=30, sticky="e")
        
        linkInput = ctk.CTkEntry(self, height=40, placeholder_text="Paste youtube link here")
        linkInput.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="ew")

        downloadBtn = ctk.CTkButton(self, height=30, text="Download", command=sendDetails)
        downloadBtn.grid(row=1, column=5, padx=5, sticky="ew")

        folderBtn = ctk.CTkButton(self, height=30, text="Folder", command=open_folder_threading)
        folderBtn.grid(row=1, column=6, padx=10, sticky="ew")

        qualityVar = ctk.StringVar(value="720p")
        qualityBtn = ctk.CTkSegmentedButton(self, values=["720p", "360p"], variable=qualityVar)
        qualityBtn.grid(row=2, column=0, columnspan=4, padx=10, pady=30, sticky="we")

        def switchType():
            typeSwitch.configure(text=typeVar.get())
            if(typeVar.get() == "Video"):
                qualityBtn.configure(state="normal")
            else:
                qualityBtn.configure(state="disabled")
        typeVar = ctk.StringVar(value="Video")
        typeSwitch = ctk.CTkSwitch(self, text=typeVar.get(), variable=typeVar, onvalue="Video", offvalue="Audio", command=switchType)
        typeSwitch.grid(row=2, column=4, sticky="e")

        def slider_event(value):
            speed =  speedVar.get()
            speedLabel.configure(text="Download Speed: "+str("%.1f"%speed)+"MB/s")
            request.default_range_size = int(1024*1024*speed)

        speedVar = ctk.DoubleVar(value=5.0)
        request.default_range_size = int(1024*1024*5)
        speedBtn = ctk.CTkSlider(self, width=150, from_=1, to=5, number_of_steps=40, command=slider_event, variable=speedVar)
        speedBtn.grid(row=2, column=6, padx=10, sticky="w")

        speedLabel = ctk.CTkLabel(self, text="Download Speed: "+str(speedVar.get())+"MB/s")
        speedLabel.grid(row=2, column=5, padx=5, sticky="e")

        self.downloadDetails = downloadDetails(self, width=814)
        self.downloadDetails.grid(row=3, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("854x480")
        self.title('DownTube')
        current_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(current_dir, 'downB.ico')
        self.iconbitmap(icon_path)
        
        self.main = mainFrame(master=self, width=834, height=460)
        self.main.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

app = App()
app.mainloop()

# Compiler Command
# pyinstaller --onefile --windowed --add-data "downB.ico;." --icon="downW.ico" DownTube.py