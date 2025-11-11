import sys
import os
import matplotlib.pyplot as plt
from huffman import (
    build_tree, build_codes, encode_text, decode_text, rebuild_tree_from_codes
)
from utils import (
    pad_encoded_text, get_byte_array, remove_padding,
    read_file, write_binary_file, read_binary_file, write_text_file,
    save_metadata, load_metadata
)

OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def compress(file_path, progress_callback=None):
    print(f"🔹 Reading {file_path} ...")
    text = read_file(file_path)
    original_size = os.path.getsize(file_path)

    print("🔹 Building Huffman Tree ...")
    root = build_tree(text)
    codes = build_codes(root)

    print("🔹 Encoding text ...")
    encoded_text = ""
    length = len(text)
    for i, ch in enumerate(text):
        encoded_text += codes[ch]
        # ✅ Update progress every ~1% of data
        if progress_callback and i % max(1, length // 100) == 0:
            progress_callback(i / length * 80)  # up to 80% for encoding

    padded_text = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded_text)

    base_name = os.path.basename(file_path).split('.')[0]
    output_path = os.path.join(OUTPUT_DIR, base_name + ".huff")
    meta_path = save_metadata(output_path, codes)

    print("🔹 Writing compressed file ...")
    write_binary_file(output_path, bytes(byte_array))

    compressed_size = os.path.getsize(output_path)
    ratio = (1 - compressed_size / original_size) * 100

    if progress_callback:
        progress_callback(100)  # complete

    print(f"✅ Compressed successfully → {output_path}")
    print(f"🧾 Metadata saved → {meta_path}")
    print(f"📉 Compression ratio: {ratio:.2f}%")

    return output_path


def decompress(file_path, progress_callback=None):
    print(f"🔹 Reading compressed file {file_path} ...")
    bit_string = read_binary_file(file_path)

    if progress_callback:
        progress_callback(20)

    encoded_text = remove_padding(bit_string)

    if progress_callback:
        progress_callback(40)

    print("🔹 Loading Huffman metadata ...")
    codes = load_metadata(file_path)
    root = rebuild_tree_from_codes(codes)

    if progress_callback:
        progress_callback(60)

    print("🔹 Decoding text ...")
    decoded_chars = []
    node = root
    total_bits = len(encoded_text)
    for i, bit in enumerate(encoded_text):
        node = node.left if bit == '0' else node.right
        if node.char:
            decoded_chars.append(node.char)
            node = root
        # ✅ Update progress live
        if progress_callback and i % max(1, total_bits // 100) == 0:
            progress_callback(60 + (i / total_bits * 40))

    decoded_text = ''.join(decoded_chars)

    output_path = os.path.join(
        OUTPUT_DIR, os.path.basename(file_path).split('.')[0] + "_out.txt"
    )
    write_text_file(output_path, decoded_text)

    if progress_callback:
        progress_callback(100)

    print(f"✅ Decompressed successfully → {output_path}")
    return output_path


def show_compression_report(original_size, compressed_size, ratio, file_path):
    """Display compression summary and a visual chart"""
    print("\n📊 COMPRESSION REPORT")
    print(f"   Original file size  : {original_size / 1024:.2f} KB")
    print(f"   Compressed file size: {compressed_size / 1024:.2f} KB")
    print(f"   Space saved         : {ratio:.2f}%")

    # Bar chart
    plt.figure(figsize=(5, 4))
    plt.bar(["Original", "Compressed"], [original_size, compressed_size])
    plt.ylabel("File Size (bytes)")
    plt.title(f"Compression Report for '{os.path.basename(file_path)}'")
    plt.tight_layout()
    #plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:\n  python main.py compress <filename>\n  python main.py decompress <filename>")
        sys.exit(1)

    action = sys.argv[1]
    filename = sys.argv[2]

    if action == "compress":
        compress(filename)
    elif action == "decompress":
        decompress(filename)
    else:
        print("Invalid action. Use 'compress' or 'decompress'.")
