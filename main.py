# main.py
import os
from huffman import build_tree, build_codes, rebuild_tree_from_codes, decode_bits_to_bytes
from utils import (
    read_file_bytes, write_binary_file, write_text_file, read_binary_file_bits,
    pad_encoded_text, remove_padding, get_byte_array,
    save_metadata, load_metadata
)

OUTPUT_DIR_DEFAULT = "output"
os.makedirs(OUTPUT_DIR_DEFAULT, exist_ok=True)


def compress(file_path, output_dir=OUTPUT_DIR_DEFAULT, progress_callback=None):
    """
    Compress any file (binary-safe) using Huffman coding.
    progress_callback(percent) optional, percent in 0..100
    """
    os.makedirs(output_dir, exist_ok=True)

    data = read_file_bytes(file_path)
    total_len = len(data)
    if total_len == 0:
        raise ValueError("File is empty.")

    if progress_callback:
        progress_callback(2)

    # build tree & codes
    root = build_tree(data)
    codes = build_codes(root)

    if progress_callback:
        progress_callback(5)

    # encode bytes -> bitstring
    encoded_parts = []
    last_percent = 5
    # choose step to update roughly 1% increments
    step = max(1, total_len // 80)
    for i, b in enumerate(data):
        encoded_parts.append(codes[b])
        if progress_callback and (i % step == 0):
            percent = 5 + (i / total_len) * 75  # range 5..80
            if percent - last_percent >= 1:
                progress_callback(percent)
                last_percent = percent

    encoded_text = "".join(encoded_parts)

    if progress_callback:
        progress_callback(82)

    # pad and convert to bytes
    padded = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded)

    if progress_callback:
        progress_callback(90)

    base_name = os.path.basename(file_path)
    out_path = os.path.join(output_dir, base_name + ".huff")
    write_binary_file(out_path, byte_array)
    save_metadata(out_path, codes)

    if progress_callback:
        progress_callback(100)

    compressed_size = os.path.getsize(out_path)
    original_size = os.path.getsize(file_path)
    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0.0

    print(f"✅ Compressed {file_path} → {out_path}")
    print(f"   Original: {original_size} bytes, Compressed: {compressed_size} bytes, Saved: {ratio:.2f}%")
    return out_path


def decompress(file_path, output_dir=OUTPUT_DIR_DEFAULT, progress_callback=None):
    """
    Decompress .huff file created by this tool.
    Returns path to decompressed file (binary-safe).
    """
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Read compressed binary file as bits
    bit_string = read_binary_file_bits(file_path)
    total_bits = len(bit_string)
    if total_bits == 0:
        raise ValueError("Compressed file is empty.")

    if progress_callback:
        progress_callback(10)

    # Step 2: Remove padding
    encoded_bits = remove_padding(bit_string)

    if progress_callback:
        progress_callback(25)

    # Step 3: Load Huffman codes and rebuild tree
    codes = load_metadata(file_path)
    root = rebuild_tree_from_codes(codes)

    if progress_callback:
        progress_callback(35)

    # Step 4: Decode bits to bytes
    decoded = bytearray()
    node = root
    last_percent = 35
    total_encoded_bits = len(encoded_bits)
    step = max(1, total_encoded_bits // 60) if total_encoded_bits > 0 else 1

    for i, bit in enumerate(encoded_bits):
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded.append(node.char)
            node = root
        if progress_callback and (i % step == 0):
            percent = 35 + (i / max(1, total_encoded_bits)) * 60
            if percent - last_percent >= 1:
                progress_callback(percent)
                last_percent = percent

    if progress_callback:
        progress_callback(95)

    # Step 5: Construct output filename
    base_name = os.path.basename(file_path)
    if base_name.endswith(".huff"):
        base_name = base_name[:-5]

    # Insert "_out" before extension (e.g., data.txt → data_out.txt)
    name_part, ext_part = os.path.splitext(base_name)
    out_path = os.path.join(output_dir, f"{name_part}_out{ext_part}")

    # Step 6: Write decompressed file
    write_binary_file(out_path, bytes(decoded))

    if progress_callback:
        progress_callback(100)

    print(f"✅ Decompressed {file_path} → {out_path}")
    return out_path



# CLI entrypoint
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python main.py compress <file> OR python main.py decompress <file>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    path = sys.argv[2]

    if mode == "compress":
        compress(path)
    elif mode == "decompress":
        decompress(path)
    else:
        print("Invalid mode. Use 'compress' or 'decompress'.")
