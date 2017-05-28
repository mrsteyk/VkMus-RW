import re
import sys
import threading
import time
import queue

import requests
import simplejson
from hurry.filesize import size
from PyQt5.QtCore import QSettings, QSize, Qt, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap, QStandardItemModel
from PyQt5.QtMultimedia import QAudioProbe, QMediaContent, QMediaPlayer
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkReply,
                             QNetworkRequest)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDialog,
                             QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMenu, QMenuBar,
                             QMessageBox, QProgressDialog, QPushButton,
                             QSlider, QStyleFactory, QToolButton, QVBoxLayout,
                             QWidget)

import audio
