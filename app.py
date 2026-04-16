import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
import threading
import os

class VideoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎥 Kompres Video Cepat")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        # Variabel
        self.input_path = tk.StringVar()
        self.target_size = tk.StringVar(value="10")  # default 10 MB

        # UI
        self.create_widgets()

    def create_widgets(self):
        # Judul
        title = tk.Label(self.root, text="Kompres Video dengan Python", font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Pilih file
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=5)
        tk.Label(frame1, text="File Video:").pack(side=tk.LEFT)
        tk.Entry(frame1, textvariable=self.input_path, width=40, state='readonly').pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="Pilih", command=self.select_file).pack(side=tk.LEFT)

        # Ukuran target
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10)
        tk.Label(frame2, text="Target Ukuran (MB):").pack(side=tk.LEFT)
        tk.Entry(frame2, textvariable=self.target_size, width=10).pack(side=tk.LEFT, padx=5)

        # Tombol kompres
        self.compress_btn = tk.Button(self.root, text="Kompres Video", command=self.start_compress, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.compress_btn.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill='x')

        # Status
        self.status_label = tk.Label(self.root, text="Siap", fg="gray")
        self.status_label.pack()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv")]
        )
        if file_path:
            self.input_path.set(file_path)

    def start_compress(self):
        input_file = self.input_path.get()
        if not input_file or not os.path.isfile(input_file):
            messagebox.showerror("Error", "Silakan pilih file video yang valid!")
            return

        try:
            target_mb = int(self.target_size.get())
            if target_mb <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ukuran target harus berupa angka positif (dalam MB)!")
            return

        # Jalankan kompresi di thread terpisah agar GUI tidak freeze
        threading.Thread(target=self.compress_video, args=(input_file, target_mb), daemon=True).start()

    def compress_video(self, input_path, target_mb):
        self.root.after(0, lambda: self.compress_btn.config(state='disabled'))
        self.root.after(0, lambda: self.status_label.config(text="Sedang mengompres..."))
        self.progress.start()

        try:
            clip = VideoFileClip(input_path)
            duration = clip.duration
            if duration <= 0:
                raise ValueError("Durasi video tidak valid.")

            # Hitung bitrate
            target_bitrate = (target_mb * 8192) / duration  # dalam kbps
            if target_bitrate < 50:
                target_bitrate = 50

            # Nama output
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_compressed{ext}"

            # Kompres
            clip.write_videofile(
                output_path,
                bitrate=f"{int(target_bitrate)}k",
                audio_bitrate="32k",
                codec="libx264",
                preset="fast",
                threads=4,
                logger=None  # nonaktifkan log moviepy di GUI
            )
            clip.close()

            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            msg = f"✅ Selesai!\nFile disimpan di:\n{output_path}\nUkuran akhir: {final_size_mb:.1f} MB"
            self.root.after(0, lambda: messagebox.showinfo("Sukses", msg))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal mengompres video:\n{str(e)}"))

        finally:
            self.root.after(0, lambda: self.compress_btn.config(state='normal'))
            self.root.after(0, lambda: self.status_label.config(text="Selesai"))
            self.root.after(0, self.progress.stop)

# Jalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCompressorApp(root)
    root.mainloop()