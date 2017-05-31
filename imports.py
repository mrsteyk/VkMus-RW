import os
import re
import sys
import threading
import time

import requests
from hurry.filesize import size
from pygs import QxtGlobalShortcut
from PyQt5.QtCore import QSettings, QSize, Qt, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap, QStandardItemModel, QKeySequence
from PyQt5.QtMultimedia import QAudioProbe, QMediaContent, QMediaPlayer
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkReply,
                             QNetworkRequest)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDialog, QSystemTrayIcon, 
                             QFileDialog, QHBoxLayout, QKeySequenceEdit,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMenu, QMenuBar, QMessageBox, QProgressDialog,
                             QPushButton, QSlider, QStyleFactory, QToolButton,
                             QVBoxLayout, QWidget)

import audio
