import queue
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import BooleanVar, StringVar, Tk, filedialog, messagebox
from tkinter import ttk


APP_DIR = Path(__file__).resolve().parent
DEFAULT_DOWNLOAD_DIR = APP_DIR / "downloads"


class YoutubeDownloaderApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("720x500")
        self.root.minsize(640, 420)

        self.url_var = StringVar()
        self.output_dir_var = StringVar(value=str(DEFAULT_DOWNLOAD_DIR))
        self.mode_var = StringVar(value="video")
        self.status_var = StringVar(value="Listo")
        self.auto_open_var = BooleanVar(value=True)

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.current_process: subprocess.Popen[str] | None = None
        self.download_thread: threading.Thread | None = None

        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(5, weight=1)

        title = ttk.Label(main, text="Descargador de YouTube", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 14))

        url_frame = ttk.Frame(main)
        url_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        url_frame.columnconfigure(0, weight=1)

        ttk.Label(url_frame, text="URL del video").grid(row=0, column=0, sticky="w", pady=(0, 4))
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var)
        url_entry.grid(row=1, column=0, sticky="ew")
        url_entry.focus()

        options = ttk.Frame(main)
        options.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        options.columnconfigure(2, weight=1)

        ttk.Radiobutton(options, text="Video + audio", variable=self.mode_var, value="video").grid(
            row=0, column=0, sticky="w", padx=(0, 16)
        )
        ttk.Radiobutton(options, text="Solo audio MP3", variable=self.mode_var, value="audio").grid(
            row=0, column=1, sticky="w", padx=(0, 16)
        )
        ttk.Checkbutton(options, text="Abrir carpeta al terminar", variable=self.auto_open_var).grid(
            row=0, column=2, sticky="e"
        )

        output_frame = ttk.Frame(main)
        output_frame.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        output_frame.columnconfigure(0, weight=1)

        ttk.Label(output_frame, text="Carpeta de descarga").grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Entry(output_frame, textvariable=self.output_dir_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(output_frame, text="Elegir...", command=self._select_output_dir).grid(row=1, column=1, sticky="e")

        buttons = ttk.Frame(main)
        buttons.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        buttons.columnconfigure(2, weight=1)

        self.download_button = ttk.Button(buttons, text="Descargar", command=self._start_download)
        self.download_button.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.cancel_button = ttk.Button(buttons, text="Cancelar", command=self._cancel_download, state="disabled")
        self.cancel_button.grid(row=0, column=1, sticky="w")

        ttk.Label(buttons, textvariable=self.status_var).grid(row=0, column=2, sticky="e")

        log_frame = ttk.Frame(main)
        log_frame.grid(row=5, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = TextLog(log_frame)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def _select_output_dir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(APP_DIR))
        if selected:
            self.output_dir_var.set(selected)

    def _start_download(self) -> None:
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Falta la URL", "Pega la URL del video antes de descargar.")
            return

        output_dir = Path(self.output_dir_var.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        self._set_running(True)
        self.log_text.clear()
        self._log("Preparando descarga...")

        command = self._build_command(url, output_dir)
        self.download_thread = threading.Thread(target=self._run_download, args=(command, output_dir), daemon=True)
        self.download_thread.start()

    def _build_command(self, url: str, output_dir: Path) -> list[str]:
        output_template = str(output_dir / "%(title).200B.%(ext)s")
        base_command = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--newline",
            "--no-playlist",
            "--force-overwrites",
            "-o",
            output_template,
        ]

        if self.mode_var.get() == "audio":
            return [
                *base_command,
                "-x",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "0",
                url,
            ]

        return [
            *base_command,
            "-f",
            "bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a][acodec^=mp4a]/b[ext=mp4][vcodec^=avc1][acodec^=mp4a]",
            "--merge-output-format",
            "mp4",
            url,
        ]

    def _run_download(self, command: list[str], output_dir: Path) -> None:
        try:
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            assert self.current_process.stdout is not None
            for line in self.current_process.stdout:
                self._log(line.rstrip())

            exit_code = self.current_process.wait()
            if exit_code == 0:
                self._log("Descarga terminada.")
                self.root.after(0, self.status_var.set, "Completado")
                if self.auto_open_var.get():
                    self.root.after(0, lambda: self._open_output_dir(output_dir))
            else:
                self._log(f"yt-dlp terminó con código {exit_code}.")
                self.root.after(0, self.status_var.set, "Error")
        except FileNotFoundError:
            self._log("No se encontró yt-dlp. Instálalo con: pip install yt-dlp")
            self.root.after(0, self.status_var.set, "Falta yt-dlp")
        except Exception as exc:
            self._log(f"Error: {exc}")
            self.root.after(0, self.status_var.set, "Error")
        finally:
            self.current_process = None
            self.root.after(0, self._set_running, False)

    def _cancel_download(self) -> None:
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self._log("Cancelando descarga...")
            self.status_var.set("Cancelando")

    def _open_output_dir(self, output_dir: Path) -> None:
        subprocess.Popen(["explorer", str(output_dir)])

    def _set_running(self, running: bool) -> None:
        self.download_button.configure(state="disabled" if running else "normal")
        self.cancel_button.configure(state="normal" if running else "disabled")
        if running:
            self.status_var.set("Descargando")

    def _log(self, message: str) -> None:
        self.log_queue.put(message)

    def _poll_log_queue(self) -> None:
        while not self.log_queue.empty():
            self.log_text.append(self.log_queue.get_nowait())
        self.root.after(100, self._poll_log_queue)


class TextLog(ttk.Frame):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        import tkinter as tk

        self.text = tk.Text(self, wrap="word", height=12, state="disabled")
        self.text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

    def append(self, line: str) -> None:
        self.text.configure(state="normal")
        self.text.insert("end", line + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")


def main() -> None:
    root = Tk()
    ttk.Style().theme_use("clam")
    YoutubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
