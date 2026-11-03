from __future__ import annotations

import shutil
import subprocess
import sys
import threading
import zipfile
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "FLX Radio Importer"
MOD_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
SOURCE_DIR = MOD_ROOT / "My Tracks"
ARCHIVE_DIR = MOD_ROOT / "Imported Tracks Archive"
TARGET_DIR = MOD_ROOT / "gamedata" / "sounds" / "radio" / "_playlist_5"
TOOLS_DIR = MOD_ROOT / ".flx_tools"
SUPPORTED = {".ogg", ".mp3", ".wav", ".flac", ".m4a", ".aac", ".wma", ".opus"}


def find_ffmpeg() -> Path | None:
    candidates = [MOD_ROOT / "ffmpeg.exe", MOD_ROOT / "bin" / "ffmpeg.exe", TOOLS_DIR / "ffmpeg.exe"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    command = shutil.which("ffmpeg")
    if command:
        return Path(command)
    archives = sorted(MOD_ROOT.glob("ffmpeg*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if archives:
        TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archives[0]) as archive:
            member = next((name for name in archive.namelist() if name.lower().endswith("/bin/ffmpeg.exe") or name.lower() == "ffmpeg.exe"), None)
            if member:
                with archive.open(member) as source, (TOOLS_DIR / "ffmpeg.exe").open("wb") as target:
                    shutil.copyfileobj(source, target)
                return TOOLS_DIR / "ffmpeg.exe"
    return None


class Importer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("850x590")
        self.minsize(720, 480)
        self.option_add("*Font", ("Segoe UI", 10))
        self.files: list[Path] = []
        self.normalize = tk.BooleanVar(value=True)
        self.archive_sources = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Добавьте аудиофайлы или импортируйте папку My Tracks.")
        self._build()

    def _build(self):
        header = ttk.Frame(self, padding=14)
        header.pack(fill="x")
        ttk.Label(header, text="Импорт музыки в общий PDA-плейлист", font=("Segoe UI Semibold", 15)).pack(anchor="w")
        ttk.Label(header, text="Файлы будут преобразованы в совместимый OGG 44,1 кГц stereo и попадут в общий список радио.").pack(anchor="w", pady=(3, 0))

        buttons = ttk.Frame(self, padding=(14, 0))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Добавить файлы…", command=self.add_files).pack(side="left")
        ttk.Button(buttons, text="Добавить папку…", command=self.add_folder).pack(side="left", padx=8)
        ttk.Button(buttons, text="Взять My Tracks", command=self.add_my_tracks).pack(side="left")
        ttk.Button(buttons, text="Убрать из списка", command=self.remove_selected).pack(side="right")

        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(frame, selectmode="extended")
        scroll = ttk.Scrollbar(frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        options = ttk.Frame(self, padding=(14, 0, 14, 8))
        options.pack(fill="x")
        ttk.Checkbutton(options, text="Выровнять воспринимаемую громкость треков", variable=self.normalize).pack(side="left")
        ttk.Checkbutton(options, text="После импорта очистить My Tracks (исходники — в архив)", variable=self.archive_sources).pack(side="left", padx=(18, 0))
        ttk.Button(options, text="Очистить личную музыку…", command=self.clear_personal).pack(side="right")

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=14)
        footer = ttk.Frame(self, padding=14)
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status).pack(side="left", fill="x", expand=True)
        self.import_button = ttk.Button(footer, text="Импортировать", command=self.start_import)
        self.import_button.pack(side="right")

    def add_paths(self, paths):
        known = {p.resolve() for p in self.files}
        for raw in paths:
            path = Path(raw)
            if path.is_file() and path.suffix.lower() in SUPPORTED and path.resolve() not in known:
                self.files.append(path)
                known.add(path.resolve())
                self.listbox.insert("end", str(path))
        self.status.set(f"Выбрано треков: {len(self.files)}")

    def add_files(self):
        self.add_paths(filedialog.askopenfilenames(title="Выберите музыку", filetypes=[("Аудиофайлы", "*.ogg *.mp3 *.wav *.flac *.m4a *.aac *.wma *.opus"), ("Все файлы", "*.*")]))

    def add_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку с музыкой", initialdir=SOURCE_DIR)
        if folder:
            self.add_paths(sorted((p for p in Path(folder).rglob("*") if p.is_file()), key=lambda p: p.name.lower()))

    def add_my_tracks(self):
        SOURCE_DIR.mkdir(exist_ok=True)
        self.add_paths(sorted((p for p in SOURCE_DIR.iterdir() if p.is_file()), key=lambda p: p.name.lower()))

    def remove_selected(self):
        selected = set(self.listbox.curselection())
        self.files = [path for index, path in enumerate(self.files) if index not in selected]
        self.listbox.delete(0, "end")
        for path in self.files: self.listbox.insert("end", str(path))
        self.status.set(f"Выбрано треков: {len(self.files)}")

    def clear_personal(self):
        existing = list(TARGET_DIR.glob("*.ogg")) if TARGET_DIR.exists() else []
        if not existing:
            messagebox.showinfo(APP_TITLE, "Личная папка плейлиста уже пуста.")
            return
        if messagebox.askyesno(APP_TITLE, f"Удалить {len(existing)} треков из личной папки?\n\nМузыка из остальных папок GAMMA не пострадает."):
            for path in existing: path.unlink()
            self.status.set(f"Удалено личных треков: {len(existing)}")

    def start_import(self):
        if not self.files:
            messagebox.showwarning(APP_TITLE, "Сначала добавьте аудиофайлы.")
            return
        self.import_button.configure(state="disabled")
        self.progress.configure(maximum=len(self.files), value=0)
        normalize = self.normalize.get()
        archive_sources = self.archive_sources.get()
        threading.Thread(target=self._import, args=(normalize, archive_sources), daemon=True).start()

    def _import(self, normalize: bool, archive_sources: bool):
        try:
            ffmpeg = find_ffmpeg()
            if not ffmpeg:
                raise RuntimeError("FFmpeg не найден. Оставьте ffmpeg ZIP в папке мода или установите FFmpeg в Windows.")
            TARGET_DIR.mkdir(parents=True, exist_ok=True)
            highest = 0
            for path in TARGET_DIR.glob("flx_*.ogg"):
                try: highest = max(highest, int(path.stem.split("_")[1]))
                except (ValueError, IndexError): pass
            imported = 0
            imported_sources: list[Path] = []
            for index, source in enumerate(self.files, 1):
                highest += 1
                destination = TARGET_DIR / f"flx_{highest:04d}.ogg"
                filters = ["loudnorm=I=-16:TP=-1.5:LRA=11"] if normalize else []
                command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-vn"]
                if filters: command += ["-af", ",".join(filters)]
                command += ["-c:a", "libvorbis", "-q:a", "5", "-ar", "44100", "-ac", "2", str(destination)]
                result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if result.returncode != 0:
                    destination.unlink(missing_ok=True)
                    raise RuntimeError(f"Не удалось преобразовать «{source.name}»:\n{result.stderr.strip()}")
                imported += 1
                imported_sources.append(source)
                self.after(0, self._progress, index, source.name)
            archived = self._archive_my_tracks(imported_sources) if archive_sources else 0
            self.after(0, self._done, imported, archived)
        except Exception as exc:
            self.after(0, self._failed, str(exc))

    def _progress(self, value, name):
        self.progress.configure(value=value)
        self.status.set(f"Импортируется: {name}")

    def _archive_my_tracks(self, imported_sources: list[Path]) -> int:
        SOURCE_DIR.mkdir(exist_ok=True)
        source_root = SOURCE_DIR.resolve()
        candidates = []
        for path in imported_sources:
            try:
                path.resolve().relative_to(source_root)
                candidates.append(path)
            except ValueError:
                pass
        if not candidates:
            return 0
        destination = ARCHIVE_DIR / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        destination.mkdir(parents=True, exist_ok=False)
        moved = 0
        for source in candidates:
            if source.exists():
                target = destination / source.name
                suffix = 2
                while target.exists():
                    target = destination / f"{source.stem}_{suffix}{source.suffix}"
                    suffix += 1
                shutil.move(str(source), str(target))
                moved += 1
        return moved

    def _done(self, count, archived):
        self.import_button.configure(state="normal")
        self.status.set(f"Готово. Импортировано: {count}; убрано из My Tracks: {archived}")
        self.files = [path for path in self.files if path.exists()]
        self.listbox.delete(0, "end")
        for path in self.files: self.listbox.insert("end", str(path))
        archive_note = f"\nИсходники из My Tracks перемещены в архив: {archived}." if archived else ""
        messagebox.showinfo(APP_TITLE, f"Импортировано треков: {count}.{archive_note}\n\nПорядок уже импортированной музыки сохранён. Новые треки добавлены в конец.")

    def _failed(self, error):
        self.import_button.configure(state="normal")
        self.status.set("Импорт остановлен из-за ошибки.")
        messagebox.showerror(APP_TITLE, error)


if __name__ == "__main__":
    Importer().mainloop()
