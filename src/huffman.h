#ifndef HUFFMAN_H
#define HUFFMAN_H

#include <vector>
#include <string>
#include <functional>
#include <unordered_map>

// progress_callback receives percent (0..100)
using ProgressCallback = std::function<void(int)>;

namespace Huffman {

// Compress input file (binary-safe).
// outputDir: directory where .huff and .meta will be written.
// Returns output .huff path, throws std::runtime_error on error.
std::string compress(const std::string &inputPath, const std::string &outputDir, ProgressCallback progress = nullptr);

// Decompress .huff file (binary-safe).
// outputDir: directory where decompressed file will be written.
// Returns decompressed file path, throws std::runtime_error on error.
std::string decompress(const std::string &huffPath, const std::string &outputDir, ProgressCallback progress = nullptr);

} // namespace Huffman

#endif // HUFFMAN_H
