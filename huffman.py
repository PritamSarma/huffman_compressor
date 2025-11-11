# huffman.py
import heapq
from collections import Counter

class Node:
    def __init__(self, char, freq):
        """
        char: int (0-255) or None for internal node
        freq: frequency
        """
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(data_bytes):
    """
    data_bytes: bytes or iterable of ints (0-255)
    returns: root Node
    """
    freq = Counter(data_bytes)  # iterates bytes as ints
    heap = [Node(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)

    if len(heap) == 0:
        return None

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(None, n1.freq + n2.freq)
        merged.left = n1
        merged.right = n2
        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(root):
    """
    root: Node
    returns: dict mapping int(byte) -> code string like '1010'
    """
    codes = {}
    if root is None:
        return codes

    def traverse(node, prefix=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = prefix if prefix != "" else "0"
            return
        traverse(node.left, prefix + "0")
        traverse(node.right, prefix + "1")

    traverse(root)
    return codes


def encode_bytes(data_bytes, codes):
    """
    Encode bytes (iterable of ints or bytes) to bitstring using codes dict.
    returns bitstring (str of '0'/'1')
    """
    return ''.join(codes[b] for b in data_bytes)


def decode_bits_to_bytes(encoded_bits, root):
    """
    Decode bitstring using tree root to bytes.
    returns bytes object
    """
    if root is None:
        return b''

    decoded = bytearray()
    node = root
    for bit in encoded_bits:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded.append(node.char)
            node = root
    return bytes(decoded)


def rebuild_tree_from_codes(codes):
    """
    codes: dict mapping int(byte) -> code string
    returns tree root
    """
    root = Node(None, 0)
    for ch_int, code in codes.items():
        node = root
        for bit in code:
            if bit == '0':
                if not node.left:
                    node.left = Node(None, 0)
                node = node.left
            else:
                if not node.right:
                    node.right = Node(None, 0)
                node = node.right
        node.char = int(ch_int)
    return root
