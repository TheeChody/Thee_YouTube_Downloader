import os
import subprocess
import customtkinter
from pathlib import Path
from pytube import YouTube

folder_path = Path(__file__).parent.absolute()
video_list = ["Audio Only", "1080p", "720p", "Lowest Res"]
Path(f"{folder_path}/pytube/__cache__").mkdir(parents=True, exist_ok=True)
illegal_chars = ("#", "%", "&", "{", "}", "\\", "<", ">", "*", "?", "/", "$", "!", "'", '"', ":", "@", "+", "`", "|", "=")


def start_download():
    try:
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
        filename = f"{youtube_object.author}--{youtube_object.title}{'.mp3' if audio_only else '.mp4'}"
        for letter in filename:
            if letter in illegal_chars:
                letter = "X"
            elif letter == " ":
                letter = "_"
            new_filename += letter
        filename = new_filename
        download.download(filename=filename)
        if hd_res:
            audio_filename = filename[:-4] + ".mp3"
            audio_download.download(filename=audio_filename)
            comb_filename = f"combined_{filename}"
            subprocess.run(f"ffmpeg -i {filename} -i {audio_filename} -c copy {comb_filename}")
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            if os.path.exists(comb_filename) and not os.path.exists(filename):
                os.rename(comb_filename, filename)
            download_completed.configure(text=f"{filename}\nDownloaded & Ready")
        else:
            download_completed.configure(text=f"{filename}\n{'Audio' if audio_only else 'Video'} Downloaded")
        reset_app()
    except Exception as e:
        if WindowsError:
            download_completed.configure(text=f"Error Combining Video with Audio\nAre you sure you have FFmpeg installed and path set correctly?\nIf so, contact TheeChody\n\n{e}")
            reset_app(True)
        else:
            download_completed.configure(text=f"Error downloading file\n\n{e}\n\nContact TheeChody for more details")
            reset_app(True)
        return


def reset_app(error=False):
    if error:
        title.configure(text="Try Again with thee Full Link\nOr just 'v=characters' bit")
    else:
        title.configure(text="Enter New YouTube Link")
        link_box.delete(0, 'end')


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

app = customtkinter.CTk()
app.geometry("700x450")
app.title("Thee YT Downloader")

title = customtkinter.CTkLabel(app, text="Enter YouTube LInk")
title.pack(padx=10, pady=10)

dl_link = customtkinter.StringVar()
link_box = customtkinter.CTkEntry(app, width=600, height=30, textvariable=dl_link)
link_box.pack()

video_res = customtkinter.StringVar()
vid_res_list = customtkinter.CTkOptionMenu(app, values=video_list, variable=video_res, )
vid_res_list.pack(padx=10, pady=10)

download_button = customtkinter.CTkButton(app, text="Download", command=start_download)
download_button.pack(padx=10, pady=10)

download_completed = customtkinter.CTkLabel(app, text="")
download_completed.pack(padx=10, pady=10)

app.mainloop()
