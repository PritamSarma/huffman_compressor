#include "huffman.h"
#include <fstream>
#include <queue>
#include <vector>
#include <array>
#include <stdexcept>
#include <filesystem>
#include <sstream>
#include <iomanip>
#include <nlohmann/json.hpp> // We'll avoid external dependency - implement basic JSON manually below

// We'll implement a minimal JSON writer/reader to avoid adding third-party dependencies.
// But for simplicity here we'll write metadata as a simple line format: byte:number:code
// However, to keep readability we'll write a small JSON-like file manually.

namespace fs = std::filesystem;

struct Node {
    int byteVal; // -1 for internal
    uint64_t freq;
    Node* left;
    Node* right;
    Node(int b, uint64_t f) : byteVal(b), freq(f), left(nullptr), right(nullptr) {}
    Node(Node* l, Node* r) : byteVal(-1), freq(l->freq + r->freq), left(l), right(r) {}
};

struct NodeCmp {
    bool operator()(const Node* a, const Node* b) const {
        return a->freq > b->freq;
    }
};

// helper to free tree
static void freeTree(Node* n) {
    if (!n) return;
    freeTree(n->left);
    freeTree(n->right);
    delete n;
}

// Build tree from frequency array
static Node* buildTree(const std::array<uint64_t,256> &freq) {
    std::priority_queue<Node*, std::vector<Node*>, NodeCmp> pq;
    for (int i=0;i<256;i++){
        if (freq[i] > 0) pq.push(new Node(i, freq[i]));
    }
    if (pq.empty()) return nullptr;
    while (pq.size() > 1) {
        Node* a = pq.top(); pq.pop();
        Node* b = pq.top(); pq.pop();
        pq.push(new Node(a,b));
    }
    return pq.top();
}

// Build codes by traversing tree
static void buildCodes(Node* root, std::vector<std::string> &codes, std::string &cur) {
    if (!root) return;
    if (root->left == nullptr && root->right == nullptr) {
        // leaf
        int b = root->byteVal;
        codes[b] = cur.empty() ? "0" : cur;
        return;
    }
    if (root->left) {
        cur.push_back('0');
        buildCodes(root->left, codes, cur);
        cur.pop_back();
    }
    if (root->right) {
        cur.push_back('1');
        buildCodes(root->right, codes, cur);
        cur.pop_back();
    }
}

// Convert bitstring (string of '0'/'1') to vector<uint8_t>
static std::vector<uint8_t> bitsToBytes(const std::string &bits) {
    std::vector<uint8_t> out;
    size_t n = bits.size();
    // add padding info at start: 1 byte representing extra padding (0..7)
    int extra = (8 - (n % 8)) % 8;
    std::string padded = bits + std::string(extra, '0');
    // store padding as first byte later (we'll prepend to result)
    for (size_t i=0;i<padded.size(); i+=8) {
        uint8_t val = 0;
        for (size_t j=0;j<8;j++){
            val = (val << 1) | (padded[i+j] - '0');
        }
        out.push_back(val);
    }
    // result currently is only the data bytes; caller must prepend padding info
    return out;
}

// Convert bytes to bitstring. `bytes` should be the data bytes read from file.
// paddingByte is the first byte that tells how many padding bits were added at end.
static std::string bytesToBits(const std::vector<uint8_t>& bytes, int paddingBits) {
    std::string bits;
    bits.reserve(bytes.size()*8);
    for (uint8_t b : bytes) {
        for (int i=7;i>=0;--i){
            bits.push_back(((b >> i) & 1) ? '1' : '0');
        }
    }
    if (paddingBits) bits.erase(bits.end()-paddingBits, bits.end());
    return bits;
}

// Save codes to .meta file as simple JSON-like lines: "byte": "code"
static void saveMeta(const std::string &metaPath, const std::vector<std::string> &codes) {
    std::ofstream fout(metaPath, std::ios::binary);
    if (!fout) throw std::runtime_error("Cannot write metadata file: " + metaPath);
    // write as simple lines: byte<space>code\n e.g. 32 10101
    for (int i=0;i<256;i++){
        if (!codes[i].empty()) {
            fout << i << ' ' << codes[i] << '\n';
        }
    }
    fout.close();
}

// Load meta file: fill codes map
static std::vector<std::string> loadMeta(const std::string &metaPath) {
    std::vector<std::string> codes(256);
    std::ifstream fin(metaPath, std::ios::binary);
    if (!fin) throw std::runtime_error("Cannot open metadata: " + metaPath);
    int b;
    std::string code;
    while (fin >> b >> code) {
        codes[b] = code;
    }
    fin.close();
    return codes;
}

// Rebuild tree from code map
static Node* rebuildFromCodes(const std::vector<std::string> &codes) {
    Node* root = new Node(-1,0);
    for (int i=0;i<256;i++){
        if (codes[i].empty()) continue;
        Node* cur = root;
        for (char c : codes[i]) {
            if (c == '0') {
                if (!cur->left) cur->left = new Node(-1,0);
                cur = cur->left;
            } else {
                if (!cur->right) cur->right = new Node(-1,0);
                cur = cur->right;
            }
        }
        cur->byteVal = i;
    }
    return root;
}

