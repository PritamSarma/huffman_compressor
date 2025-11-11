import os
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from main import compress, decompress


class HuffmanGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Huffman File Compressor")
        self.geometry("500x300")
        self.configure(bg="#1E1E1E")

        # Title
        title_label = tk.Label(
            self, text="🗜️ Huffman File Compressor",
            font=("Segoe UI", 16, "bold"), fg="white", bg="#1E1E1E"
        )
        title_label.pack(pady=20)

        # Drop area
        self.drop_area = tk.Label(
            self,
            text="\n\nDrag and Drop your file here\n(.txt to compress or .huff to decompress)\n\n",
            relief="ridge",
            width=50,
            height=8,
            bg="#2D2D2D",
            fg="lightgray",
            font=("Segoe UI", 11)
        )
        self.drop_area.pack(pady=20)

        # Bind drag & drop
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # Status label
        self.status_label = tk.Label(
            self, text="Ready.", fg="lightgreen", bg="#1E1E1E", font=("Consolas", 10)
        )
        self.status_label.pack(pady=10)

    def on_drop(self, event):
        file_path = event.data.strip("{}")  # handle paths with spaces
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
                messagebox.showinfo("Success", f"✅ Compressed successfully!\n\nSaved to:\n{output_path}")
                self.status_label.config(text="Compression complete.")
            except Exception as e:
                messagebox.showerror("Error", f"Compression failed:\n{e}")
                self.status_label.config(text="Error.")
        elif file_path.lower().endswith(".huff"):
            self.status_label.config(text="Decompressing...")
            self.update_idletasks()
            try:
                output_path = decompress(file_path)
                messagebox.showinfo("Success", f"✅ Decompressed successfully!\n\nSaved to:\n{output_path}")
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