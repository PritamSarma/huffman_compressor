# utils.py
import json
import os

# --- Bit padding helpers (work with strings of '0'/'1') ---
def pad_encoded_text(encoded_text):
    """
    Adds padding info at the front (8 bits) representing number of padded zeros added.
    """
    extra_padding = 8 - (len(encoded_text) % 8)
    if extra_padding == 8:
        extra_padding = 0
    padded = encoded_text + ("0" * extra_padding)
    padded_info = "{0:08b}".format(extra_padding)
    return padded_info + padded


def get_byte_array(padded_text):
    """
    Convert padded '0'/'1' string to bytes (bytearray)
    """
    b = bytearray()
    for i in range(0, len(padded_text), 8):
        byte = padded_text[i:i + 8]
        b.append(int(byte, 2))
    return bytes(b)


def remove_padding(padded_encoded_text):
    """
    Remove first 8 bits header and trailing padding zeros
    """
    if len(padded_encoded_text) < 8:
        return ""
    padded_info = padded_encoded_text[:8]
    extra_padding = int(padded_info, 2)
    encoded_text = padded_encoded_text[8:]
    if extra_padding:
        return encoded_text[:-extra_padding]
    return encoded_text


# --- File I/O helpers (binary-safe) ---
def read_file_bytes(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def write_binary_file(file_path, data_bytes):
    os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
    with open(file_path, "wb") as f:
        f.write(data_bytes)


def read_binary_file_bits(file_path):
    """
    Read a binary file and return its bits as a string '010101...'
    Used to read .huff compressed files
    """
    bits = []
    with open(file_path, "rb") as f:
        chunk = f.read(4096)
        while chunk:
            for b in chunk:
                bits.append(format(b, '08b'))
            chunk = f.read(4096)
    return ''.join(bits)


def write_text_file(file_path, text, encoding="utf-8"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
    with open(file_path, "w", encoding=encoding) as f:
        f.write(text)


# --- Metadata save/load ---
def save_metadata(huff_path, codes):
    """
    codes: dict mapping int -> code string
    Save as JSON alongside compressed file: huff_path + '.meta'
    """
    meta_path = huff_path + ".meta"
    # convert keys to strings for JSON
    serializable = {str(k): v for k, v in codes.items()}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f)
    return meta_path


def load_metadata(huff_path):
    meta_path = huff_path + ".meta"
    with open(meta_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # convert keys back to ints
    return {int(k): v for k, v in raw.items()}
