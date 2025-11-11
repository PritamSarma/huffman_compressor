import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from main import compress, decompress


class HuffmanGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("🗜️ Huffman File Compressor")
        self.geometry("700x500")
        self.minsize(600, 400)  # allow resize
        self.resizable(True, True)

        # --- Default theme ---
        self.theme = "dark"
        self.colors = {
            "dark": {"bg": "#1E1E1E", "fg": "white", "box": "#2D2D2D", "accent": "#007ACC"},
            "light": {"bg": "#F5F5F5", "fg": "#000000", "box": "#E6E6E6", "accent": "#0057B8"},
        }
        self.apply_theme()

        # --- Title Label ---
        self.title_label = tk.Label(
            self,
            text="🗜️ Huffman File Compressor",
            font=("Segoe UI", 18, "bold"),
            fg=self.colors[self.theme]["fg"],
            bg=self.colors[self.theme]["bg"],
        )
        self.title_label.pack(pady=20)

        # --- Drop Area ---
        self.drop_area = tk.Label(
            self,
            text="\n\nDrag & Drop your file here\n(.txt to compress or .huff to decompress)\n\n",
            relief="ridge",
            width=60,
            height=8,
            bg=self.colors[self.theme]["box"],
            fg=self.colors[self.theme]["fg"],
            font=("Segoe UI", 11),
        )
        self.drop_area.pack(pady=10, fill="x", padx=40, expand=False)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.on_drop)

        # --- Buttons ---
        btn_frame = tk.Frame(self, bg=self.colors[self.theme]["bg"])
        btn_frame.pack(pady=10)

        choose_btn = tk.Button(
            btn_frame,
            text="📂 Choose File",
            command=self.choose_file,
            bg=self.colors[self.theme]["accent"],
            fg="white",
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
            bg=self.colors[self.theme]["box"],
            fg=self.colors[self.theme]["fg"],
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
        )
        theme_btn.grid(row=0, column=1, padx=10)

        # --- Status Label ---
        self.status_label = tk.Label(
            self,
            text="Ready.",
            fg="lightgreen",
            bg=self.colors[self.theme]["bg"],
            font=("Consolas", 10),
        )
        self.status_label.pack(pady=10)

        # --- Result Frame ---
        self.result_frame = tk.Frame(self, bg=self.colors[self.theme]["bg"])
        self.result_frame.pack(fill="both", expand=True)

        self.result_text = tk.Label(
            self.result_frame,
            text="",
            justify="left",
            fg=self.colors[self.theme]["fg"],
            bg=self.colors[self.theme]["bg"],
            font=("Consolas", 11),
        )
        self.result_text.pack(pady=10)

        # --- Graph Area (matplotlib canvas) ---
        self.graph_canvas = None

    # -------------------
    # THEME MANAGEMENT
    # -------------------
    def apply_theme(self):
        c = self.colors[self.theme]
        self.configure(bg=c["bg"])
        if hasattr(self, "drop_area"):
            self.drop_area.configure(bg=c["box"], fg=c["fg"])
        if hasattr(self, "title_label"):
            self.title_label.configure(bg=c["bg"], fg=c["fg"])
        if hasattr(self, "status_label"):
            self.status_label.configure(bg=c["bg"], fg="lightgreen")
        if hasattr(self, "result_text"):
            self.result_text.configure(bg=c["bg"], fg=c["fg"])

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.status_label.config(text=f"Theme changed to {self.theme.capitalize()} Mode.")

    # -------------------
    # FILE HANDLING
    # -------------------
    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Text files", "*.txt"), ("Huffman files", "*.huff"), ("All files", "*.*")]
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

        # Clear previous result & chart
        self.result_text.config(text="")
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None

        if file_path.lower().endswith(".txt"):
            self.status_label.config(text="Compressing...")
            self.update_idletasks()
            try:
                output_path = compress(file_path)
                self.show_compression_info(file_path, output_path)
                self.status_label.config(text="✅ Compression complete.")
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")
        elif file_path.lower().endswith(".huff"):
            self.status_label.config(text="Decompressing...")
            self.update_idletasks()
            try:
                output_path = decompress(file_path)
                self.result_text.config(text=f"✅ Decompressed successfully!\nSaved to:\n{output_path}")
                self.status_label.config(text="✅ Decompression complete.")
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")
        else:
            self.status_label.config(text="⚠️ Unsupported file type.")

    # -------------------
    # DISPLAY COMPRESSION STATS + GRAPH
    # -------------------
    def show_compression_info(self, original_path, compressed_path):
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

        # --- Embed graph inside GUI ---
        self.show_compression_graph(original_size, compressed_size, ratio)

    def show_compression_graph(self, original_size, compressed_size, ratio):
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.bar(["Original", "Compressed"], [original_size, compressed_size], color=["#5B8BF7", "#F15A5A"])
        ax.set_ylabel("File Size (bytes)")
        ax.set_title(f"Compression Ratio: {ratio:.2f}% Saved")
        plt.tight_layout()

        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        self.graph_canvas.draw()
        widget = self.graph_canvas.get_tk_widget()
        widget.pack(pady=5)


if __name__ == "__main__":
    app = HuffmanGUI()
    app.mainloop()
