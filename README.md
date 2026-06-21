# YouTube Video Downloader

Interfaz local basica para descargar videos de YouTube con `yt-dlp`.

## Requisitos

- Python 3.10 o superior
- `ffmpeg` para convertir audio a MP3 y unir video y audio

## Instalacion

Instala la dependencia de Python:

```powershell
python -m pip install -r requirements.txt
```

Instala FFmpeg:

### Windows

Descargalo desde [ffmpeg.org](https://ffmpeg.org/download.html) y agrega la
carpeta que contiene `ffmpeg.exe` al `PATH`.

Si utilizas Chocolatey:

```powershell
choco install ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

Comprueba que FFmpeg esta disponible:

```powershell
ffmpeg -version
```

## Uso

```powershell
python app.py
```

Pega la URL, elige `Video + audio` o `Solo audio MP3`, selecciona una carpeta si no quieres usar `downloads/`, y pulsa `Descargar`.
Usa `Actualizar yt-dlp` para instalar la ultima version de `yt-dlp` desde la propia app.

El modo `Video + audio` intenta descargar MP4 con video H.264 y audio M4A/AAC cuando YouTube lo ofrece. Algunos archivos pueden no abrirse en el reproductor de Windows, aunque editores como CapCut si los acepten.

## Si YouTube da errores

YouTube cambia a menudo. Si una descarga falla, prueba primero a actualizar `yt-dlp`:

```powershell
python -m pip install -U yt-dlp
```
