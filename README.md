Anyone download YouTube videos on thee regular? I used to, still do occasionally, and was sick and tired of them sketchy websites, so I made my own local app. Figured I'd share if anyone is interested. 

One pre-requisite for my app though(ONLY if you want Audio Only or 1080p videos, as Audio Only needs mp3 conversion from mp4a for compatibility via FFMPEG and 1080p videos do not come with audio, so there is a process involved to download 1080p video and audio track separately and merge them with FFMPEG), is FFMPEG (Link here, how to download/install/set winPath( https://www.wikihow.com/Install-FFmpeg-on-Windows ))

Once done with that, just extract thee zip folder, and run thee .exe, input thee YouTube link, select res/audio only and hit download. program will ask you to login via Google's auth page ( https://google.com/device ) in the open command prompt window and that is for age gated videos. should only need to login once, and a token will be generated locally ( _internal/pytube/--cache-- (underscores, not dashes, text box don't like underscores)). thee program will "not respond" while downloading, so based on your internet speeds, just be patient

if anyone has any questions, comments or concerns, don't hesitate to reach out.
Much Love
