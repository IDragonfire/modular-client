#!/usr/bin/env python

## 

#######################################################################

##

##  Blah1234 - example of video player in Phonon Qt4 module  

##  Copyright (C) ~~~ Qt4 birth year ~~~ by t00l (http://g55y.blogspot.com)

##

##  But I was something like 2 years younger and much more stupid back then,

##  than I'm now. As least I think so. Probably.

##

##  This program is free software: you can redistribute it and/or modify

##  it under the terms of the GNU General Public License as published by

##  the Free Software Foundation, either version 3 of the License, or

##  (at your option) any later version.

##

##  This program is distributed in the hope that it will be useful,

##  but WITHOUT ANY WARRANTY; without even the implied warranty of

##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

##  GNU General Public License for more details.

##

##  You should have received a copy of the GNU General Public License

##  along with this program. If not, see http://www.gnu.org/licenses/

##

##  Yes, I know, it sucks, it's suppose to suck tough

##  That's just an example from hs years, c'mon! 

##

########################################################################

 

import sys

from PyQt4 import QtGui

from PyQt4 import QtCore

 

try:

    from PyQt4.phonon import Phonon

except ImportError:

    app = QtGui.QApplication(sys.argv)

    QtGui.QMessageBox.critical(None, "Import error!",

            "Try downlaod the newest Qt4-Phonon packages from http:/www.qtsoftware.com/",

            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,

            QtGui.QMessageBox.NoButton | QtGui.QMessageBox.Escape)

    sys.exit(1)

 

# ======================================================================

# **********************************************************************

 

 

def setStyleHelper(widget, style):

        widget.setStyle(style)

        widget.setPalette(style.standardPalette())

        for child in widget.children():

            if isinstance(child, QtGui.QWidget):

                setStyleHelper(child, style)

    

def change_style(widget, style):

    style=QtGui.QStyleFactory.create(style)

    if style: setStyleHelper(widget, style)

 

# ======================================================================

