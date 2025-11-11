import heapq
from collections import Counter

# Node class for Huffman Tree
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


# Build Huffman Tree from text
def build_tree(text):
    freq = Counter(text)
    heap = [Node(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = Node(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)

    return heap[0]


# Generate Huffman codes
def build_codes(root):
    codes = {}

    def traverse(node, prefix=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = prefix
        traverse(node.left, prefix + "0")
        traverse(node.right, prefix + "1")

    traverse(root)
    return codes


# Encode text to binary string
def encode_text(text, codes):
    return ''.join(codes[ch] for ch in text)


# Decode binary string using Huffman tree
def decode_text(encoded_text, root):
    decoded = []
    node = root
    for bit in encoded_text:
        node = node.left if bit == '0' else node.right
        if node.char:
            decoded.append(node.char)
            node = root
    return ''.join(decoded)