std::string Huffman::compress(const std::string &inputPath, const std::string &outputDir, ProgressCallback progress) {
    // read all bytes
    std::ifstream fin(inputPath, std::ios::binary);
    if (!fin) throw std::runtime_error("Cannot open input file");
    std::vector<uint8_t> data((std::istreambuf_iterator<char>(fin)), std::istreambuf_iterator<char>());
    fin.close();
    uint64_t totalBytes = data.size();
    if (totalBytes == 0) throw std::runtime_error("Input file is empty");

    if (progress) progress(2);

    // freq
    std::array<uint64_t,256> freq{};
    freq.fill(0);
    for (auto b : data) freq[b]++;

    // build tree
    Node* root = buildTree(freq);
    if (!root) throw std::runtime_error("Failed to build Huffman tree");

    // build codes
    std::vector<std::string> codes(256);
    std::string cur;
    buildCodes(root, codes, cur);

    if (progress) progress(5);

    // encode
    std::string bitstring;
    bitstring.reserve(totalBytes); // rough
    uint64_t processed = 0;
    for (size_t i=0;i<data.size();++i) {
        bitstring += codes[data[i]];
        processed++;
        if (progress && (i % std::max<size_t>(1, data.size()/100) == 0)) {
            int percent = 5 + int((processed * 75) / totalBytes); // 5..80
            progress(std::min(percent, 80));
        }
    }

    // pad info
    int extra = (8 - (bitstring.size() % 8)) % 8;
    std::string padded = bitstring + std::string(extra, '0');
    // convert to bytes
    std::vector<uint8_t> payload;
    payload.reserve((padded.size()/8));
    for (size_t i=0;i<padded.size(); i+=8) {
        uint8_t v = 0;
        for (size_t j=0;j<8;j++){
            v = (v<<1) | (padded[i+j]-'0');
        }
        payload.push_back(v);
    }

    if (progress) progress(90);

    // write output .huff: first byte = padding extra (0..7), then payload bytes
    fs::create_directories(outputDir);
    std::string base = fs::path(inputPath).filename().string();
    std::string outHuff = (fs::path(outputDir) / (base + ".huff")).string();
    std::ofstream fout(outHuff, std::ios::binary);
    if (!fout) {
        freeTree(root);
        throw std::runtime_error("Cannot write output file");
    }
    fout.put(static_cast<char>(extra));
    fout.write(reinterpret_cast<const char*>(payload.data()), (std::streamsize)payload.size());
    fout.close();

    // save metadata
    std::string metaPath = outHuff + ".meta";
    saveMeta(metaPath, codes);

    if (progress) progress(100);
    freeTree(root);
    return outHuff;
}

std::string Huffman::decompress(const std::string &huffPath, const std::string &outputDir, ProgressCallback progress) {
    // read padding byte + payload
    std::ifstream fin(huffPath, std::ios::binary);
    if (!fin) throw std::runtime_error("Cannot open compressed file");
    int padding = fin.get();
    std::vector<uint8_t> payload((std::istreambuf_iterator<char>(fin)), std::istreambuf_iterator<char>());
    fin.close();

    if (payload.empty() && padding==EOF) throw std::runtime_error("Empty compressed file");
    if (progress) progress(10);

    // convert payload to bitstring
    std::string bits;
    bits.reserve(payload.size()*8);
    for (auto b : payload) {
        for (int i=7;i>=0;--i) bits.push_back(((b>>i)&1)?'1':'0');
    }
    // remove padding bits at end
    if (padding) bits.erase(bits.end()-padding, bits.end());

    if (progress) progress(25);

    // load metadata
    std::string metaPath = huffPath + ".meta";
    auto codes = loadMeta(metaPath);

    if (progress) progress(35);

    // rebuild tree
    Node* root = rebuildFromCodes(codes);

    // decode
    std::vector<uint8_t> outbytes;
    Node* cur = root;
    size_t totalBits = bits.size();
    for (size_t i=0;i<bits.size();++i) {
        cur = (bits[i]=='0') ? cur->left : cur->right;
        if (!cur) { freeTree(root); throw std::runtime_error("Decoding failed (tree traversal)"); }
        if (!cur->left && !cur->right) {
            outbytes.push_back(static_cast<uint8_t>(cur->byteVal));
            cur = root;
        }
        if (progress && (i % std::max<size_t>(1, totalBits/100) == 0)) {
            int percent = 35 + int((i * 60) / std::max<size_t>(1,totalBits));
            progress(std::min(percent, 95));
        }
    }

    if (progress) progress(95);

    // write output with _out before extension
    fs::create_directories(outputDir);
    std::string base = fs::path(huffPath).filename().string();
    if (base.size() >= 5 && base.substr(base.size()-5) == ".huff") base = base.substr(0, base.size()-5);
    auto parts = fs::path(base).stem().string(); // stem strips only final extension; but for complex names we'll use split_extension
    // better split:
    std::string name_part, ext_part;
    std::string filename = fs::path(base).filename().string();
    size_t pos = filename.rfind('.');
    if (pos == std::string::npos) { name_part = filename; ext_part = ""; }
    else { name_part = filename.substr(0,pos); ext_part = filename.substr(pos); }

    std::string outPath = (fs::path(outputDir) / (name_part + "_out" + ext_part)).string();
    std::ofstream out(outPath, std::ios::binary);
    if (!out) { freeTree(root); throw std::runtime_error("Cannot write decompressed file"); }
    out.write(reinterpret_cast<const char*>(outbytes.data()), (std::streamsize)outbytes.size());
    out.close();

    if (progress) progress(100);
    freeTree(root);
    return outPath;
}
