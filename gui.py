import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from main import compress, decompress


class HuffmanGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("🗜️ Huffman File Compressor")
        self.geometry("700x540")
        self.minsize(600, 440)
        self.resizable(True, True)

        # Exit cleanup so terminal becomes free after close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- State variables ---
        self.graph_canvas = None
        self.result_frame = None
        self.result_text = None
        self.progress_bar = None
        self.last_graph_data = None  # stores last chart for redrawing on theme switch

        # --- Theme setup ---
        self.theme = "dark"
        self.colors = {
            "dark": {
                "bg": "#1E1E1E",
                "fg": "white",
                "box": "#2D2D2D",
                "accent": "#007ACC",
                "plot_bg": "#1E1E1E",
            },
            "light": {
                "bg": "#F5F5F5",
                "fg": "#000000",
                "box": "#E6E6E6",
                "accent": "#0057B8",
                "plot_bg": "#FFFFFF",
            },
        }

        # --- Build GUI ---
        self.title_label = tk.Label(
            self,
            text="🗜️ Huffman File Compressor",
            font=("Segoe UI", 18, "bold"),
        )
        self.title_label.pack(pady=20)

        self.drop_area = tk.Label(
            self,
            text="\n\nDrag & Drop your file here\n(.txt to compress or .huff to decompress)\n\n",
            relief="ridge",
            width=60,
            height=8,
            font=("Segoe UI", 11),
        )
        self.drop_area.pack(pady=10, fill="x", padx=40, expand=False)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.on_drop)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        choose_btn = tk.Button(
            btn_frame,
            text="📂 Choose File",
            command=self.choose_file,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
        )
        choose_btn.grid(row=0, column=0, padx=10)

        theme_btn = tk.Button(
            btn_frame,
            text="🌙 Toggle Theme",
            command=self.toggle_theme,
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
        )
        theme_btn.grid(row=0, column=1, padx=10)

        # Status label
        self.status_label = tk.Label(self, text="Ready.", font=("Consolas", 10))
        self.status_label.pack(pady=(10, 0))

        # Progress bar (real progress — fills left to right)
        self.progress_bar = ttk.Progressbar(
            self,
            orient="horizontal",
            mode="determinate",
            length=400,
        )
        self.progress_bar.pack(pady=(5, 15))
        self.progress_bar["maximum"] = 100
        self.progress_bar["value"] = 0

        # Result section
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(fill="both", expand=True)

        self.result_text = tk.Label(
            self.result_frame,
            text="",
            justify="left",
            font=("Consolas", 11),
        )
        self.result_text.pack(pady=10)

        # Apply theme after everything exists
        self.apply_theme()

    # -------------------
    # THEME MANAGEMENT
    # -------------------
    def apply_theme(self):
        c = self.colors[self.theme]
        self.configure(bg=c["bg"])
        self.title_label.configure(bg=c["bg"], fg=c["fg"])
        self.drop_area.configure(bg=c["box"], fg=c["fg"])
        self.status_label.configure(bg=c["bg"], fg="lightgreen")
        self.result_frame.configure(bg=c["bg"])
        self.result_text.configure(bg=c["bg"], fg=c["fg"])

        if self.graph_canvas:
            self.redraw_graph()  # refresh chart with new colors

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.status_label.config(
            text=f"Theme changed to {self.theme.capitalize()} Mode."
        )

    # -------------------
    # FILE HANDLING
    # -------------------
    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Huffman files", "*.huff"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.handle_file(file_path)

    def on_drop(self, event):
        file_path = event.data.strip("{}")
        self.handle_file(file_path)

    def handle_file(self, file_path):
        if not os.path.exists(file_path):
            self.status_label.config(text="❌ File not found.")
            return

        # Clear previous output
        self.result_text.config(text="")
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None
        self.progress_bar["value"] = 0
        self.last_graph_data = None

        # Determine mode
        if file_path.lower().endswith(".txt"):
            self.compress_file(file_path)
        elif file_path.lower().endswith(".huff"):
            self.decompress_file(file_path)
        else:
            self.status_label.config(text="⚠️ Unsupported file type.")

    # -------------------
    # TASKS WITH REAL PROGRESS
    # -------------------
    def compress_file(self, file_path):
        """Compress file with live progress tracking"""
        try:
            self.status_label.config(text="Compressing...")
            self.progress_bar["value"] = 0

            def update_progress(value):
                """Update bar during compression"""
                self.progress_bar["value"] = value
                self.update_idletasks()

            output_path = compress(file_path, progress_callback=update_progress)
            self.show_compression_info(file_path, output_path)
            self.progress_bar["value"] = 100
            self.status_label.config(text="✅ Compression complete.")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            self.progress_bar["value"] = 0

    def decompress_file(self, file_path):
        """Decompress file with live progress tracking"""
        try:
            self.status_label.config(text="Decompressing...")
            self.progress_bar["value"] = 0

            def update_progress(value):
                """Update bar during decompression"""
                self.progress_bar["value"] = value
                self.update_idletasks()

            output_path = decompress(file_path, progress_callback=update_progress)
            self.result_text.config(
                text=f"✅ Decompressed successfully!\nSaved to:\n{output_path}"
            )
            self.progress_bar["value"] = 100
            self.status_label.config(text="✅ Decompression complete.")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            self.progress_bar["value"] = 0

    # -------------------
    # GRAPH + INFO DISPLAY
    # -------------------
    def show_compression_info(self, original_path, compressed_path):
        """Display compression stats + store graph data"""
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)
        ratio = (1 - compressed_size / original_size) * 100

        info = (
            f"✅ Compression complete\n"
            f"Original: {original_size / 1024:.2f} KB\n"
            f"Compressed: {compressed_size / 1024:.2f} KB\n"
            f"Saved: {ratio:.2f}%\n\nOutput File:\n{compressed_path}"
        )
        self.result_text.config(text=info)
        self.last_graph_data = (original_size, compressed_size, ratio)
        self.redraw_graph()

    def redraw_graph(self):
        """Draw or refresh chart"""
        if not self.last_graph_data:
            return

        original_size, compressed_size, ratio = self.last_graph_data
        colors = self.colors[self.theme]

        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
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
        widget.pack(pady=5)

    # -------------------
    # CLEAN EXIT
    # -------------------
    def on_close(self):
        """Close app and restore terminal"""
        try:
            self.destroy()
            self.quit()
        finally:
            os._exit(0)


if __name__ == "__main__":
    app = HuffmanGUI()
    app.mainloop()
