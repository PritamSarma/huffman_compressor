cmake_minimum_required(VERSION 3.16)
project(huffman_qt VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Charts Core Gui)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

add_executable(huffman-qt
    src/main.cpp
    src/MainWindow.h
    src/MainWindow.cpp
    src/Worker.h
    src/Worker.cpp
    src/huffman.h
    src/huffman.cpp
)

target_link_libraries(huffman-qt PRIVATE Qt6::Widgets Qt6::Charts Qt6::Core Qt6::Gui)
