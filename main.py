#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
VKMus
"""
from imports import *
import platform
if platform.system == "windows":
    import PyQt5
    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "bin"))
__version__ = "1.5"
cleanr = re.compile('\[.*?\]')
cleanr2 = re.compile('\(.*?\)')
STATES = ["media-playlist-repeat", "media-playlist-repeat-one", "media-playlist-shuffle"]
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
        try:
            covers = requests.get("https://itunes.apple.com/search", params={
                "term":clean_trackname(track),
            }).json()
        except Exception:
            return
        if covers["resultCount"] == 0:
            pass
        else:
            img = QImage()
            img.loadFromData(requests.get(covers["results"][0]["artworkUrl100"].replace("100x100", "135x135")).content)
            item.setIcon(QIcon(QPixmap(img)))

def time_convert(time):
    seconds = int(time / 1000)
    time = str(datetime.timedelta(seconds=seconds))
    if time.startswith("0:"):
        return time[2:]
    else:
        return time

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
        self.smallmode = False
        self.initUI()
        self.btnstate = 0
        self.cookie = None
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

    def erase_vk(self):
        dialog = QMessageBox(self)
        dialog.setIcon(dialog.Question)
        dialog.setText("Точно выйти из ВКонтакте?")
        dialog.addButton("Да", dialog.YesRole)
        dialog.addButton("Нет", dialog.NoRole)        
        if dialog.exec_() == 0:
            self.store.deleteAllCookies()
            dl = QMessageBox(self)
            dl.setText("Готово. VKMus будет перезапущен")
            dl.setIcon(dl.Information)
            dl.show()
            self.close()
            ex()


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
        erase_vk = QPushButton("Выйти из ВКонтакте")
        erase_vk.clicked.connect(self.erase_vk)
        self.settingsdial.lyt.addWidget(erase_vk)
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
        self.playerwdt.trackname.setText("%(artist)s\n%(title)s" % self.tracks[self.tracknum])
        self.trayicon.showMessage(self.tracks[self.tracknum]["artist"], self.tracks[self.tracknum]["title"], self.trayicon.NoIcon, 1000)
        self.setWindowTitle("%(artist)s - %(title)s" % self.tracks[self.tracknum])
        self.ctable.setCurrentRow(self.tracknum)
        self.player.play()
        self.player.setPosition(900)
        self.playerwdt.slider.setMaximum(int(self.tracks[self.tracknum]["duration"])*1000)
        self.playerwdt.tracklen.setText(time_convert(self.playerwdt.slider.maximum()))
        self.trayicon.setToolTip("%(artist)s - %(title)s" % self.tracks[self.tracknum])
        if self.tracks[self.tracknum]["cover"]:
            img = QImage()
            img.loadFromData(requests.get(self.tracks[self.tracknum]["cover"]).content)
            self.playerwdt.albumpic.setPixmap(QPixmap(img))
        else:
            self.playerwdt.albumpic.setPixmap(self.ctable.currentItem().icon().pixmap(QSize(135, 135)))
        if self.smallmode and self.tabs.isVisible():
            self.smode_trackop()

    def next_track(self):
        if self.btnstate == 0:
            if self.tracknum + 1 > len(self.tracks) - 1:
                self.tracknum = 0
            else:
                self.tracknum += 1
        elif self.btnstate == 2:
            self.tracknum = random.randint(0, len(self.tracks)-1)
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
            self.playerwdt.volumeicon.setIcon(self.style().standardIcon(self.style().SP_MediaVolumeMuted))
        else:
            self.playerwdt.volumeicon.setIcon(self.style().standardIcon(self.style().SP_MediaVolume))

    def button_shuffle(self):
        if self.btnstate + 1 == 3:
            self.btnstate = 0
        else:
            self.btnstate += 1
        if self.btnstate == 0:
            self.playerwdt.nextbtn.setDisabled(False)
            self.playerwdt.prevbtn.setDisabled(False)
        elif self.btnstate == 1:
            self.playerwdt.nextbtn.setDisabled(True)
            self.playerwdt.prevbtn.setDisabled(True)
        else:
            self.playerwdt.nextbtn.setDisabled(False)
            self.playerwdt.prevbtn.setDisabled(True)
        self.playerwdt.shuffle.setIcon(QIcon().fromTheme(STATES[self.btnstate]))

    def create_player_ui(self):
        self.pwidget = QWidget()
        self.pwidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored)
        self.playerwdt = player.Ui_Player()
        self.playerwdt.setupUi(self.pwidget)
        # Сигналы
        #self.playerwdt.volume.valueChanged.connect(self.vol_ctl)
        #self.playerwdt.volumeicon.clicked.connect(lambda: self.player.setMuted(not self.player.isMuted()))
        self.player.mutedChanged.connect(lambda muted:self.playerwdt.volumebtn.setIcon(self.style().standardIcon(self.style().SP_MediaVolumeMuted) if muted else self.style().standardIcon(self.style().SP_MediaVolume)))
        self.playerwdt.playbtn.clicked.connect(self.pbutton_hnd)
        self.playerwdt.prevbtn.clicked.connect(self.previous_track)
        self.playerwdt.nextbtn.clicked.connect(self.next_track)
        self.playerwdt.shuffle.released.connect(self.button_shuffle)
        self.main_box.addWidget(self.pwidget)
        self.playerwdt.goto_tracks.clicked.connect(self.smode_trackop)
        self.volumechanger = QWidgetAction(self.playerwdt.volumebtn)
        self.volumechanger.wdt = QWidget()
        self.volumechanger.setDefaultWidget(self.volumechanger.wdt)
        self.volumechanger.lyt = QHBoxLayout()
        self.volumechanger.wdt.setLayout(self.volumechanger.lyt)
        self.volumechanger.volume_text = QLabel(self.volumechanger.wdt)
        self.volumechanger.volume_text.setText("100")
        self.volumechanger.volume_slider = QSlider(Qt.Horizontal)
        self.volumechanger.volume_slider.setMaximum(100)
        self.volumechanger.volume_slider.setValue(100)
        self.volumechanger.volume_slider.valueChanged.connect(self.player.setVolume)
        self.volumechanger.lyt.addWidget(self.volumechanger.volume_text)
        self.volumechanger.lyt.addWidget(self.volumechanger.volume_slider)
        menu = QMenu()
        menu.addAction(self.volumechanger)
        self.mute_bt = menu.addAction('Выключить звук')
        self.mute_bt.triggered.connect(lambda:self.player.setMuted(not self.player.isMuted()))
        self.player.volumeChanged.connect(self.volume_changed)
        self.player.mutedChanged.connect(self.muted_changed)
        self.playerwdt.volumebtn.setPopupMode(self.playerwdt.volumebtn.InstantPopup)
        self.playerwdt.volumebtn.setMenu(menu)

    def muted_changed(self, muted):
        if muted:
            self.playerwdt.volumebtn.setIcon(QIcon.fromTheme("audio-volume-muted"))
            self.mute_bt.setText("Включить звук")
        else:
            self.volume_changed(self.player.volume())
            self.mute_bt.setText("Выключить звук")

    def volume_changed(self, volume):
        if self.player.isMuted() or volume == 0:
            self.playerwdt.volumebtn.setIcon(QIcon.fromTheme("audio-volume-muted"))
        elif volume > 75:
            self.playerwdt.volumebtn.setIcon(QIcon.fromTheme("audio-volume-high"))
        elif volume > 35:
            self.playerwdt.volumebtn.setIcon(QIcon.fromTheme("audio-volume-medium"))
        else:
            self.playerwdt.volumebtn.setIcon(QIcon.fromTheme("audio-volume-low"))
        self.volumechanger.volume_text.setText(str(volume))

    def smode_trackop(self):
        self.pwidget.setVisible(not self.pwidget.isVisible())
        self.goto_player.setVisible(not self.goto_player.isVisible())
        self.tabs.setVisible(not self.tabs.isVisible())

    def adaptive_tlist(self):
        if self.width() < 700:
            self.smallmode = True
            self.pwidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.tabs.hide()
            self.playerwdt.goto_tracks.show()
        else:
            self.smallmode = False
            self.tabs.show()
            self.pwidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored)
            self.playerwdt.goto_tracks.hide()

    def state_handle(self):
        if self.player.state() == self.player.StoppedState:
            if not self.dont_autoswitch:
                self.next_track()
        elif self.player.state() == self.player.PlayingState:
            self.playerwdt.playbtn.setIcon(self.style().standardIcon(self.style().SP_MediaPause))
            self.ppause_tray.setIcon(self.style().standardIcon(self.style().SP_MediaPause))
            self.ppause_tray.setText("Поставить на паузу")
        elif self.player.state() == self.player.PausedState:
            self.ppause_tray.setText("Играть")
            self.ppause_tray.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
            self.playerwdt.playbtn.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))

    def timechange(self, value):
        self.playerwdt.trackpos.setText(time_convert(value))

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
            action = menu.exec_(self.ctable.mapToGlobal(pos))
            if action == downact:
                track = self.tracks[self.ctable.indexFromItem(self.ctable.itemAt(pos)).row()]
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
                track = self.tracks[self.ctable.indexFromItem(self.ctable.itemAt(pos)).row()]
                audio.track_mgmt("delete", self.cookie, track["mgmtid"])
                del self.tracks[self.ctable.indexFromItem(self.ctable.itemAt(pos)).row()]
                self.write_into_table()
            elif action == addact:
                track = self.tracks[self.ctable.indexFromItem(self.ctable.itemAt(pos)).row()]
                audio.track_mgmt("add", self.cookie, track["mgmtid"])
            self.menulock = False

    def write_into_table(self):
        self.ctable.clear()
        self.ctable.setSortingEnabled(False)
        self.ctable.setIconSize(QSize(45,45))
        self.ctable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ctable.customContextMenuRequested.connect(self.downmenu)
        for track in self.tracks:
            item = QListWidgetItem("%(artist)s\n%(title)s" % track)
            self.ctable.addItem(item)
            threading.Thread(target=setCover, args=(self, item, track)).start()
        self.ctable.setCurrentRow(0)
        self.ctable.itemDoubleClicked.connect(self.switch_track)
        self.ctable.setEditTriggers(self.ctable.NoEditTriggers)
        self.ctable.setSelectionBehavior(self.ctable.SelectRows)
        self.ctable.setSelectionMode(self.ctable.SingleSelection)
        self.ctable.setSortingEnabled(True)
        self.ctable.setStyleSheet("""
        QTableWidget::item:hover {
            background-color:!important;
        }
        """)
        self.tracknum = 0

    def update_table(self, index, inthread=False):
        self.ctable = self.tabs.currentWidget().table
        self.tabs.currentWidget().loading.show()
        self.ctable.hide()
        if inthread:
            self.tracks = audio.audio_get(self.cookie, playlist=self.playlists[index]["url"])[0]
            self.write_into_table()
            self.tabs.currentWidget().loading.hide()
            self.ctable.show()
        else:
            threading.Thread(target=self.update_table, args=(index, True)).start()

    def resizeEvent(self, event):
        if self.cookie:
            self.adaptive_tlist()

    def new_cookie(self, cookie):
        if cookie.name() == "remixsid":
            splash = QSplashScreen(self, self.app_icon.pixmap(512, 512))
            splash.show()
            self.hide()
            menu = self.trayicon.contextMenu()
            self.ppause_tray = menu.addAction("Играть")
            self.ppause_tray.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
            self.ppause_tray.triggered.connect(self.pbutton_hnd)
            next = menu.addAction("Следующий трек")
            next.setIcon(self.style().standardIcon(self.style().SP_MediaSkipForward))
            next.triggered.connect(self.next_track)
            prev = menu.addAction("Предыдущий трек")
            prev.setIcon(self.style().standardIcon(self.style().SP_MediaSkipBackward))
            prev.triggered.connect(self.previous_track)
            self.cookie = str(cookie.value(), 'utf-8')
            self.tracks, self.playlists = audio.audio_get(self.cookie)
            self.web.hide()
            self.log_label.close()
            self.player = QMediaPlayer()
            self.create_player_ui()
            self.player.positionChanged.connect(self.playerwdt.slider.setValue)
            self.player.stateChanged.connect(self.state_handle)
            self.playerwdt.slider.sliderReleased.connect(self.changepos)
            self.playerwdt.slider.valueChanged.connect(self.timechange)
            self.tabs = QTabWidget()
            loading = QtWaitingSpinner(None)
            loading.setColor(app.palette().light())
            for playlist in self.playlists:
                t = QWidget()
                t_l = QVBoxLayout()
                t.setLayout(t_l)
                t.loading = loading
                t.table = QListWidget()
                t_l.addWidget(t.loading)
                t_l.addWidget(t.table)
                self.tabs.addTab(t, playlist["name"])
            self.tabs.setCurrentIndex(0)
            self.ctable = self.tabs.currentWidget().table
            self.write_into_table()
            trackslen = 0
            for track in self.tracks:
                trackslen += int(track["duration"])
            self.tabs.setTabPosition(self.tabs.East)
            self.tabs.currentChanged.connect(self.update_table)
            self.main_box.addWidget(self.tabs)
            self.set_track()
            self.player.pause()
            self.searchtb = self.toolbar.addAction("Поиск")
            self.toolbar.addAction("Настройки").triggered.connect(self.settingswin)
            self.searchtb.triggered.connect(self.search)
            self.toolbar.addAction("О программе").triggered.connect(self.about)
            self.goto_player = QToolButton()
            self.goto_player.setFocusPolicy(Qt.NoFocus)
            self.goto_player.setToolButtonStyle(Qt.ToolButtonFollowStyle)
            self.goto_player.setAutoRaise(True)
            self.goto_player.setArrowType(Qt.LeftArrow)
            self.goto_player.setText("Назад в плеер")
            self.goto_player.clicked.connect(self.smode_trackop)
            self.goto_player.hide()
            self.corelyt.insertWidget(1,self.goto_player)
            splash.hide()
            self.adaptive_tlist()
        self.show()

    def switch_track(self,track):
        self.tracknum = self.ctable.row(track) - 2
        self.set_track()

    def changepos(self):
        self.player.setPosition(self.playerwdt.slider.value())

    def about(self, _):
        QMessageBox.about(self, "О программе","""
        <p align="center">VKMus %s</p>
        <ul>
        <li>Обложки достаются с iTunes, спасибо Apple за их API</li>
        <li>Сделано на PyQt5.</li>
        <li>Иконка - эмодзи арбуза из Firefox OS</li>
        </ul>
        """ % __version__)

    def continuesearch_thread(self, value):
        maxval = self.ctable.verticalScrollBar().maximum()
        if value/maxval > 0.7:
            self.offset += 50
            self.tracks += audio.audio_get(self.cookie, self.searchq, self.offset, self.no_vasyan)
            self.write_into_table()

    def continuesearch(self, value):
        threading.Thread(target=self.continuesearch_thread, args=[value]).start()

    def exitsearch(self, _):
        self.searchtb.triggered.disconnect(self.exitsearch)
        self.searchtb.triggered.connect(self.search)
        self.searchtb.setText("Поиск")
        self.ctable.verticalScrollBar().valueChanged.disconnect(self.continuesearch)
        self.tracks, self.playlists = audio.audio_get(self.cookie)
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
            self.tracks, self.playlists = audio.audio_get(self.cookie, self.searchq, 0, self.no_vasyan)
            self.tracknum = 0
            self.player.stop()
            self.player.pause()
            self.ctable.verticalScrollBar().valueChanged.connect(self.continuesearch)
            self.write_into_table()
            self.searchtb.setText("Выйти из поиска")
            self.searchtb.triggered.disconnect()
            self.searchtb.triggered.connect(self.exitsearch)


    def closeEvent(self, event):
        print("About to quit")
        self.trayicon.hide()
        self.trayicon.deleteLater()
        self.settings.setValue("geometry", self.saveGeometry())

    def initUI(self):
        self.small_lyt = QHBoxLayout()
        self.app_icon = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.png"))
        self.trayicon = QSystemTrayIcon(self.app_icon)
        self.trayicon.setContextMenu(QMenu())
        self.trayicon.show()
        self.setWindowIcon(self.app_icon)
        self.toolbar = QMenuBar()
        self.toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.corelyt = QVBoxLayout()
        self.corelyt.addWidget(self.toolbar)
        mainwdt = QWidget()
        self.main_box = QHBoxLayout()
        mainwdt.setLayout(self.main_box)
        self.web = QWebEngineView()
        self.web.load(QUrl("http://m.vk.com"))
        self.web.show()
        self.store = self.web.page().profile().cookieStore()
        self.store.cookieAdded.connect(self.new_cookie)
        self.setLayout(self.corelyt)
        self.log_label = QLabel("Авторизуйтесь в мобильной версии ВК для начала")
        self.corelyt.addWidget(self.log_label)
        self.corelyt.addWidget(self.web)
        self.corelyt.addWidget(mainwdt)
        self.setGeometry(600, 600, 800, 600)
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        self.setWindowTitle('VKMus')
        self.main_box.setObjectName("body")

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
    print("".join(traceback.format_tb(tb)))
    raise SystemExit

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(os.getpid())
    app.setApplicationVersion(__version__)
    app.setApplicationName("VKMus")
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