# **********************************************************************

 

 

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent = None):

        QtGui.QMainWindow.__init__(self, parent)

 

            ##  next 5 lines below are just a copy of this c++ code:

            ##     Phonon.MediaObject *mediaObject = new Phonon.MediaObject(this);

            ##     Phonon.VideoWidget *videoWidget = new Phonon.VideoWidget(this);

            ##     Phonon.createPath(mediaObject, videoWidget);

            ##     Phonon.AudioOutput *audioOutput = new Phonon.AudioOutput(Phonon.VideoCategory, this);

            ##     Phonon.createPath(mediaObject, audioOutput);

 

        self.mediaObject = Phonon.MediaObject(self)

        self.videoWidget = Phonon.VideoWidget(self)

        Phonon.createPath(self.mediaObject, self.videoWidget) 

        self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory, self)

        Phonon.createPath(self.mediaObject, self.audioOutput)  

 

        self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(1000)

        self.videoWidget.setScaleMode(0)

 

        self.connect(self.mediaObject, QtCore.SIGNAL('tick(qint64)'),self.tick)

        self.connect(self.mediaObject,QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'),self.stateChanged)

        self.connect(self.metaInformationResolver,QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'),self.metaStateChanged)

        self.connect(self.mediaObject,QtCore.SIGNAL('currentSourceChanged(Phonon::MediaSource)'),self.sourceChanged)

 

        self.setupActions()

        self.setupMenus()

        self.setupUi()

        self.timeLcd.display("00:00")

 

        self.video_id = self.videoWidget.winId()

        self.source = ''

 

    def caps(self):

        self.caps = Caps()

        self.caps.show()

 

    def screenshot(self):

        self.screenshot = Screenshot(self.video_id)

        self.screenshot.show()

 

    def muting(self):

        if self.audioOutput.isMuted():

            self.audioOutput.setMuted(0)

            self.muteAction.setIcon(QtGui.QIcon("mute_off.png"))

        else:

            self.audioOutput.setMuted(1)

            self.muteAction.setIcon(QtGui.QIcon("mute_on.png"))

                

    def sizeHint(self):

        return QtCore.QSize(600, 450)

 

    def addFiles(self):

        files = QtGui.QFileDialog.getOpenFileNames(self,

                self.tr("Select video files"),

                QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

 

        if files.isEmpty(): return

        for string in files: self.source = Phonon.MediaSource(string)

        if self.source: self.metaInformationResolver.setCurrentSource(self.source)

 

    def about(self):

        QtGui.QMessageBox.information(self, self.tr("About me"),

                self.tr("This simple video player example shows how to use Phonon - "

                        "the newest multimedia framework that comes with Qt4 - to "

                        "create a simple movies player in one file using Python."))

 

    def stateChanged(self, newState, oldState):

        if newState == Phonon.ErrorState:

            if self.mediaObject.errorType() == Phonon.FatalError:

                QtGui.QMessageBox.warning(self, self.tr("Fatal Error"),self.mediaObject.errorString())

            else:

                QtGui.QMessageBox.warning(self, self.tr("Error"),self.mediaObject.errorString())

 

        elif newState == Phonon.PlayingState:

            self.playAction.setEnabled(False)

            self.pauseAction.setEnabled(True)

            self.stopAction.setEnabled(True)

 

        elif newState == Phonon.StoppedState:

            self.stopAction.setEnabled(False)

            self.playAction.setEnabled(True)

            self.pauseAction.setEnabled(False)

            self.timeLcd.display("00:00")

 

        elif newState == Phonon.PausedState:

            self.pauseAction.setEnabled(False)

            self.stopAction.setEnabled(True)

            self.playAction.setEnabled(True)

 

    def tick(self, time):

        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)

        self.timeLcd.display(displayTime.toString('mm:ss'))

 

    def sourceChanged(self, source):

        self.timeLcd.display("00:00")

 

    def metaStateChanged(self, newState, oldState):

        if newState == Phonon.ErrorState:

            QtGui.QMessageBox.warning(self, self.tr("Error opening files"),

                    self.metaInformationResolver.errorString())

 

        self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

 

        source = self.metaInformationResolver.currentSource()

 

    def full(self):

        if not self.videoWidget.isFullScreen():

            self.videoWidget.enterFullScreen()

        else: 

            self.videoWidget.exitFullScreen()

 

 

    # I know, it might be one func but... err, that was faster to ctrl+c/v

    def aspect_auto(self): self.videoWidget.setAspectRatio(0)

    def aspect_user(self): self.videoWidget.setAspectRatio(1)

    def aspect_43(self): self.videoWidget.setAspectRatio(2)

    def aspect_169(self): self.videoWidget.setAspectRatio(3)

 

    def scale_fit(self): self.videoWidget.setScaleMode(0)

    def scale_scale(self): self.videoWidget.setScaleMode(1)

 

    def change_stylecleanlooks(self): change_style(app,'cleanlooks')

    def change_styleplastique(self): change_style(app,'plastique')

 

    def setupActions(self):

 

        self.playAction = QtGui.QAction(QtGui.QIcon("play.png"), self.tr("Play"), self)

        self.playAction.setShortcut(self.tr("Crl+P"))

        self.playAction.setDisabled(0)

 

        self.pauseAction = QtGui.QAction(QtGui.QIcon("pause.png"), self.tr("Pause"), self)

        self.pauseAction.setShortcut(self.tr("Ctrl+A"))

        self.pauseAction.setDisabled(True)

 

        self.stopAction = QtGui.QAction(QtGui.QIcon("stop.png"), self.tr("Stop"), self)

        self.stopAction.setShortcut(self.tr("Ctrl+S"))

        self.stopAction.setDisabled(True)

 

        self.muteAction = QtGui.QAction(QtGui.QIcon("mute_off.png"), self.tr("Mute"), self)

        self.muteAction.setShortcut(self.tr("Ctrl+M"))

 

        self.addFilesAction = QtGui.QAction(self.tr("Open..."), self)

        self.addFilesAction.setShortcut(self.tr("Ctrl+F"))

 

        self.exitAction = QtGui.QAction(self.tr("E&xit"), self)

        self.exitAction.setShortcut(self.tr("Ctrl+X"))

 

        self.aboutAction = QtGui.QAction(self.tr("About"), self)

        self.aboutAction.setShortcut(self.tr("Ctrl+B"))

 

        self.fullAction = QtGui.QAction(self.tr("Full screen"), self)

        self.fullAction.setShortcut(self.tr("F11"))

 

        self.aboutQtAction = QtGui.QAction(self.tr("About Qt"), self)

        self.aboutQtAction.setShortcut(self.tr("Ctrl+Q"))

 

        self.screenAction = QtGui.QAction(self.tr("Screenshot"), self)

        self.screenAction.setShortcut(self.tr("F5"))

 

        self.capsAction = QtGui.QAction(self.tr("Capabilities"), self)

        self.capsAction.setShortcut(self.tr("F12"))

 

        # aspect ratio

        self.aspect_autoAction = QtGui.QAction(self.tr("Auto"), self)

        self.aspect_userAction = QtGui.QAction(self.tr("Manual"), self)

        self.aspect_43Action = QtGui.QAction(self.tr("4:3"), self)

        self.aspect_169Action = QtGui.QAction(self.tr("16:9"), self)

 

        self.aspect_autoAction.setCheckable(True)

        self.aspect_userAction.setCheckable(True)

        self.aspect_43Action.setCheckable(True)

        self.aspect_169Action.setCheckable(True)

 

        self.aspectGroup = QtGui.QActionGroup(self)

        self.aspectGroup.addAction(self.aspect_autoAction)

        self.aspectGroup.addAction(self.aspect_userAction)

        self.aspectGroup.addAction(self.aspect_43Action)

        self.aspectGroup.addAction(self.aspect_169Action)

        self.aspect_autoAction.setChecked(True)

 

        # scale mode

        self.scale_fitAction = QtGui.QAction(self.tr("Fit in view"), self)

        self.scale_scaleAction = QtGui.QAction(self.tr("Scale and crop"), self)

        self.scale_fitAction.setCheckable(True)

        self.scale_scaleAction.setCheckable(True)

 

        self.scaleGroup = QtGui.QActionGroup(self)

        self.scaleGroup.addAction(self.scale_fitAction)

        self.scaleGroup.addAction(self.scale_scaleAction)

        self.scale_fitAction.setChecked(True)

 

        # qt-styles

        self.style_plastiqueAction = QtGui.QAction(self.tr("Plastuique"), self)

        self.style_cleanlooksAction = QtGui.QAction(self.tr("Cleanlooks"), self)

 

        self.style_plastiqueAction.setCheckable(True)

        self.style_cleanlooksAction.setCheckable(True)

 

        self.styleGroup = QtGui.QActionGroup(self)

        self.styleGroup.addAction(self.style_plastiqueAction)

        self.styleGroup.addAction(self.style_cleanlooksAction)

        self.style_cleanlooksAction.setChecked(True)

 

        # connections

        self.connect(self.playAction, QtCore.SIGNAL('triggered()'),self.mediaObject, QtCore.SLOT('play()'))

        self.connect(self.pauseAction, QtCore.SIGNAL('triggered()'),self.mediaObject, QtCore.SLOT('pause()'))

        self.connect(self.stopAction, QtCore.SIGNAL('triggered()'),self.mediaObject, QtCore.SLOT('stop()'))

        self.connect(self.muteAction, QtCore.SIGNAL('triggered()'),self.muting)

        self.connect(self.addFilesAction, QtCore.SIGNAL('triggered()'),self.addFiles)

        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'),self, QtCore.SLOT('close()'))

        self.connect(self.fullAction, QtCore.SIGNAL('triggered()'),self.full)

        self.connect(self.aboutAction, QtCore.SIGNAL('triggered()'),self.about)

        self.connect(self.screenAction, QtCore.SIGNAL('triggered()'),self.screenshot)

        self.connect(self.capsAction, QtCore.SIGNAL('triggered()'),self.caps)

        self.connect(self.aboutQtAction, QtCore.SIGNAL('triggered()'),QtGui.qApp, QtCore.SLOT('aboutQt()'))

        # aspect ratio

        self.connect(self.aspect_autoAction, QtCore.SIGNAL('triggered()'),self.aspect_auto)

        self.connect(self.aspect_userAction, QtCore.SIGNAL('triggered()'),self.aspect_user)

        self.connect(self.aspect_43Action, QtCore.SIGNAL('triggered()'),self.aspect_43)

        self.connect(self.aspect_169Action, QtCore.SIGNAL('triggered()'),self.aspect_169)

        # scale mode

        self.connect(self.scale_fitAction, QtCore.SIGNAL('triggered()'),self.scale_fit)

        self.connect(self.scale_scaleAction, QtCore.SIGNAL('triggered()'),self.scale_scale)

        # style conns

        self.connect(self.style_plastiqueAction, QtCore.SIGNAL('triggered()'),self.change_styleplastique)

        self.connect(self.style_cleanlooksAction, QtCore.SIGNAL('triggered()'),self.change_stylecleanlooks)

 

    def setupMenus(self):

        fileMenu = self.menuBar().addMenu(self.tr("File"))

        fileMenu.addAction(self.addFilesAction)

        fileMenu.addSeparator()

        fileMenu.addAction(self.exitAction)

 

        editMenu = self.menuBar().addMenu(self.tr("Edit"))

        editMenu.addAction(self.fullAction)

        editMenu.addAction(self.screenAction)

        editMenu.addSeparator()

        editMenu.addAction(self.capsAction)

        

        videoMenu = self.menuBar().addMenu(self.tr("Video"))

        aspectMenu = videoMenu.addMenu(self.tr("Aspect ratio"))

        aspectMenu.addAction(self.aspect_autoAction)

        aspectMenu.addAction(self.aspect_userAction)

        aspectMenu.addAction(self.aspect_43Action)

        aspectMenu.addAction(self.aspect_169Action)

        scaleMenu = videoMenu.addMenu(self.tr("Scale mode"))

        scaleMenu.addAction(self.scale_fitAction)

        scaleMenu.addAction(self.scale_scaleAction)

 

        styleMenu = self.menuBar().addMenu(self.tr("Style"))

        styleMenu.addAction(self.style_cleanlooksAction)

        styleMenu.addAction(self.style_plastiqueAction)

        

        aboutMenu = self.menuBar().addMenu(self.tr("Help"))

        aboutMenu.addAction(self.aboutAction)

        aboutMenu.addAction(self.aboutQtAction)

 

    def setupUi(self):

        bar = QtGui.QToolBar()

        bar.addAction(self.playAction)

        bar.addAction(self.pauseAction)

        bar.addAction(self.stopAction)

        bar.addAction(self.muteAction)

 

        self.seekSlider = Phonon.SeekSlider(self)

        self.seekSlider.setMediaObject(self.mediaObject)

 

        self.volumeSlider = Phonon.VolumeSlider(self)

        self.volumeSlider.setAudioOutput(self.audioOutput)

        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)

 

        volumeLabel = QtGui.QLabel()

        volumeLabel.setPixmap(QtGui.QPixmap('images/volume.png'))

 

        palette = QtGui.QPalette()

        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

 

        self.timeLcd = QtGui.QLCDNumber()

        self.timeLcd.setPalette(palette)

 

        seekerLayout = QtGui.QHBoxLayout()

        seekerLayout.addWidget(self.seekSlider)

        seekerLayout.addWidget(self.timeLcd)

 

        playbackLayout = QtGui.QHBoxLayout()

        playbackLayout.addWidget(bar)

        playbackLayout.addStretch()

        playbackLayout.addWidget(volumeLabel)

        playbackLayout.addWidget(self.volumeSlider)

 

        mainLayout = QtGui.QVBoxLayout()

        mainLayout.addWidget(self.videoWidget)

        

        mainLayout.addLayout(seekerLayout)

        mainLayout.addLayout(playbackLayout)

 

        widget = QtGui.QWidget()

        widget.setLayout(mainLayout)

 

        self.setCentralWidget(widget)

        self.setWindowTitle("Phonvideo")

 

# ======================================================================

# **********************************************************************

 

class Screenshot(QtGui.QWidget):

    def __init__(self, video_id, parent = None):

        QtGui.QWidget.__init__(self, parent)

 

        self.screenshotLabel = QtGui.QLabel()

        self.screenshotLabel.setSizePolicy(QtGui.QSizePolicy.Expanding,

                                           QtGui.QSizePolicy.Expanding)

        self.screenshotLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.screenshotLabel.setMinimumSize(240, 160)

 

        self.createOptionsGroupBox()

        self.createButtonsLayout()

        self.video_id = video_id # in your face stupid class!

 

        self.mainLayout = QtGui.QVBoxLayout()

        self.mainLayout.addWidget(self.screenshotLabel)

        self.mainLayout.addWidget(self.optionsGroupBox)

        self.mainLayout.addLayout(self.buttonsLayout)

        self.setLayout(self.mainLayout)

 

        self.shootScreen()

        self.delaySpinBox.setValue(5)

 

        self.setWindowTitle(self.tr("Screenshot"))

        self.resize(300, 200)

 

    def resizeEvent(self, event):

        scaledSize = self.originalPixmap.size()

        scaledSize.scale(self.screenshotLabel.size(), QtCore.Qt.KeepAspectRatio)

        if not self.screenshotLabel.pixmap() or scaledSize != self.screenshotLabel.pixmap().size():

            self.updateScreenshotLabel()

 

    def newScreenshot(self):

        if self.hideThisWindowCheckBox.isChecked():

            self.hide()

        self.newScreenshotButton.setDisabled(True)

 

        QtCore.QTimer.singleShot(self.delaySpinBox.value() * 1000, self.shootScreen)

 

    def saveScreenshot(self):

        format = QtCore.QString("png")

        initialPath = QtCore.QDir.currentPath() + self.tr("/untitled.") + format

 

        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"),

                               initialPath,

                               self.tr("%1 Files (*.%2);;All Files (*)")

                                   .arg(format.toUpper())

                                   .arg(format))

        if not fileName.isEmpty():

            self.originalPixmap.save(fileName, str(format))

 

    def shootScreen(self):

        if self.delaySpinBox.value() != 0:

            QtGui.qApp.beep()

 

        self.originalPixmap = QtGui.QPixmap.grabWindow(self.video_id)

        self.updateScreenshotLabel()

 

        self.newScreenshotButton.setDisabled(False)

        if self.hideThisWindowCheckBox.isChecked():

            self.show()

 

    def updateCheckBox(self):

        if self.delaySpinBox.value() == 0:

            self.hideThisWindowCheckBox.setDisabled(True)

        else:

            self.hideThisWindowCheckBox.setDisabled(False)

 

    def createOptionsGroupBox(self):

        self.optionsGroupBox = QtGui.QGroupBox(self.tr("Options"))

 

        self.delaySpinBox = QtGui.QSpinBox()

        self.delaySpinBox.setSuffix(self.tr(" s"))

        self.delaySpinBox.setMaximum(60)

        self.connect(self.delaySpinBox, QtCore.SIGNAL("valueChanged(int)"),

                     self.updateCheckBox)

 

        self.delaySpinBoxLabel = QtGui.QLabel(self.tr("Screenshot Delay:"))

 

        self.hideThisWindowCheckBox = QtGui.QCheckBox(self.tr("Hide This Window"))

 

        self.optionsGroupBoxLayout = QtGui.QGridLayout()

        self.optionsGroupBoxLayout.addWidget(self.delaySpinBoxLabel, 0, 0)

        self.optionsGroupBoxLayout.addWidget(self.delaySpinBox, 0, 1)

        self.optionsGroupBoxLayout.addWidget(self.hideThisWindowCheckBox, 1, 0, 1, 2)

        self.optionsGroupBox.setLayout(self.optionsGroupBoxLayout)

 

    def createButtonsLayout(self):

        self.newScreenshotButton = self.createButton(self.tr("New"),

                                                     self.newScreenshot)

 

        self.saveScreenshotButton = self.createButton(self.tr("Save"),

                                                      self.saveScreenshot)

 

        self.quitScreenshotButton = self.createButton(self.tr("Quit"),

                                                      self.close)

 

        self.buttonsLayout = QtGui.QHBoxLayout()

        self.buttonsLayout.addStretch()

        self.buttonsLayout.addWidget(self.newScreenshotButton)

        self.buttonsLayout.addWidget(self.saveScreenshotButton)

        self.buttonsLayout.addWidget(self.quitScreenshotButton)

 

    def createButton(self, text, member):

        button = QtGui.QPushButton(text)

        button.connect(button, QtCore.SIGNAL("clicked()"), member)

        return button

 

    def updateScreenshotLabel(self):

        self.screenshotLabel.setPixmap(self.originalPixmap.scaled(

            self.screenshotLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

 

# ======================================================================

# **********************************************************************

# Here's eaxmple that there's no problem to include code from other Qt4

# scripts into this one. It's from official examples btw.

 

 

class Caps(QtGui.QWidget):

    def __init__(self):

        QtGui.QWidget.__init__(self)

 

        self.setupUi()

        self.updateWidgets()

 

        self.connect(Phonon.BackendCapabilities.notifier(),

                QtCore.SIGNAL('capabilitiesChanged()'), self.updateWidgets)

        self.connect(Phonon.BackendCapabilities.notifier(),

                QtCore.SIGNAL('availableAudioOutputDevicesChanged()'),

                self.updateWidgets)

 

    def updateWidgets(self):

        # Output devices.

        devices = Phonon.BackendCapabilities.availableAudioOutputDevices()

        model = Phonon.AudioOutputDeviceModel(devices, self)

        self.devicesListView.setModel(model)

 

        # MIME types.

        self.mimeListWidget.clear()

 

        for mimeType in Phonon.BackendCapabilities.availableMimeTypes():

            item = QtGui.QListWidgetItem(self.mimeListWidget)

            item.setText(mimeType)

 

        # Effects.

        self.effectsTreeWidget.clear()

 

        for effect in Phonon.BackendCapabilities.availableAudioEffects():

            item = QtGui.QTreeWidgetItem(self.effectsTreeWidget)

            item.setText(0, self.tr("Effect"))

            item.setText(1, effect.name())

            item.setText(2, effect.description())

 

            # Effects parameters.

            for parameter in Phonon.Effect(effect, self).parameters():

                defaultValue = parameter.defaultValue()

                minimumValue = parameter.minimumValue()

                maximumValue = parameter.maximumValue()

 

                valueString = QtCore.QString("%1 / %2 / %3").arg(defaultValue.toString()).arg(minimumValue.toString()).arg(maximumValue.toString())

 

                parameterItem = QtGui.QTreeWidgetItem(item)

                parameterItem.setText(0, self.tr("Parameter"))

                parameterItem.setText(1, parameter.name())

                parameterItem.setText(2, parameter.description())

                parameterItem.setText(3, QtCore.QVariant.typeToName(parameter.type()))

                parameterItem.setText(4, valueString)

 

        for i in range(self.effectsTreeWidget.columnCount()):

            if i == 0:

                self.effectsTreeWidget.setColumnWidth(0, 150)

            elif i == 2:

                self.effectsTreeWidget.setColumnWidth(2, 350)

            else:

                self.effectsTreeWidget.resizeColumnToContents(i)

 

    def setupUi(self):

        self.setupBackendBox()

 

        layout = QtGui.QVBoxLayout()

        layout.addWidget(self.backendBox)

 

        self.setLayout(layout)

        self.setWindowTitle(self.tr("Capabilities Example"))

 

    def setupBackendBox(self):

        self.devicesLabel = QtGui.QLabel(self.tr("Available Audio Devices:"))

        self.devicesListView = QtGui.QListView()

 

        self.mimeTypesLabel = QtGui.QLabel(self.tr("Supported MIME Types:"))

        self.mimeListWidget = QtGui.QListWidget()

 

        self.effectsLabel = QtGui.QLabel(self.tr("Available Audio Effects:"))

 

        headerLabels = [self.tr("Type"), self.tr("Name"),

                self.tr("Description"), self.tr("Value Type"),

                self.tr("Default/Min/Max Values")]

 

        self.effectsTreeWidget = QtGui.QTreeWidget()

        self.effectsTreeWidget.setHeaderLabels(headerLabels)

        self.effectsTreeWidget.setColumnCount(5)

 

        layout = QtGui.QGridLayout()

        layout.addWidget(self.devicesLabel, 0, 0)

        layout.addWidget(self.devicesListView, 1, 0)

        layout.addWidget(self.mimeTypesLabel, 0, 1)

        layout.addWidget(self.mimeListWidget, 1, 1)

        layout.addWidget(self.effectsLabel, 2, 0)

        layout.addWidget(self.effectsTreeWidget, 3, 0, 2, 2)

        layout.setRowStretch(3, 100)

 

        self.backendBox = QtGui.QGroupBox(self.tr("Backend Capabilities"))

        self.backendBox.setLayout(layout)

 

# ======================================================================

# **********************************************************************

 

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    app.setApplicationName("Phonvideo")

    app.setQuitOnLastWindowClosed(True)

    change_style(app,"cleanlooks")  # default style, 'cos it's damn cute

 

    window = MainWindow()

    window.show()

 

    sys.exit(app.exec_())
