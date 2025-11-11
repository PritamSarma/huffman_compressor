# gui.py
import os
import time
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from main import compress, decompress

class HuffmanGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Window
        self.title("🗜️ Huffman File Compressor")
        self.geometry("820x640")
        self.minsize(720, 520)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # State
        self.graph_canvas = None
        self.last_graph_data = None
        self._progress_start_time = None
        self._progress_total_size = None

        # Theme
        self.theme = "dark"
        self.colors = {
            "dark": {"bg": "#1E1E1E", "fg": "white", "box": "#2D2D2D", "accent": "#007ACC", "plot_bg": "#1E1E1E"},
            "light": {"bg": "#F5F5F5", "fg": "#000000", "box": "#E6E6E6", "accent": "#0057B8", "plot_bg": "#FFFFFF"},
        }

        # Header
        self.title_label = tk.Label(self, text="🗜️ Huffman File Compressor", font=("Segoe UI", 18, "bold"))
        self.title_label.pack(pady=16)

        # Drop area
        self.drop_area = tk.Label(self,
                                  text="\n\nDrag & Drop your file here\n(.txt/.png/.zip/.pdf etc.)\n\n",
                                  relief="ridge", width=80, height=8, font=("Segoe UI", 11))
        self.drop_area.pack(pady=8, fill="x", padx=40)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.on_drop)

        # Buttons + output folder
        top_frame = tk.Frame(self)
        top_frame.pack(pady=8)

        choose_btn = tk.Button(top_frame, text="📂 Choose File", command=self.choose_file, font=("Segoe UI", 10, "bold"),
                               relief="flat", padx=14, pady=6, cursor="hand2")
        choose_btn.grid(row=0, column=0, padx=8)

        theme_btn = tk.Button(top_frame, text="🌙 Toggle Theme", command=self.toggle_theme, font=("Segoe UI", 10),
                              relief="flat", padx=10, pady=6, cursor="hand2")
        theme_btn.grid(row=0, column=1, padx=8)

        out_btn = tk.Button(top_frame, text="📁 Choose Output Folder", command=self.choose_output_folder,
                            font=("Segoe UI", 10), relief="flat", padx=10, pady=6, cursor="hand2")
        out_btn.grid(row=0, column=2, padx=8)

        self.output_dir_var = tk.StringVar(value="output")
        self.output_label = tk.Label(top_frame, text=self.output_dir_var.get(), font=("Consolas", 9), anchor="w")
        self.output_label.grid(row=0, column=3, padx=(8,0))

        # Status
        self.status_label = tk.Label(self, text="Ready.", font=("Consolas", 10))
        self.status_label.pack(pady=(8, 4))

        # Progress + ETA
        prog_frame = tk.Frame(self)
        prog_frame.pack(pady=(4, 10))

        self.progress_bar = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate", length=560)
        self.progress_bar.grid(row=0, column=0, padx=8, pady=2)

        info_frame = tk.Frame(prog_frame)
        info_frame.grid(row=0, column=1, padx=(10,0), sticky="n")

        self.speed_label = tk.Label(info_frame, text="Speed: - KB/s", font=("Consolas", 9))
        self.speed_label.pack(anchor="w")
        self.eta_label = tk.Label(info_frame, text="ETA: --:--", font=("Consolas", 9))
        self.eta_label.pack(anchor="w")

        self.progress_bar["maximum"] = 100
        self.progress_bar["value"] = 0

        # Result & graph area
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(fill="both", expand=True, padx=8, pady=6)

        self.result_text = tk.Label(self.result_frame, text="", justify="left", font=("Consolas", 11))
        self.result_text.pack(pady=8)

        self.apply_theme()

    # Theme
    def apply_theme(self):
        c = self.colors[self.theme]
        self.configure(bg=c["bg"])
        self.title_label.configure(bg=c["bg"], fg=c["fg"])
        self.drop_area.configure(bg=c["box"], fg=c["fg"])
        self.status_label.configure(bg=c["bg"], fg="lightgreen")
        self.result_frame.configure(bg=c["bg"])
        self.result_text.configure(bg=c["bg"], fg=c["fg"])
        self.output_label.configure(bg=c["bg"], fg=c["fg"])
        self.speed_label.configure(bg=c["bg"], fg=c["fg"])
        self.eta_label.configure(bg=c["bg"], fg=c["fg"])
        if self.graph_canvas:
            self.redraw_graph()

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.status_label.config(text=f"Theme changed to {self.theme.capitalize()} Mode.")

    # File selection
    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[("All files","*.*")])
        if file_path:
            self.handle_file(file_path)

    def on_drop(self, event):
        file_path = event.data.strip("{}")
        self.handle_file(file_path)

    # Output folder chooser
    def choose_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir_var.set(folder)
            self.output_label.config(text=folder)
            self.status_label.config(text=f"Output folder set to: {folder}")

    # Handle file
    def handle_file(self, file_path):
        if not os.path.exists(file_path):
            self.status_label.config(text="❌ File not found.")
            return

        # reset ui
        self.result_text.config(text="")
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None
        self.progress_bar["value"] = 0
        self.speed_label.config(text="Speed: - KB/s")
        self.eta_label.config(text="ETA: --:--")
        self.last_graph_data = None
        self._progress_start_time = None
        self._progress_total_size = None

        out_dir = self.output_dir_var.get() or "output"
        os.makedirs(out_dir, exist_ok=True)

        if file_path.lower().endswith(".huff"):
            # decompression
            total = os.path.getsize(file_path)
            self._progress_total_size = total
            self.decompress_file(file_path, out_dir)
        else:
            # compression (handle any file type)
            total = os.path.getsize(file_path)
            self._progress_total_size = total
            self.compress_file(file_path, out_dir)

    # Progress helpers
    def _start_progress_timer(self):
        self._progress_start_time = time.time()

    def _update_progress_ui(self, percent):
        if self._progress_start_time is None:
            self._start_progress_timer()

        p = max(0.0, min(100.0, float(percent)))
        self.progress_bar["value"] = p
        self.update_idletasks()

        total = self._progress_total_size or 0
        elapsed = time.time() - self._progress_start_time
        processed = (p / 100.0) * total

        speed_bps = processed / elapsed if elapsed > 0 else 0.0
        speed_kbps = speed_bps / 1024.0
        remaining = max(0.0, total - processed)
        eta_seconds = remaining / speed_bps if speed_bps > 0 else None

        if speed_kbps > 0:
            self.speed_label.config(text=f"Speed: {speed_kbps:0.2f} KB/s")
        else:
            self.speed_label.config(text="Speed: - KB/s")

        if eta_seconds is None:
            self.eta_label.config(text="ETA: --:--")
        else:
            eta = int(eta_seconds)
            h = eta // 3600
            m = (eta % 3600) // 60
            s = eta % 60
            if h > 0:
                self.eta_label.config(text=f"ETA: {h:d}:{m:02d}:{s:02d}")
            else:
                self.eta_label.config(text=f"ETA: {m:02d}:{s:02d}")

    # Tasks
    def compress_file(self, file_path, out_dir):
        try:
            self.status_label.config(text="Compressing...")
            self.progress_bar["value"] = 0
            self._start_progress_time = None  # for consistency

            def update_progress(v):
                self._update_progress_ui(v)

            out_path = compress(file_path, output_dir=out_dir, progress_callback=update_progress)
            # ensure 100
            self._update_progress_ui(100.0)
            self.show_compression_info(file_path, out_path)
            self.status_label.config(text="✅ Compression complete.")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            self.progress_bar["value"] = 0

    def decompress_file(self, file_path, out_dir):
        try:
            self.status_label.config(text="Decompressing...")
            self.progress_bar["value"] = 0

            def update_progress(v):
                self._update_progress_ui(v)

            out_path = decompress(file_path, output_dir=out_dir, progress_callback=update_progress)
            self._update_progress_ui(100.0)
            self.result_text.config(text=f"✅ Decompressed successfully!\nSaved to:\n{out_path}")
            self.status_label.config(text="✅ Decompression complete.")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            self.progress_bar["value"] = 0

    # Graph & info
    def show_compression_info(self, original_path, compressed_path):
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0.0

        info = (f"✅ Compression complete\n"
                f"Original: {original_size / 1024:.2f} KB\n"
                f"Compressed: {compressed_size / 1024:.2f} KB\n"
                f"Saved: {ratio:.2f}%\n\nOutput File:\n{compressed_path}")
        self.result_text.config(text=info)
        self.last_graph_data = (original_size, compressed_size, ratio)
        self.redraw_graph()

    def redraw_graph(self):
        if not self.last_graph_data:
            return

        original_size, compressed_size, ratio = self.last_graph_data
        colors = self.colors[self.theme]

        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None

        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=100)
        ax.bar(["Original", "Compressed"], [original_size, compressed_size],
               color=["#5B8BF7", "#F15A5A"])
        ax.set_ylabel("File Size (bytes)", color=colors["fg"])
        ax.set_title(f"Compression Ratio: {ratio:.2f}% Saved", color=colors["fg"])
        fig.patch.set_facecolor(colors["plot_bg"])
        ax.set_facecolor(colors["plot_bg"])
        ax.tick_params(colors=colors["fg"])
        for spine in ax.spines.values():
            spine.set_color(colors["fg"])
        plt.tight_layout()

        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        self.graph_canvas.draw()
        widget = self.graph_canvas.get_tk_widget()
        widget.configure(bg=colors["bg"], highlightthickness=0)
        widget.pack(pady=6)

    # Close
    def on_close(self):
        try:
            self.destroy()
            self.quit()
        finally:
            os._exit(0)


if __name__ == "__main__":
    app = HuffmanGUI()
    app.mainloop()
