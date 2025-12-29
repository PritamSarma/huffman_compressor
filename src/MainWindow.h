#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QThread>
#include <QtCharts>

QT_CHARTS_USE_NAMESPACE

class Worker;

namespace Ui { class MainWindow; }

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

protected:
    void dragEnterEvent(QDragEnterEvent *event) override;
    void dropEvent(QDropEvent *event) override;

private slots:
    void on_chooseFileButton_clicked();
    void on_chooseOutputButton_clicked();
    void on_modeButton_clicked(); // toggles between Compress / Decompress
    void startProcessing(bool compressMode);
    void onWorkerProgress(int percent);
    void onWorkerFinished(const QString &outPath);
    void onWorkerError(const QString &msg);

private:
    QWidget *centralWidget;
    QPushButton *chooseFileButton;
    QPushButton *chooseOutputButton;
    QPushButton *modeButton;
    QLabel *fileLabel;
    QLabel *outputLabel;
    QProgressBar *progressBar;
    QLabel *statusLabel;
    QLabel *speedLabel;
    QLabel *etaLabel;
    QChartView *chartView;
    QChart *chart;
    QBarSeries *series;

    QString currentFile;
    QString outputDir;
    QThread *workerThread;
    Worker *worker;
    QElapsedTimer timer;
    qint64 totalSize;
    qint64 lastProcessedEstimate;

    void setupUi();
    void updateChart(qint64 originalSize, qint64 compressedSize);
};

#endif // MAINWINDOW_H
