#include "MainWindow.h"
#include "Worker.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QFileDialog>
#include <QLabel>
#include <QProgressBar>
#include <QDragEnterEvent>
#include <QMimeData>
#include <QElapsedTimer>
#include <QDateTime>
#include <QMessageBox>
#include <QBarSet>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      workerThread(nullptr),
      worker(nullptr),
      totalSize(0),
      lastProcessedEstimate(0)
{
    setupUi();
    setWindowTitle("Huffman Compressor (Qt)");

    setAcceptDrops(true);
    outputDir = "output";
    outputLabel->setText(outputDir);
}

MainWindow::~MainWindow() {
    if (workerThread && workerThread->isRunning()) {
        workerThread->quit();
        workerThread->wait();
    }
}

void MainWindow::setupUi() {
    centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);

    QVBoxLayout *mainLay = new QVBoxLayout(centralWidget);

    QLabel *title = new QLabel("<h2>🗜️ Huffman File Compressor</h2>");
    title->setAlignment(Qt::AlignCenter);
    mainLay->addWidget(title);

    chooseFileButton = new QPushButton("📂 Choose File");
    chooseOutputButton = new QPushButton("📁 Choose Output Folder");
    modeButton = new QPushButton("Mode: Compress");
    fileLabel = new QLabel("No file selected");
    outputLabel = new QLabel("output");
    progressBar = new QProgressBar();
    progressBar->setRange(0,100);
    statusLabel = new QLabel("Ready.");
    speedLabel = new QLabel("Speed: - KB/s");
    etaLabel = new QLabel("ETA: --:--");

    QHBoxLayout *btnLay = new QHBoxLayout();
    btnLay->addWidget(chooseFileButton);
    btnLay->addWidget(chooseOutputButton);
    btnLay->addWidget(modeButton);
    mainLay->addLayout(btnLay);

    mainLay->addWidget(fileLabel);
    mainLay->addWidget(outputLabel);
    mainLay->addWidget(progressBar);

    QHBoxLayout *infoLay = new QHBoxLayout();
    infoLay->addWidget(statusLabel);
    infoLay->addStretch();
    infoLay->addWidget(speedLabel);
    infoLay->addWidget(etaLabel);
    mainLay->addLayout(infoLay);

    // Chart
    series = new QBarSeries();
    chart = new QChart();
    chart->addSeries(series);
    chart->setTitle("Compression (bytes)");
    QStringList categories;
    categories << "Original" << "Compressed";
    QBarCategoryAxis *axis = new QBarCategoryAxis();
    axis->append(categories);
    chart->createDefaultAxes();
    chart->setAxisX(axis, series);
    chartView = new QChartView(chart);
    chartView->setRenderHint(QPainter::Antialiasing);
    mainLay->addWidget(chartView, 1);

    // signals
    connect(chooseFileButton, &QPushButton::clicked, this, &MainWindow::on_chooseFileButton_clicked);
    connect(chooseOutputButton, &QPushButton::clicked, this, &MainWindow::on_chooseOutputButton_clicked);
    connect(modeButton, &QPushButton::clicked, this, &MainWindow::on_modeButton_clicked);
}

void MainWindow::dragEnterEvent(QDragEnterEvent *event) {
    if (event->mimeData()->hasUrls()) event->acceptProposedAction();
}

void MainWindow::dropEvent(QDropEvent *event) {
    const QList<QUrl> urls = event->mimeData()->urls();
    if (!urls.isEmpty()) {
        QString path = urls.first().toLocalFile();
        currentFile = path;
        fileLabel->setText(path);
        // start process automatically
        startProcessing(true); // compress mode by default; you can toggle
    }
}

void MainWindow::on_chooseFileButton_clicked() {
    QString f = QFileDialog::getOpenFileName(this, tr("Select file"), ".", tr("All Files (*)"));
    if (!f.isEmpty()) {
        currentFile = f;
        fileLabel->setText(f);
    }
}

