import sys
import os
from huffman import build_tree, build_codes, encode_text, decode_text
from utils import (
    pad_encoded_text, get_byte_array, remove_padding,
    read_file, write_binary_file, read_binary_file, write_text_file
)

OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def compress(file_path):
    print(f"🔹 Reading {file_path} ...")
    text = read_file(file_path)

    print("🔹 Building Huffman Tree ...")
    root = build_tree(text)
    codes = build_codes(root)

    print("🔹 Encoding text ...")
    encoded_text = encode_text(text, codes)
    padded_text = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded_text)

    output_path = os.path.join(OUTPUT_DIR, os.path.basename(file_path).split('.')[0] + ".huff")
    write_binary_file(output_path, bytes(byte_array))

    ratio = (1 - len(byte_array) / len(text.encode('utf-8'))) * 100
    print(f"✅ Compressed successfully → {output_path}")
    print(f"📉 Compression ratio: {ratio:.2f}%")
    return output_path, root


def decompress(file_path, root=None):
    print(f"🔹 Reading compressed file {file_path} ...")
    bit_string = read_binary_file(file_path)

    print("🔹 Removing padding ...")
    encoded_text = remove_padding(bit_string)

    if not root:
        print("⚠️ Huffman tree not provided. Decompression will not work correctly without it.")
        return

    print("🔹 Decoding text ...")
    decoded_text = decode_text(encoded_text, root)

    output_path = os.path.join(OUTPUT_DIR, os.path.basename(file_path).split('.')[0] + "_out.txt")
    write_text_file(output_path, decoded_text)
    print(f"✅ Decompressed successfully → {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:\n  python main.py compress <filename>\n  python main.py decompress <filename>")
        sys.exit(1)

    action = sys.argv[1]
    filename = sys.argv[2]

    if action == "compress":
        compress(filename)
    elif action == "decompress":
        print("⚠️ Note: Tree must match the one used for compression in this run.")
        print("Currently, decompression only works in the same session.")
    else:
        print("Invalid action. Use 'compress' or 'decompress'.")
        