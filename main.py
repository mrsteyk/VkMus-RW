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
            pass;
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
        self.tracknum = 0
        self.offset = 0
        self.downloader = QNetworkAccessManager()
        self.initUI()
        self.dont_autoswitch = False
        self.no_vasyan = False
        self.menulock = False
        self.settings = QSettings("OctoNezd", "VKMus")

    def pbutton_hnd(self):
        if self.player.state() == self.player.PausedState:
            self.player.play()
        else:
            self.player.pause()

    def settingswin(self):
        return
        #self.settingsdial = QDialog(self)
        #self.settingsdial.lyt = QVBoxLayout()
        #self.settingsdial.hotkeytable = QTableWidget()
        #self.settingsdial.lyt.addWidget(self.settingsdial.hotkeytable)

    def set_track(self):
        self.player.setMedia(QMediaContent(QUrl(self.tracks[self.tracknum]["url"])))
        self.trackname.setText("%(artist)s - %(title)s" % self.tracks[self.tracknum])
        self.table.setCurrentRow(self.tracknum)
        self.player.play()
        self.slider.setMaximum(int(self.tracks[self.tracknum]["duration"])*1000)
        self.tracklen.setText(time_convert(self.slider.maximum()))
        if self.tracks[self.tracknum]["cover"]:
            img = QImage()
            img.loadFromData(requests.get(self.tracks[self.tracknum]["cover"]).content)
            self.albumpic.setPixmap(QPixmap(img))
        else:
            self.albumpic.setPixmap(self.table.currentItem().icon().pixmap(QSize(135,135)))

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

    def create_player_ui(self):
        # Виджет плеера
        self.player = QWidget()
        self.player_body = QHBoxLayout()
        self.player.setLayout(self.player_body)
        self.playerwdt = QWidget()
        self.player.setObjectName("player")
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
        self.player.setMaximumHeight(155)
        self.slider = QSlider(Qt.Horizontal)
        self.tracklen = QLabel()
        self.trackpos = QLabel()
        # Кнопки управления
        self.controls = QWidget()
        self.controlslyt = QHBoxLayout()
        self.playbtn = QToolButton()
        self.prevbtn = QToolButton()
        self.nextbtn = QToolButton()
        # Позиция
        self.pos = QWidget()
        self.poslyt = QHBoxLayout()
        self.pos.setLayout(self.poslyt)
        # Иконки
        self.playbtn.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.playbtn.setFixedSize(40, 40)
        self.prevbtn.setIcon(self.style().standardIcon(self.style().SP_MediaSkipBackward))
        self.nextbtn.setIcon(self.style().standardIcon(self.style().SP_MediaSkipForward))
        # Сигналы
        self.playbtn.clicked.connect(self.pbutton_hnd)
        self.prevbtn.clicked.connect(self.previous_track)
        self.nextbtn.clicked.connect(self.next_track)
        # Добавляем
        self.controlslyt.addStretch()
        self.controlslyt.addWidget(self.prevbtn)
        self.controlslyt.addWidget(self.playbtn)
        self.controlslyt.addWidget(self.nextbtn)
        self.controlslyt.addStretch()
        self.playerwdt.setLayout(self.playerlyt)
        self.playerlyt.addWidget(self.trackname)
        self.poslyt.addWidget(self.trackpos)
        self.poslyt.addWidget(self.slider)
        self.poslyt.addWidget(self.tracklen)
        self.playerlyt.addWidget(self.pos)
        self.playerlyt.addWidget(self.controls)
        self.controls.setLayout(self.controlslyt)
        self.main_box.addWidget(self.player)

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
        i = 0
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
            self.create_player_ui()
            self.tracks = audio.audio_get(self.cookie)
            self.web.close()
            self.log_label.close()
            self.player = QMediaPlayer()
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
            self.tracknum = 0
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
        about.setTextFormat(Qt.RichText)
        about.setText("""
        VKMus v0.1<br><br>
        Обложки достаются с iTunes, спасибо Apple за их API<br><br>
        Сделано на PyQt5.<br><br>
        Иконка - эмодзи арбуза из Firefox OS
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


    def initUI(self):
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.png")))
        self.toolbar = QMenuBar()
        self.searchtb = self.toolbar.addAction("Поиск")
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


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = vkmus()
    sys.exit(app.exec_())
