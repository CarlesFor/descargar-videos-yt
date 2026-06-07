# YouTube Video Downloader

Interfaz local basica para descargar videos de YouTube con `yt-dlp`.

## Requisitos

- Python 3.10 o superior
- `yt-dlp`
- `ffmpeg` para convertir audio a MP3 y unir video + audio

Instalacion de dependencias Python:

```powershell
pip install -r requirements.txt
```

## Uso

```powershell
python app.py
```

Pega la URL, elige `Video + audio` o `Solo audio MP3`, selecciona una carpeta si no quieres usar `downloads/`, y pulsa `Descargar`.

El modo `Video + audio` intenta descargar MP4 con video H.264 y audio M4A/AAC cuando YouTube lo ofrece. Algunos archivos pueden no abrirse en el reproductor de Windows, aunque editores como CapCut si los acepten.

## Si YouTube da errores

YouTube cambia a menudo. Si una descarga falla, prueba primero a actualizar `yt-dlp`:

```powershell
python -m pip install -U yt-dlp
```
