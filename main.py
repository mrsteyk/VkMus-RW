#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
VKMus
"""
from imports import *
cleanr = re.compile('\[.*?\]')
cleanr2 = re.compile('\(.*?\)')
def clean_trackname(track):
    return re.sub(cleanr2, '', re.sub(cleanr,'', "%(artist)s %(title)s" % track).replace("OST",""))

def setCover(window, item, track):
    """
    Ставит обложки в листе
    """
    item.setIcon(window.style().standardIcon(window.style().SP_DriveCDIcon))
    if track["cover"]:
        img = QImage()
        img.loadFromData(requests.get(track["cover"]).content)
        item.setIcon(QIcon(QPixmap(img)))
    else:
        covers = requests.get("https://itunes.apple.com/search", params={
            "term":clean_trackname(track),
        }).json()
        if covers["resultCount"] == 0:
            pass
        else:
            img = QImage()
            img.loadFromData(requests.get(covers["results"][0]["artworkUrl100"].replace("100x100", "135x135")).content)
            item.setIcon(QIcon(QPixmap(img)))

def time_convert(time):
    seconds = time / 1000
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

class vkmus(QWidget):

    def __init__(self):
        super().__init__()
        self.offset = 0
        self.downloader = QNetworkAccessManager()
        self.dont_autoswitch = False
        self.no_vasyan = False
        self.menulock = False
        self.settings = QSettings("OctoNezd", "VKMus")
        self.tracknum = int(self.settings.value("last_track", 0))
        self.initUI()
        shortcut_play.activated.connect(self.pbutton_hnd)
        shortcut_next.activated.connect(self.next_track)
        shortcut_prev.activated.connect(self.previous_track)


    def pbutton_hnd(self):
        if self.player.state() == self.player.PausedState:
            self.player.play()
        else:
            self.trayicon.showMessage("VKMus", "Пауза", QSystemTrayIcon.NoIcon, 2000)
            self.player.pause()


    def setHotkeys(self):
        return

    def settingswin(self):
        self.settingsdial = QDialog(self)
        self.settingsdial.setWindowTitle("Настройки")
        self.settingsdial.lyt = QVBoxLayout()
        self.settingsdial.keyseq_play = QKeySequenceEdit(self.settings.value("h_play", QKeySequence(Qt.Key_MediaPlay)))
        self.settingsdial.keyseq_next = QKeySequenceEdit(self.settings.value("h_next", QKeySequence(Qt.Key_MediaNext)))
        self.settingsdial.keyseq_prev = QKeySequenceEdit(self.settings.value("h_prev", QKeySequence(Qt.Key_MediaPrevious)))
        self.settingsdial.setLayout(self.settingsdial.lyt)
        self.settingsdial.lyt.addWidget(QLabel("Приостановить/Запустить"))
        self.settingsdial.lyt.addWidget(self.settingsdial.keyseq_play)
        self.settingsdial.lyt.addWidget(QLabel("Следующий трек"))
        self.settingsdial.lyt.addWidget(self.settingsdial.keyseq_next)
        self.settingsdial.lyt.addWidget(QLabel("Предыдущий трек"))
        self.settingsdial.lyt.addWidget(self.settingsdial.keyseq_prev)
        exbtn = QPushButton("Сохранить")
        self.settingsdial.setFocusPolicy(Qt.NoFocus)
        self.settingsdial.setFocus(Qt.NoFocusReason)
        self.settingsdial.lyt.addWidget(exbtn)
        exbtn.clicked.connect(self.settingsdial.accept)
        if self.settingsdial.exec_() != 0:
            print("Setting new hotkeys")
            self.settings.setValue("h_play", QKeySequence(self.settingsdial.keyseq_play.keySequence()[0]))
            shortcut_play.setShortcut(settings.value("h_play", QKeySequence(Qt.Key_MediaPlay)))    
            self.settings.setValue("h_next", QKeySequence(self.settingsdial.keyseq_next.keySequence()[0]))
            shortcut_next.setShortcut(settings.value("h_next", QKeySequence(Qt.Key_MediaPlay)))    
            self.settings.setValue("h_prev", QKeySequence(self.settingsdial.keyseq_prev.keySequence()[0]))
            shortcut_prev.setShortcut(settings.value("h_prev", QKeySequence(Qt.Key_MediaPlay)))    

    def set_track(self):
        self.settings.setValue("last_track", self.tracknum)
        self.player.setMedia(QMediaContent(QUrl(self.tracks[self.tracknum]["url"])))
        self.trackname.setText("%(artist)s - %(title)s" % self.tracks[self.tracknum])
        self.trayicon.showMessage(self.tracks[self.tracknum]["artist"], self.tracks[self.tracknum]["title"], self.trayicon.NoIcon, 1000)
        self.setWindowTitle("%(artist)s - %(title)s" % self.tracks[self.tracknum])
        self.table.setCurrentRow(self.tracknum)
        self.player.play()
        self.player.setPosition(900)
        self.slider.setMaximum(int(self.tracks[self.tracknum]["duration"])*1000)
        self.tracklen.setText(time_convert(self.slider.maximum()))
        if self.tracks[self.tracknum]["cover"]:
            img = QImage()
            img.loadFromData(requests.get(self.tracks[self.tracknum]["cover"]).content)
            self.albumpic.setPixmap(QPixmap(img))
        else:
            self.albumpic.setPixmap(self.table.currentItem().icon().pixmap(QSize(135, 135)))

    def next_track(self):
        if self.tracknum + 1 > len(self.tracks) - 1:
            self.tracknum = 0
        else:
            self.tracknum += 1
        self.dont_autoswitch = True
        self.set_track()
        self.dont_autoswitch = False

    def previous_track(self):
        if self.tracknum - 1 < 0:
            self.tracknum = len(self.tracks) - 1
        else:
            self.tracknum -= 1
        self.dont_autoswitch = True
        self.set_track()
        self.dont_autoswitch = False

    def vol_ctl(self, vol):
        self.player.setVolume(vol)
        if vol == 0:
            self.volumeicon.setIcon(self.style().standardIcon(self.style().SP_MediaVolumeMuted))
        else:
            self.volumeicon.setIcon(self.style().standardIcon(self.style().SP_MediaVolume))

    def create_player_ui(self):
        # Виджет плеера
        player = QWidget()
        self.player_body = QHBoxLayout()
        player.setLayout(self.player_body)
        self.playerwdt = QWidget()
        player.setObjectName("player")
        self.albumpic = QLabel()
        self.albumpic.setAlignment(Qt.AlignCenter)
        self.albumpic.setMinimumWidth(135)
        self.albumpic.setMaximumWidth(135)
        self.albumpic.setMinimumHeight(135)
        self.albumpic.setMaximumHeight(135)
        self.player_body.addWidget(self.albumpic)
        self.player_body.addWidget(self.playerwdt)
        self.playerlyt = QVBoxLayout()
        self.trackname = QLabel()
        self.trackname.setAlignment(Qt.AlignCenter)
        player.setMaximumHeight(155)
        self.slider = QSlider(Qt.Horizontal)
        self.tracklen = QLabel()
        self.trackpos = QLabel()
        # Кнопки управления
        self.controls = QWidget()
        self.controlslyt = QHBoxLayout()
        self.playbtn = QToolButton()
        self.prevbtn = QToolButton()
        self.nextbtn = QToolButton()
        self.volumeicon = QToolButton()
        self.volume = QSlider(Qt.Horizontal)
        self.player.setVolume(int(self.settings.value("volume", 100)))
        self.volume.setValue(self.player.volume())
        self.volume.valueChanged.connect(self.vol_ctl)
        # Позиция
        self.pos = QWidget()
        self.poslyt = QHBoxLayout()
        self.pos.setLayout(self.poslyt)
        # Иконки
        self.playbtn.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.volumeicon.setIcon(self.style().standardIcon(self.style().SP_MediaVolume))
        self.playbtn.setFixedSize(40, 40)
        self.prevbtn.setIcon(self.style().standardIcon(self.style().SP_MediaSkipBackward))
        self.nextbtn.setIcon(self.style().standardIcon(self.style().SP_MediaSkipForward))
        # Сигналы
        self.volumeicon.clicked.connect(lambda: self.player.setMuted(not self.player.isMuted()))
        self.player.mutedChanged.connect(lambda muted:self.volumeicon.setIcon(self.style().standardIcon(self.style().SP_MediaVolumeMuted) if muted else self.style().standardIcon(self.style().SP_MediaVolume)))
        self.playbtn.clicked.connect(self.pbutton_hnd)
        self.prevbtn.clicked.connect(self.previous_track)
        self.nextbtn.clicked.connect(self.next_track)
        # Добавляем
        self.controlslyt.addStretch()
        self.controlslyt.addWidget(self.prevbtn)
        self.controlslyt.addWidget(self.playbtn)
        self.controlslyt.addWidget(self.nextbtn)
        self.controlslyt.addStretch()
        self.controlslyt.addWidget(self.volumeicon)
        self.controlslyt.addWidget(self.volume)
        self.playerwdt.setLayout(self.playerlyt)
        self.controlslyt.insertSpacing(0, self.volume.sizeHint().width() + self.volumeicon.sizeHint().width())
        self.playerlyt.addWidget(self.trackname)
        self.poslyt.addWidget(self.trackpos)
        self.poslyt.addWidget(self.slider)
        self.poslyt.addWidget(self.tracklen)
        self.playerlyt.addWidget(self.pos)
        self.playerlyt.addWidget(self.controls)
        self.controls.setLayout(self.controlslyt)
        self.main_box.addWidget(player)

    def state_handle(self):
        if self.player.state() == self.player.StoppedState:
            if not self.dont_autoswitch:
                self.next_track()
        elif self.player.state() == self.player.PlayingState:
            self.playbtn.setIcon(self.style().standardIcon(self.style().SP_MediaPause))
        elif self.player.state() == self.player.PausedState:
            self.playbtn.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))

    def timechange(self, value):
        self.trackpos.setText(time_convert(value))

    def progress_control(self, received, total):
        self.progress.setMaximum(total)
        self.progress.setValue(received)

    def download_finished(self):
        successdialog = QMessageBox()
        successdialog.setText("Загрузка %(artist)s - %(title)s завершена!")
        successdialog.setWindowTitle("Загрузка завершена")
        successdialog.setIcon(successdialog.Information)
        with open(self.path, 'wb') as f:
            f.write(self.curdown.readAll())
        successdialog.show()

    def downmenu(self, pos):
        if not self.menulock:
            self.menulock = True
            menu = QMenu()
            downact = menu.addAction("Скачать")
            if self.searchtb.text() == "Поиск":
                removeact = menu.addAction("Удалить")
                addact = 0
            else:
                removeact = 0
                addact = menu.addAction("Добавить")
            action = menu.exec_(self.table.mapToGlobal(pos))
            if action == downact:
                track = self.tracks[self.table.itemAt(pos).row()]
                self.path, _ = QFileDialog.getSaveFileName(None, "Куда скачать?",
                                                    "%(artist)s - %(title)s.mp3" % track,
                                                    "MPEG-1/2/2.5 Layer 3 (*.mp3)")
                if self.path == "":
                    return
                self.curdown = self.downloader.get(QNetworkRequest(QUrl(track["url"])))
                self.progress = QProgressDialog()
                self.progress.setWindowTitle("Загрузка %(artist)s - %(title)s" % track)
                self.progress.setLabel(QLabel("Загрузка %(artist)s - %(title)s" % track))
                self.progress.canceled.connect(self.curdown.close)
                self.curdown.downloadProgress.connect(self.progress_control)
                self.curdown.finished.connect(self.download_finished)
                self.progress.show()
            elif action == removeact:
                track = self.tracks[self.table.itemAt(pos).row()]
                audio.track_mgmt("delete", self.cookie, track["mgmtid"])
                del self.tracks[self.table.itemAt(pos).row()]
                self.write_into_table()
            elif action == addact:
                track = self.tracks[self.table.itemAt(pos).row()]
                audio.track_mgmt("add", self.cookie, track["mgmtid"])
            self.menulock = False

    def write_into_table(self):
        self.table.setIconSize(QSize(45,45))
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.downmenu)
        for track in self.tracks:
            item = QListWidgetItem("%(artist)s\n%(title)s" % track)
            self.table.addItem(item)
            threading.Thread(target=setCover, args=(self, item, track)).start()
        self.table.setCurrentRow(0)

    def visual(self, buf):
        return
        print(buf.data())

    def new_cookie(self, cookie):
        if cookie.name() == "remixsid":
            print("Auth complete")
            self.cookie = str(cookie.value(), 'utf-8')
            self.tracks = audio.audio_get(self.cookie)
            self.web.close()
            self.log_label.close()
            self.player = QMediaPlayer()
            self.create_player_ui()
            self.player.positionChanged.connect(self.slider.setValue)
            self.player.stateChanged.connect(self.state_handle)
            self.slider.sliderReleased.connect(self.changepos)
            self.slider.valueChanged.connect(self.timechange)
            self.table = QListWidget()
            self.write_into_table()
            self.table.itemDoubleClicked.connect(self.switch_track)
            self.table.setEditTriggers(self.table.NoEditTriggers)
            self.table.setSelectionBehavior(self.table.SelectRows)
            self.table.setSelectionMode(self.table.SingleSelection)
            self.table.setSortingEnabled(True)
            self.table.setStyleSheet("""
            QTableWidget::item:hover {
                background-color:!important;
            }
            """)
            trackslen = 0
            for track in self.tracks:
                trackslen += int(track["duration"])
            self.main_box.addWidget(self.table)
            trackinfo = QLabel("%s треков, %s, примерно %s" % (
                len(self.tracks),
                time_convert(trackslen * 1000),
                size(trackslen * 128 * 192)
            ))
            trackinfo.setObjectName("trackcount")
            self.main_box.addWidget(trackinfo)
            self.set_track()
            self.player.pause()
            self.player.probe = QAudioProbe()
            self.player.probe.setSource(self.player)
            self.player.probe.audioBufferProbed.connect(self.visual)

    def switch_track(self,track):
        self.tracknum = self.table.row(track) - 2
        self.set_track()

    def changepos(self):
        self.player.setPosition(self.slider.value())

    def about(self, _):
        about = QMessageBox(self)
        about.setWindowTitle("О программе")
        about.setIconPixmap(self.app_icon.pixmap(QSize(150, 150)))
        about.setTextFormat(Qt.RichText)
        about.setText("""
        <p align="center">VKMus v1.0</p>
        <ul>
        <li>Обложки достаются с iTunes, спасибо Apple за их API</li>
        <li>Сделано на PyQt5.</li>
        <li>Иконка - эмодзи арбуза из Firefox OS</li>
        </ul>
        """)
        about.show()

    def continuesearch_thread(self, value):
        maxval = self.table.verticalScrollBar().maximum()
        if value/maxval > 0.7:
            print("Обновляем результаты")
            self.offset += 50
            self.tracks += audio.audio_get(self.cookie, self.searchq, self.offset, self.no_vasyan)
            self.write_into_table()

    def continuesearch(self, value):
        threading.Thread(target=self.continuesearch_thread, args=[value]).start()

    def exitsearch(self, _):
        self.searchtb.triggered.disconnect(self.exitsearch)
        self.searchtb.triggered.connect(self.search)
        self.searchtb.setText("Поиск")
        self.table.verticalScrollBar().valueChanged.disconnect(self.continuesearch)
        self.tracks = audio.audio_get(self.cookie)
        self.offset = 0
        self.player.stop()
        self.player.pause()
        self.write_into_table()

    def search(self, _):
        dialog = QDialog(self)
        dialoglyt = QVBoxLayout()
        dialog.setLayout(dialoglyt)
        dialog.textIn = QLineEdit()
        dialog.ok = QPushButton("Искать")
        dialog.ok.clicked.connect(dialog.accept)
        dialog.cancel = QPushButton("Отмена")
        dialog.cancel.clicked.connect(dialog.reject)
        dialog.vasyan = QCheckBox("Не показывать ремиксы?")
        btns = QWidget()
        btnlyt = QHBoxLayout()
        btns.setLayout(btnlyt)
        btnlyt.addWidget(dialog.cancel)
        btnlyt.addWidget(dialog.ok)
        dialog.textIn.returnPressed.connect(dialog.accept)
        dialoglyt.addWidget(dialog.textIn)
        dialoglyt.addWidget(dialog.vasyan)
        dialoglyt.addWidget(btns)
        if dialog.exec_() == 0:
            return
        else:
            self.no_vasyan = dialog.vasyan.isChecked()
            self.searchq = dialog.textIn.text()
            self.tracks = audio.audio_get(self.cookie, self.searchq, 0, self.no_vasyan)
            self.tracknum = 0
            self.player.stop()
            self.player.pause()
            self.table.verticalScrollBar().valueChanged.connect(self.continuesearch)
            self.write_into_table()
            self.searchtb.setText("Выйти из поиска")
            self.searchtb.triggered.disconnect()
            self.searchtb.triggered.connect(self.exitsearch)


    def closeEvent(self, event):
        print("About to quit")
        self.trayicon.hide()
        self.trayicon.deleteLater()

    def initUI(self):
        self.app_icon = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.png"))
        self.trayicon = QSystemTrayIcon(self.app_icon)
        self.trayicon.show()
        self.setWindowIcon(self.app_icon)
        self.toolbar = QMenuBar()
        self.searchtb = self.toolbar.addAction("Поиск")
        self.toolbar.addAction("Настройки").triggered.connect(self.settingswin)
        self.searchtb.triggered.connect(self.search)
        self.toolbar.addAction("О программе").triggered.connect(self.about)
        self.main_box = QVBoxLayout()
        self.main_box.addWidget(self.toolbar)
        self.web = QWebEngineView()
        self.web.load(QUrl("http://m.vk.com"))
        self.web.show()
        self.store = self.web.page().profile().cookieStore()
        self.store.cookieAdded.connect(self.new_cookie)
        self.setLayout(self.main_box)
        self.log_label = QLabel("Авторизуйтесь в мобильной версии ВК для начала")
        self.main_box.addWidget(self.log_label)
        self.main_box.addWidget(self.web)
        self.setGeometry(600, 600, 800, 600)
        self.setWindowTitle('VKMus')
        self.main_box.setObjectName("body")
        self.setStyleSheet("""
        #body {
            margin:0;
        }
        #player {
            border-bottom:1px solid grey;
        }
        #trackcount {
            border-top:1px solid grey;
        }
        """)
        self.show()
        self.setHotkeys()

def excepthook(type, error, tb):
    print("Excepthook jumps in")
    errorbox = QMessageBox()
    errorbox.setWindowTitle("Критическая ошибка!")
    errorbox.setTextFormat(Qt.RichText)
    errorbox.setText("Название ошибки: " + str(error) +
                     "<br>Следующая информация возможно пригодится разработчику:<pre>" +
                     "".join(traceback.format_tb(tb))  + "</pre>"
                     '<a href="http://vk.com/42link">Ссылка на профиль разработчика ВК</a><br>'
                     '<a href="http://t.me/octonezd">Ссылка на профиль разработчика в Telegram</a><br>'
                     '<a href="https://github.com/OctoNezd/vkmus/issues">Багтрекер плеера</a>')
    errorbox.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = excepthook
    print("Setting hotkeys")
    settings = QSettings("OctoNezd", "VKMus")    
    shortcut_play = QxtGlobalShortcut()
    shortcut_play.setShortcut(settings.value("h_play", QKeySequence(Qt.Key_MediaPlay)))
    shortcut_next = QxtGlobalShortcut()
    shortcut_next.setShortcut(settings.value("h_next", QKeySequence(Qt.Key_MediaPlay)))
    shortcut_prev = QxtGlobalShortcut()
    shortcut_prev.setShortcut(settings.value("h_prev", QKeySequence(Qt.Key_MediaPlay)))
    ex = vkmus()
    res = app.exec_()
    sys.exit(res)
