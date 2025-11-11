import os
from huffman import build_tree, build_codes, rebuild_tree_from_codes
from utils import (
    read_file, write_binary_file, write_text_file, read_binary_file,
    pad_encoded_text, remove_padding, get_byte_array,
    save_metadata, load_metadata
)

OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def compress(file_path, progress_callback=None):
    """
    Compress a text file using Huffman coding.
    Updates progress_callback(percent) during the process.
    """

    # --- Step 1: Read input file ---
    text = read_file(file_path)
    total_len = len(text)
    original_size = os.path.getsize(file_path)

    if progress_callback:
        progress_callback(2)

    # --- Step 2: Build Huffman Tree and Codes ---
    root = build_tree(text)
    codes = build_codes(root)

    if progress_callback:
        progress_callback(5)

    # --- Step 3: Encode Text ---
    encoded_text = []
    last_percent = 0
    for i, ch in enumerate(text):
        encoded_text.append(codes[ch])
        if progress_callback and i % max(1, total_len // 90) == 0:
            percent = 5 + (i / total_len) * 75  # 5% → 80%
            if percent - last_percent >= 1:
                progress_callback(percent)
                last_percent = percent

    encoded_text = "".join(encoded_text)

    if progress_callback:
        progress_callback(82)

    # --- Step 4: Pad encoded text & convert to bytes ---
    padded_text = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded_text)

    if progress_callback:
        progress_callback(90)

    # --- Step 5: Save compressed file & metadata ---
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(OUTPUT_DIR, base_name + ".huff")
    write_binary_file(output_path, bytes(byte_array))
    save_metadata(output_path, codes)

    if progress_callback:
        progress_callback(97)

    # --- Step 6: Finalize ---
    compressed_size = os.path.getsize(output_path)
    ratio = (1 - compressed_size / original_size) * 100

    if progress_callback:
        progress_callback(100)

    print("✅ Compression complete:")
    print(f"   Input File: {file_path}")
    print(f"   Output File: {output_path}")
    print(f"   Original Size: {original_size / 1024:.2f} KB")
    print(f"   Compressed Size: {compressed_size / 1024:.2f} KB")
    print(f"   Space Saved: {ratio:.2f}%")

    return output_path


def decompress(file_path, progress_callback=None):
    """
    Decompress a .huff file using Huffman coding.
    Updates progress_callback(percent) during the process.
    """

    # --- Step 1: Read compressed binary data ---
    bit_string = read_binary_file(file_path)
    total_bits = len(bit_string)

    if progress_callback:
        progress_callback(10)

    # --- Step 2: Remove padding ---
    encoded_text = remove_padding(bit_string)

    if progress_callback:
        progress_callback(25)

    # --- Step 3: Load Huffman codes ---
    codes = load_metadata(file_path)
    root = rebuild_tree_from_codes(codes)

    if progress_callback:
        progress_callback(35)

    # --- Step 4: Decode text ---
    decoded_chars = []
    node = root
    last_percent = 35
    for i, bit in enumerate(encoded_text):
        node = node.left if bit == '0' else node.right
        if node.char:
            decoded_chars.append(node.char)
            node = root
        if progress_callback and i % max(1, total_bits // 60) == 0:
            percent = 35 + (i / total_bits) * 60  # up to 95%
            if percent - last_percent >= 1:
                progress_callback(percent)
                last_percent = percent

    if progress_callback:
        progress_callback(97)

    decoded_text = "".join(decoded_chars)

    # --- Step 5: Write decompressed file ---
    output_path = os.path.join(
        OUTPUT_DIR, os.path.basename(file_path).split(".")[0] + "_out.txt"
    )
    write_text_file(output_path, decoded_text)

    if progress_callback:
        progress_callback(100)

    print("✅ Decompression complete:")
    print(f"   Input File: {file_path}")
    print(f"   Output File: {output_path}")

    return output_path


# --- CLI Entry Point ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python main.py compress <input_file>")
        print("  python main.py decompress <input_file>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    file_path = sys.argv[2]

    if mode == "compress":
        compress(file_path)
    elif mode == "decompress":
        decompress(file_path)
    else:
        print("Invalid mode. Use 'compress' or 'decompress'.")
