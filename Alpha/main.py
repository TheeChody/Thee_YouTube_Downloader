import os
import sys
import threading
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
ffmpeg_path = f"{Path(__file__).parent.absolute()}/ffmpeg/"
dl_audio_path = f"{downloads_path}Audio/"
dl_video_path = f"{downloads_path}Video/"
Path(dl_audio_path).mkdir(parents=True, exist_ok=True)
Path(dl_video_path).mkdir(parents=True, exist_ok=True)
Path(f"{Path(__file__).parent.absolute()}/pytube/__cache__").mkdir(parents=True, exist_ok=True)


def keep_audio_box_state(value: str):
    if value == "Audio Only":
        keep_audio_box.deselect()
        keep_audio_box.configure(state=customtkinter.DISABLED)
    else:
        keep_audio_box.configure(state=customtkinter.NORMAL)


def local_ffmpeg(relative_path: str):
    try:
        return os.path.join(ffmpeg_path, relative_path)
    except Exception as e:
        download_completed.configure(text=f"Error pathing out resources\n\n{e}\n\n{ffmpeg_path}{relative_path}")
        return None


def progress_update(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    perc_completion = bytes_downloaded / total_size * 100
    progress_bar.set(float(perc_completion) / 100)


def reset_app(error: bool = False):
    state_change(True)
    if error:
        title.configure(text="Try Again with thee Full Link\nOr just 'v=characters' bit")
    else:
        title.configure(text="Enter New YouTube Link")
        link_box.delete(0, 'end')


def state_change(normal: bool):
    if normal:
        state = customtkinter.NORMAL
    else:
        state = customtkinter.DISABLED
    link_box.configure(state=state)
    vid_res_list.configure(state=state)
    keep_audio_box.configure(state=state)
    download_button.configure(state=state)


def start_download():
    try:
        state_change(False)
        if dl_link.get() == "":
            download_completed.configure(text=f"URL Field Is Blank")
            reset_app(True)
            return
        elif video_res.get() == "":
            download_completed.configure(text=f"Please choose one of thee following via Drop-Down Menu\n{', '.join(video_list)}")
            reset_app(True)
            return
        progress_bar.set(0)
        download_completed.configure(text="")
        title.configure(text="Processing Request")
        hd_res, audio_only, new_filename = False, False, ""
        youtube_object = YouTube(dl_link.get(), use_oauth=True, allow_oauth_cache=True, on_progress_callback=progress_update)
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
        elif video_res.get() == "720p":
            download = youtube_object.streams.get_highest_resolution()
        elif video_res.get() == "Lowest Res":
            download = youtube_object.streams.get_lowest_resolution()
        else:
            download_completed.configure(text=f"Something went wrong selecting video resolution, let TheeChody know please and thank you\n\nValue of video_res:: '{video_res.get()}'")
            reset_app(True)
            return
        filename = f"{youtube_object.author}_-_{youtube_object.title}.mp4"
        for letter in filename:
            if letter in illegal_chars:
                letter = "X"
            elif letter == " ":
                letter = "_"
            new_filename += letter
        filename = new_filename
        download.download(filename=filename)
        if audio_only:
            download_completed.configure(text=f"Downloaded {filename}\nConverting to .mp3")
            audio_filename = f"{filename[:-4]}.mp3"
            subprocess.run(local_ffmpeg(f"ffmpeg -i {filename} {audio_filename}"))
            download_completed.configure(text="Finished Audio Conversion\nCleaning Up/Renaming Remaining Files")
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(audio_filename):
                os.rename(audio_filename, f"{dl_audio_path}{audio_filename.replace('_', ' ')}")
            download_completed.configure(text=f"{audio_filename[:-4].replace('_', ' ')}\nAudio Downloaded")
        elif hd_res:
            download_completed.configure(text=f"Downloaded {filename}\nStarting on audio track")
            progress_bar.set(0)
            audio_filename = f"audio_{filename}"
            comb_filename = f"combined_{filename}"
            youtube_object.streams.get_audio_only().download(filename=audio_filename)
            download_completed.configure(text=f"Downloaded {audio_filename}\nStarting Video Combination Process")
            subprocess.run(local_ffmpeg(f"ffmpeg -i {filename} -i {audio_filename} -c copy {comb_filename}"))
            download_completed.configure(text=f"Finished Video Combination\n{'Starting Audio Conversion' if keep_audio.get() else 'Cleaning Up/Renaming Files'}")
            if os.path.exists(filename):
                os.remove(filename)
            if keep_audio.get():
                new_audio_filename = f"{filename[:-4]}.mp3"
                subprocess.run(local_ffmpeg(f"ffmpeg -i {audio_filename} {new_audio_filename}"))
                download_completed.configure(text=f"Finished Audio Conversion\nCleaning Up/Renaming Remaining Files")
                os.rename(new_audio_filename, f"{dl_audio_path}{new_audio_filename.replace('_', ' ')}")
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            if os.path.exists(comb_filename):
                filename = filename.replace("_", " ")
                os.rename(comb_filename, f"{dl_video_path}{filename}")
            download_completed.configure(text=f"{filename[:-4]}\n{'Audio & ' if keep_audio.get() else ''}Video Downloaded & Ready")
        else:
            if keep_audio.get():
                download_completed.configure(text=f"Downloaded {filename}\nConverting to .mp3")
                audio_filename = f"{filename[:-4]}.mp3"
                subprocess.run(local_ffmpeg(f"ffmpeg -i {filename} {audio_filename}"))
                download_completed.configure(text="Finished Audio Conversion\nCleaning Up/Renaming Remaining Files")
                if os.path.exists(audio_filename):
                    os.rename(audio_filename, f"{dl_audio_path}{audio_filename.replace('_', ' ')}")
            if os.path.exists(filename):
                os.rename(filename, f"{dl_video_path}{filename.replace('_', ' ')}")
            download_completed.configure(text=f"{filename[:-4].replace('_', ' ')}\n{'Audio & ' if keep_audio.get() else ''}Video Downloaded")
        reset_app()
    except Exception as e:
        if WindowsError:
            download_completed.configure(text=f"Error\n{e}\n\n\nIf regex_search: Try with full link/check link is complete\n\nIf WinError2: FFmpeg isn't setup right\n\nIf WinError 3: Filename already exists\n\nIf Else/Need Help\nContact TheeChody With Thee Error")
        else:
            download_completed.configure(text=f"Error downloading file\n\n{e}\n\nContact TheeChody with this error for more details")
        reset_app(True)
        return


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

progress_bar = customtkinter.CTkProgressBar(app, width=550)
progress_bar.set(0)
progress_bar.pack(padx=10, pady=10)

video_res = customtkinter.StringVar()
vid_res_list = customtkinter.CTkOptionMenu(app, values=video_list, variable=video_res, command=keep_audio_box_state)
vid_res_list.pack(padx=10, pady=10)

download_button = customtkinter.CTkButton(app, text="Download", command=lambda: threading.Thread(target=start_download).start())
download_button.pack(padx=10, pady=10)

keep_audio = customtkinter.BooleanVar()
keep_audio_box = customtkinter.CTkCheckBox(app, text="Keep Separate Audio File", offvalue=False, onvalue=True, variable=keep_audio)
keep_audio_box.pack(padx=5, pady=10)

download_completed = customtkinter.CTkLabel(app, text="")
download_completed.pack(padx=20, pady=10)

app.mainloop()