void MainWindow::on_chooseOutputButton_clicked() {
    QString dir = QFileDialog::getExistingDirectory(this, tr("Select output folder"), ".");
    if (!dir.isEmpty()) {
        outputDir = dir;
        outputLabel->setText(dir);
    }
}

void MainWindow::on_modeButton_clicked() {
    if (modeButton->text().contains("Compress")) {
        modeButton->setText("Mode: Decompress");
    } else {
        modeButton->setText("Mode: Compress");
    }
}

void MainWindow::startProcessing(bool compressMode) {
    if (currentFile.isEmpty()) {
        QMessageBox::information(this, "No file", "Please select a file first.");
        return;
    }

    // Prepare worker & thread
    if (workerThread && workerThread->isRunning()) {
        QMessageBox::warning(this, "Busy", "Processing already in progress.");
        return;
    }

    workerThread = new QThread(this);
    worker = new Worker();
    worker->moveToThread(workerThread);
    worker->setPaths(currentFile, outputDir);
    worker->setModeCompress(modeButton->text().contains("Compress"));

    connect(workerThread, &QThread::started, worker, &Worker::process);
    connect(worker, &Worker::progress, this, &MainWindow::onWorkerProgress);
    connect(worker, &Worker::finished, this, &MainWindow::onWorkerFinished);
    connect(worker, &Worker::error, this, &MainWindow::onWorkerError);
    connect(worker, &Worker::finished, workerThread, &QThread::quit);
    connect(worker, &Worker::error, workerThread, &QThread::quit);
    connect(workerThread, &QThread::finished, worker, &Worker::deleteLater);
    connect(workerThread, &QThread::finished, workerThread, &QThread::deleteLater);

    // prepare UI
    progressBar->setValue(0);
    statusLabel->setText(modeButton->text().contains("Compress") ? "Compressing..." : "Decompressing...");
    timer.restart();
    totalSize = QFileInfo(currentFile).size();
    lastProcessedEstimate = 0;

    workerThread->start();
}

void MainWindow::onWorkerProgress(int percent) {
    progressBar->setValue(percent);
    qint64 processed = (qint64)((percent/100.0) * (double)totalSize);
    qint64 elapsedMs = timer.elapsed();
    double elapsedSec = elapsedMs / 1000.0;
    double speed = (elapsedSec > 0) ? (processed / 1024.0) / elapsedSec : 0.0; // KB/s
    speedLabel->setText(QString("Speed: %1 KB/s").arg(QString::number(speed, 'f', 2)));
    if (speed > 0) {
        qint64 remainingBytes = std::max<qint64>(0, totalSize - processed);
        qint64 etaSec = (qint64)(remainingBytes / 1024.0 / speed);
        qint64 m = (etaSec/60);
        qint64 s = etaSec%60;
        etaLabel->setText(QString("ETA: %1:%2").arg(m,2,10,QChar('0')).arg(s,2,10,QChar('0')));
    } else {
        etaLabel->setText("ETA: --:--");
    }
}

void MainWindow::onWorkerFinished(const QString &outPath) {
    progressBar->setValue(100);
    statusLabel->setText("Done.");
    speedLabel->setText("Speed: - KB/s");
    etaLabel->setText("ETA: --:--");
    // compute sizes and update chart
    qint64 orig = QFileInfo(currentFile).size();
    qint64 comp = QFileInfo(outPath).size();
    updateChart(orig, comp);
    QMessageBox::information(this, "Finished", "Operation completed.\nOutput: " + outPath);
}

void MainWindow::onWorkerError(const QString &msg) {
    statusLabel->setText("Error.");
    QMessageBox::critical(this, "Error", msg);
}

void MainWindow::updateChart(qint64 originalSize, qint64 compressedSize) {
    series->clear();
    QBarSet *set = new QBarSet("Bytes");
    *set << static_cast<qreal>(originalSize) << static_cast<qreal>(compressedSize);
    series->append(set);
    chart->removeAllSeries();
    chart->addSeries(series);
    chart->createDefaultAxes();
    chart->setTitle("Original vs Compressed (bytes)");
}
