# TT Music

Приложение для извлечения аудио из видео.

## Возможности

- Извлечение звука из локальных видеофайлов (mp4, mkv, avi, mov, webm)
- Скачивание аудио по ссылкам YouTube и TikTok
- Выходной формат: MP3, 192 kbps
- Выбор браузера для куков (Chrome, Brave, Edge, Firefox, Opera)
- Импорт cookie-файла для обхода ограничений

## Установка

### Из exe

Скачай последний релиз: [GitHub Releases](https://github.com/Maksk979/yt-tt-music/releases/latest)

### Из исходников

```bash
git clone https://github.com/Maksk979/yt-tt-music.git
cd tt-music
pip install -r requirements.txt
python main.py
```

## Сборка exe

```bash
build.bat
```

Готовый файл будет в `dist/TT Music.exe`.

## Куки

Для скачивания видео с YouTube/TikTok нужен cookie-файл.

1. Установи расширение "Get cookies.txt LOCALLY" в браузере
2. Зайди на YouTube и залогинься
3. Нажми на расширение → Export → сохрани файл
4. В приложении загрузи этот файл через кнопку "Обзор"

Куки работают примерно 2-4 недели, потом нужно обновить.

## Используемые технологии

- Python 3.10+
- PyQt6
- yt-dlp
- FFmpeg (через imageio-ffmpeg)
