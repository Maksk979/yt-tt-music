@echo off
echo Building TT Music...
pip install pyinstaller
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "TT Music" ^
    --hidden-import yt_dlp ^
    --hidden-import PyQt6 ^
    --hidden-import static_ffmpeg ^
    --hidden-import static_ffmpeg.binaries ^
    --hidden-import imageio_ffmpeg ^
    main.py
echo Done! Exe is in dist\TT Music.exe
pause
