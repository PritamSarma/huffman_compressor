#ifndef WORKER_H
#define WORKER_H

#include <QObject>
#include <QString>

class Worker : public QObject {
    Q_OBJECT
public:
    explicit Worker(QObject* parent = nullptr);
    ~Worker();

    void setPaths(const QString &in, const QString &out);
    void setModeCompress(bool c);

public slots:
    void process(); // runs in background thread

signals:
    void progress(int percent);
    void finished(const QString &outPath);
    void error(const QString &message);

private:
    QString inputPath;
    QString outputDir;
    bool modeCompress{true};
};

#endif // WORKER_H
