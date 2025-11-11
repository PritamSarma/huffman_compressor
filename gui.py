import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from main import compress, decompress


class HuffmanGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("🗜️ Huffman File Compressor")
        self.geometry("520x360")
        self.resizable(False, False)

        # --- Default theme: Dark ---
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
            font=("Segoe UI", 16, "bold"),
            fg=self.colors[self.theme]["fg"],
            bg=self.colors[self.theme]["bg"],
        )
        self.title_label.pack(pady=20)

        # --- Drop Area ---
        self.drop_area = tk.Label(
            self,
            text="\n\nDrag & Drop your file here\n(.txt to compress or .huff to decompress)\n\n",
            relief="ridge",
            width=50,
            height=8,
            bg=self.colors[self.theme]["box"],
            fg=self.colors[self.theme]["fg"],
            font=("Segoe UI", 11),
        )
        self.drop_area.pack(pady=10)

        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.on_drop)

        # --- Buttons Frame ---
        btn_frame = tk.Frame(self, bg=self.colors[self.theme]["bg"])
        btn_frame.pack(pady=10)

        # Choose File Button
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
            cursor="hand2"
        )
        choose_btn.grid(row=0, column=0, padx=10)

        # Theme Toggle Button
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
            cursor="hand2"
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

    # --- Theme Control ---
    def apply_theme(self):
        c = self.colors[self.theme]
        self.configure(bg=c["bg"])
        if hasattr(self, "drop_area"):
            self.drop_area.configure(bg=c["box"], fg=c["fg"])
        if hasattr(self, "title_label"):
            self.title_label.configure(bg=c["bg"], fg=c["fg"])
        if hasattr(self, "status_label"):
            self.status_label.configure(bg=c["bg"], fg="lightgreen")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.status_label.config(
            text=f"Theme changed to {self.theme.capitalize()} Mode."
        )

    # --- File Handling ---
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
            messagebox.showerror("Error", "File not found.")
            return

        if file_path.lower().endswith(".txt"):
            self.status_label.config(text="Compressing...")
            self.update_idletasks()
            try:
                output_path = compress(file_path)
                messagebox.showinfo(
                    "Success",
                    f"✅ Compressed successfully!\n\nSaved to:\n{output_path}",
                )
                self.status_label.config(text="Compression complete.")
            except Exception as e:
                messagebox.showerror("Error", f"Compression failed:\n{e}")
                self.status_label.config(text="Error.")
        elif file_path.lower().endswith(".huff"):
            self.status_label.config(text="Decompressing...")
            self.update_idletasks()
            try:
                output_path = decompress(file_path)
                messagebox.showinfo(
                    "Success",
                    f"✅ Decompressed successfully!\n\nSaved to:\n{output_path}",
                )
                self.status_label.config(text="Decompression complete.")
            except Exception as e:
                messagebox.showerror("Error", f"Decompression failed:\n{e}")
                self.status_label.config(text="Error.")
        else:
            messagebox.showwarning("Unsupported", "Please drop a .txt or .huff file.")
            self.status_label.config(text="Unsupported file type.")


if __name__ == "__main__":
    app = HuffmanGUI()
    app.mainloop()
