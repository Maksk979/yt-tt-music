@echo off
echo Building TT Music...
pip install pyinstaller
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "TT Music" ^
    --icon=assets/icon.ico ^
    --hidden-import yt_dlp ^
    --hidden-import PyQt6 ^
    --hidden-import imageio_ffmpeg ^
    main.py
echo Done! Exe is in dist\TT Music.exe
pause
