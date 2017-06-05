import datetime
import os
import random
import re
import sys
import threading
import time
import traceback

import requests
from hurry.filesize import size
from PyQt5.QtCore import QSettings, QSize, Qt, QUrl
from PyQt5.QtGui import (QIcon, QImage, QKeySequence, QPixmap,
                         QStandardItemModel)
from PyQt5.QtMultimedia import QAudioProbe, QMediaContent, QMediaPlayer
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkReply,
                             QNetworkRequest)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDialog,
                             QFileDialog, QHBoxLayout, QKeySequenceEdit,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMenu, QMenuBar, QMessageBox, QProgressBar,
                             QProgressDialog, QPushButton, QSizePolicy,
                             QSlider, QSplashScreen, QStyleFactory,
                             QSystemTrayIcon, QTabWidget, QToolButton,
                             QVBoxLayout, QWidget, QWidgetAction)

import audio
import player
from waitingspinnerwidget import QtWaitingSpinner
