import os
import sys
import requests
import threading
# import webbrowser
import subprocess
from PIL import Image
from pathlib import Path
import customtkinter as ctk
from pytubefix import YouTube, Playlist, request
from moviepy.editor import VideoFileClip, AudioFileClip

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
    if len(yt.title) > 70:
        t = yt.title[0:70]+"..."
        ytTitleLable.configure(text=t)
    else:
        ytTitleLable.configure(text=yt.title)

def complete(size):
    global downloadedLabel
    downloadedLabel.configure(text=f"{size}/{size} MB")
    global progress
    progress.set(1)
    global percentage
    percentage.configure(text="100%")

def collectVideo(yt, quality, playlist_name):
    global downloadedLabel
    global errorLabel
    global statusLabel
    statusLabel.configure(text="Collecting Video file...")

    video = yt.streams.filter(mime_type="video/mp4", res=quality).first()
    if video == None:
        if playlist_name==None:
            errorLabel.configure(text=f"{quality} isn't available, select different resolution")
            return
        else:
            quality_list = ["1080p", "720p", "480p", "360p", "240p", "144p"]
            errorLabel.configure(text=f"{quality} isn't available, tying different resolution")
            for qlt in quality_list:
                video = yt.streams.filter(mime_type="video/mp4", res=qlt).first()
                if video != None:
                    break
            if video == None:
                errorLabel.configure(text=f"Unable to download this video ❗❗")
                return
        
    
    downloadedLabel.configure(text=str(0.00)+"/"+str('%.2f'%video.filesize_mb)+" MB")
    vid = video.download(loc+"\Tmp\Video/")
    complete('%.2f'%video.filesize_mb)
    return vid


def collectAudio(yt):
    global downloadedLabel
    global statusLabel
    statusLabel.configure(text="Collecting Audio file...")

    audio = yt.streams.filter(mime_type="audio/mp4", abr="128kbps").first()
    if audio == None:
        audio = yt.streams.filter(type="audio").desc().first()

    downloadedLabel.configure(text=str(0.00)+"/"+str('%.2f'%audio.filesize_mb)+" MB")
    aud = audio.download(loc+"\Tmp\Audio/")
    complete('%.2f'%audio.filesize_mb)
    return aud

def downloadVideo(url, quality, playlist_name=None, error=False):
    yt = YouTube(url, on_progress_callback=progressUpdate)
    update(yt, url)
    video = collectVideo(yt, quality, playlist_name)
    if video==None:
        return
    audio = collectAudio(yt)

    global statusLabel
    statusLabel.configure(text="Processing Video file...")
    try:
        clip = VideoFileClip(video) 
        audio_clip = AudioFileClip(audio)
        video_clip = clip.set_audio(audio_clip)
        output_file_name = os.path.basename(video)

        output_directory = os.path.join(loc, "Video")
        if playlist_name!=None:
            output_directory = os.path.join(output_directory, playlist_name)

        output_file_path = os.path.join(output_directory, output_file_name)
        video_clip.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
        statusLabel.configure(text="Video downloaded ✅")
        os.remove(video)
        os.remove(audio)
    except Exception as e: 
        print(e)


def downloadVideoPlaylist(url, quality):
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
    yt = YouTube(url, on_progress_callback=progressUpdate)
    update(yt, url)
    audio = collectAudio(yt)
    global statusLabel
    statusLabel.configure(text="Processing Audio file...")
    try:
        audio_clip = AudioFileClip(audio)
        output_file_name = os.path.basename(audio).replace('.mp4', '.mp3')
        output_directory = os.path.join(loc, "Audio")
        if playlist_name!=None:
            output_directory = os.path.join(output_directory, playlist_name)

        output_file_path = os.path.join(output_directory, output_file_name)
        audio_clip.write_audiofile(output_file_path)
        statusLabel.configure(text="Audio Downloaded ✅")
        os.remove(audio)
    except Exception as e:
        print(e)
    

def downloadAudioPlaylist(url):
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
        image_label.grid(row=1, column=0, rowspan=5, columnspan=2, padx=10, pady=10, sticky="we")

        global ytTitleLable
        ytTitleLable = ctk.CTkLabel(self, text=yt.title, text_color="White", bg_color="transparent", font=font2)
        ytTitleLable.grid(row=1, rowspan=2, column=2, columnspan=5, padx=5, pady=5, sticky="w")
        
        global errorLabel
        errorLabel = ctk.CTkLabel(self, text="", text_color="red")
        errorLabel.grid(row=3, column=2, columnspan=3, sticky="w")

        # def cancelDownload():
        #     global downlaodThread
        #     downlaodThread.raise_exception()
        #     downlaodThread.join()

        # cancelBtn = ctk.CTkButton(self, text="Cancel Downloading", command=cancelDownload)
        # cancelBtn.grid(row=2, column=6, sticky="w")

        global statusLabel
        statusLabel = ctk.CTkLabel(self, text="current status....")
        statusLabel.grid(row=4, column=2, columnspan=3, sticky="w")

        global downloadedLabel
        downloadedLabel = ctk.CTkLabel(self, text="0.00/00.0 MB")
        downloadedLabel.grid(row=5, column=2, sticky="e")

        global progress
        progress = ctk.DoubleVar(value=0.00)
        progressbar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", variable=progress)
        progressbar.grid(row=5, column=3, columnspan=2, padx=10, sticky="ew")

        global percentage
        percentage = ctk.CTkLabel(self, text="0%")
        percentage.grid(row=5, column=6, sticky="w")


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

        qualityVar = ctk.StringVar(value="1080p")
        qualityBtn = ctk.CTkOptionMenu(self, values=["1080p", "720p", "480p", "360p", "240p", "144p"], variable=qualityVar)
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