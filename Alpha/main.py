import os
import sys
import subprocess
import customtkinter
from pathlib import Path
from pytube import YouTube

video_list = ["Audio Only", "1080p", "720p", "Lowest Res"]
illegal_chars = ("#", "%", "&", "{", "}", "\\", "<", ">", "*", "?", "/", "$", "!", "'", '"', ":", "@", "+", "`", "|", "=")

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

downloads_path = f"{application_path}/Thee Downloaded/"
Path(f"{application_path}/Thee Downloaded").mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent.absolute()}/pytube/__cache__").mkdir(parents=True, exist_ok=True)


def start_download():
    print(dl_link.get())
    try:
        if dl_link.get() == "":
            download_completed.configure(text=f"URL Field Is Blank")
            reset_app(True)
            return
        elif video_res.get() == "":
            download_completed.configure(text=f"Drop-Down Menu Is Blank")
            reset_app(True)
            return
        download_completed.configure(text="")
        title.configure(text="Processing Request")
        hd_res, audio_only, audio_download, new_filename = False, False, None, ""
        youtube_object = YouTube(dl_link.get(), use_oauth=True, allow_oauth_cache=True)
        if video_res.get() == "Audio Only":
            audio_only = True
            download = youtube_object.streams.get_audio_only()
        elif video_res.get() == "1080p":
            hd_res = True
            download = youtube_object.streams.get_by_resolution(resolution="1080p")
            if download is None:
                download_completed.configure(text=f"There is no 1080p version of this video, select 720p")
                reset_app(True)
                return
            audio_download = youtube_object.streams.get_audio_only()
        elif video_res.get() == "720p":
            download = youtube_object.streams.get_highest_resolution()
        elif video_res.get() == "Lowest Res":
            download = youtube_object.streams.get_lowest_resolution()
        else:
            download_completed.configure(text=f"Error downloading file, must choose {', '.join(video_list)}")
            reset_app(True)
            return
        filename = f"{youtube_object.author}--{youtube_object.title}.mp4"
        for letter in filename:
            if letter in illegal_chars:
                letter = "X"
            elif letter == " ":
                letter = "_"
            new_filename += letter
        filename = new_filename
        download.download(filename=filename)
        if audio_only:
            audio_filename = f"{filename[:-4]}.mp3"
            subprocess.run(f"ffmpeg -i {filename} {audio_filename}")
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(audio_filename):
                os.rename(audio_filename, f"{downloads_path}{audio_filename.replace('_', ' ')}")
            download_completed.configure(text=f"{filename.replace('_', ' ')}\nAudio Downloaded")
        elif hd_res:
            audio_filename = f"{filename[:-4]}.mp3"
            audio_download.download(filename=audio_filename)
            comb_filename = f"combined_{filename}"
            subprocess.run(f"ffmpeg -i {filename} -i {audio_filename} -c copy {comb_filename}")
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            if os.path.exists(comb_filename) and not os.path.exists(filename):
                filename = filename.replace("_", " ")
                os.rename(comb_filename, f"{downloads_path}{filename}")
            download_completed.configure(text=f"{filename}\nVideo Downloaded & Ready")
        else:
            if os.path.exists(filename):
                os.rename(filename, f"{downloads_path}{filename.replace('_', ' ')}")
            download_completed.configure(text=f"{filename.replace('_', ' ')}\nVideo Downloaded")
        reset_app()
    except Exception as e:
        if WindowsError:
            download_completed.configure(text=f"Error:: {e}\n\nIf regex_search: Try with full link/check link is complete\n\nIf WinError2: Filename already exists\n\nIf WinError 3: FFmpeg isn't setup right\n\nIf Else/Need Help\nContact TheeChody With Thee Error")
        else:
            download_completed.configure(text=f"Error downloading file\n\n{e}\n\nContact TheeChody with this error for more details")
        reset_app(True)
        return


def reset_app(error=False):
    if error:
        title.configure(text="Try Again with thee Full Link\nOr just 'v=characters' bit")
    else:
        title.configure(text="Enter New YouTube Link")
        link_box.delete(0, 'end')


app = customtkinter.CTk()
app.geometry("600x420")
app.title("Thee YouTube Downloader")

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

title = customtkinter.CTkLabel(app, text="Enter YouTube LInk")
title.pack(padx=10, pady=10)

dl_link = customtkinter.StringVar()
link_box = customtkinter.CTkEntry(app, width=550, height=35, textvariable=dl_link)
link_box.pack()

video_res = customtkinter.StringVar()
vid_res_list = customtkinter.CTkOptionMenu(app, values=video_list, variable=video_res)
vid_res_list.pack(padx=10, pady=10)

download_button = customtkinter.CTkButton(app, text="Download", command=start_download)
download_button.pack(padx=10, pady=10)

download_completed = customtkinter.CTkLabel(app, text="")
download_completed.pack(padx=20, pady=10)

app.mainloop()
