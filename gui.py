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
        self.minsize(600, 400)
        self.resizable(True, True)

        # --- Predefine GUI variables to avoid attribute errors ---
        self.graph_canvas = None
        self.result_frame = None
        self.result_text = None

        # --- Default theme ---
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

        # --- Build GUI widgets ---
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

        self.status_label = tk.Label(
            self,
            text="Ready.",
            font=("Consolas", 10),
        )
        self.status_label.pack(pady=10)

        self.result_frame = tk.Frame(self)
        self.result_frame.pack(fill="both", expand=True)

        self.result_text = tk.Label(
            self.result_frame,
            text="",
            justify="left",
            font=("Consolas", 11),
        )
        self.result_text.pack(pady=10)

        # ✅ Apply theme AFTER all widgets exist
        self.apply_theme()

    # -------------------
    # THEME MANAGEMENT
    # -------------------
    def apply_theme(self):
        """Apply theme colors to all widgets"""
        c = self.colors[self.theme]
        self.configure(bg=c["bg"])

        # Update each major section
        self.title_label.configure(bg=c["bg"], fg=c["fg"])
        self.drop_area.configure(bg=c["box"], fg=c["fg"])
        self.status_label.configure(bg=c["bg"], fg="lightgreen")
        self.result_frame.configure(bg=c["bg"])
        self.result_text.configure(bg=c["bg"], fg=c["fg"])

        # Update graph theme (if exists)
        if self.graph_canvas:
            self.update_graph_theme()

    def toggle_theme(self):
        """Switch between dark and light mode"""
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.status_label.config(
            text=f"Theme changed to {self.theme.capitalize()} Mode."
        )

    # -------------------
    # FILE HANDLING
    # -------------------
    def choose_file(self):
        """Open file dialog"""
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
        """Handle file drop"""
        file_path = event.data.strip("{}")
        self.handle_file(file_path)

    def handle_file(self, file_path):
        """Handle compress/decompress actions"""
        if not os.path.exists(file_path):
            self.status_label.config(text="❌ File not found.")
            return

        # Clear old info/graph
        self.result_text.config(text="")
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None

        # Compression
        if file_path.lower().endswith(".txt"):
            self.status_label.config(text="Compressing...")
            self.update_idletasks()
            try:
                output_path = compress(file_path)
                self.show_compression_info(file_path, output_path)
                self.status_label.config(text="✅ Compression complete.")
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")

        # Decompression
        elif file_path.lower().endswith(".huff"):
            self.status_label.config(text="Decompressing...")
            self.update_idletasks()
            try:
                output_path = decompress(file_path)
                self.result_text.config(
                    text=f"✅ Decompressed successfully!\nSaved to:\n{output_path}"
                )
                self.status_label.config(text="✅ Decompression complete.")
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")

        # Unsupported file
        else:
            self.status_label.config(text="⚠️ Unsupported file type.")

    # -------------------
    # DISPLAY INFO + GRAPH
    # -------------------
    def show_compression_info(self, original_path, compressed_path):
        """Display compression stats and graph"""
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

        # Draw chart
        self.show_compression_graph(original_size, compressed_size, ratio)

    def show_compression_graph(self, original_size, compressed_size, ratio):
        """Render matplotlib bar chart inside GUI"""
        colors = self.colors[self.theme]

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.bar(["Original", "Compressed"], [original_size, compressed_size],
               color=["#5B8BF7", "#F15A5A"])

        ax.set_ylabel("File Size (bytes)", color=colors["fg"])
        ax.set_title(f"Compression Ratio: {ratio:.2f}% Saved", color=colors["fg"])

        # Apply theme to plot
        fig.patch.set_facecolor(colors["plot_bg"])
        ax.set_facecolor(colors["plot_bg"])
        ax.tick_params(colors=colors["fg"])
        for spine in ax.spines.values():
            spine.set_color(colors["fg"])

        plt.tight_layout()

        # Embed inside Tkinter
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        self.graph_canvas.draw()
        widget = self.graph_canvas.get_tk_widget()
        widget.configure(bg=colors["bg"], highlightthickness=0)
        widget.pack(pady=5)

    def update_graph_theme(self):
        """Redraw the existing graph when theme changes"""
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None


if __name__ == "__main__":
    app = HuffmanGUI()
    app.mainloop()
