import json

def pad_encoded_text(encoded_text):
    extra_padding = 8 - len(encoded_text) % 8
    for _ in range(extra_padding):
        encoded_text += "0"
    padded_info = "{0:08b}".format(extra_padding)
    return padded_info + encoded_text


def get_byte_array(padded_text):
    b = bytearray()
    for i in range(0, len(padded_text), 8):
        byte = padded_text[i:i + 8]
        b.append(int(byte, 2))
    return b


def remove_padding(padded_encoded_text):
    padded_info = padded_encoded_text[:8]
    extra_padding = int(padded_info, 2)
    encoded_text = padded_encoded_text[8:]
    return encoded_text[:-extra_padding]


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_binary_file(file_path, data):
    with open(file_path, 'wb') as f:
        f.write(data)


def read_binary_file(file_path):
    with open(file_path, 'rb') as f:
        bit_string = ""
        byte = f.read(1)
        while byte:
            byte = ord(byte)
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            byte = f.read(1)
        return bit_string


def write_text_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


# New: save and load Huffman code table
def save_metadata(file_path, codes):
    meta_path = file_path + ".meta"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(codes, f)
    return meta_path


def load_metadata(file_path):
    meta_path = file_path + ".meta"
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)
