#include "Worker.h"
#include "huffman.h"
#include <chrono>
#include <functional>

Worker::Worker(QObject* parent) : QObject(parent) {}
Worker::~Worker() {}

void Worker::setPaths(const QString &in, const QString &out) {
    inputPath = in;
    outputDir = out;
}

void Worker::setModeCompress(bool c) {
    modeCompress = c;
}

void Worker::process() {
    try {
        // create a progress callback that emits signal
        std::function<void(int)> cb = [this](int p){
            emit progress(p);
        };

        if (modeCompress) {
            std::string out = Huffman::compress(inputPath.toStdString(), outputDir.toStdString(), cb);
            emit finished(QString::fromStdString(out));
        } else {
            std::string out = Huffman::decompress(inputPath.toStdString(), outputDir.toStdString(), cb);
            emit finished(QString::fromStdString(out));
        }
    } catch (const std::exception &ex) {
        emit error(QString::fromStdString(ex.what()));
    } catch (...) {
        emit error("Unknown error in compression/decompression");
    }
}
