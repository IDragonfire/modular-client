from PyQt4 import QtCore, QtGui

import util, time
from fa import maps
from games.gameitem import GameItemDelegate
from multiprocessing import Lock
from notificatation_system.ns_dialog import NotficationDialog
from notificatation_system.ns_settings import NsSettingsDialog


class NotificationSystem():
    USER_ONLINE = 'user_online'
    NEW_GAME = 'new_game'

    def __init__(self, client):
        self.client = client

        self.dialog = NotficationDialog(self.client)
        self.events = []
        self.disabledStartup = True
        self.lock = Lock()

        self.settings = NsSettingsDialog(self.client)

        self.user = util.icon("client/user.png", pix=True)

    def isDisabled(self):
        return self.disabledStartup or not self.settings.enabled

    def setNotificationEnabled(self, enabled):
        self.settings.enabled = enabled
        self.settings.saveSettings()

    @QtCore.pyqtSlot()
    def on_event(self, eventType, data):
        if self.isDisabled() or not self.settings.popupEnabled(eventType):
            return
        self.events.append((eventType, data))
        if self.dialog.isHidden():
            self.showEvent()

    @QtCore.pyqtSlot()
    def on_showSettings(self):
        self.settings.show()

    def showEvent(self):
        self.lock.acquire()
        event = self.events[0]
        del self.events[0]
        self.lock.release()

        eventType = event[0]
        data = event[1]
        pixmap = None
        text = str(data)
        if eventType == self.USER_ONLINE:
            username = data['user']
            if self.settings.getCustomSetting(eventType, 'mode') == 'friends' and not self.client.isFriend(username):
                self.dialogClosed()
                return
            pixmap = self.user
            text = '<html>%s<br><font color="silver" size="-2">joined</font> %s</html>' % (username, data['channel'])
        elif eventType == self.NEW_GAME:
            if self.settings.getCustomSetting(eventType, 'mode') == 'friends' and ('host' not in data or not self.client.isFriend(data['host'])):
                self.dialogClosed()
                return

            pixmap = maps.preview(data['mapname'], pixmap=True).scaled(50, 50)

            #TODO: outsource as function?
            mod = None if 'featured_mod' not in data else data['featured_mod']
            mods = None if 'sim_mods' not in data else data['sim_mods']

            modstr = ''
            if (mod != 'faf' or mods):
                modstr = mod
                if mods:
                    if mod == 'faf':modstr = ", ".join(mods.values())
                    else: modstr = mod + " & " + ", ".join(mods.values())
                    if len(modstr) > 20: modstr = modstr[:15] + "..."

            modhtml = '' if (modstr == '') else '<br><font size="-4"><font color="red">mods</font> %s</font>' % modstr
            text = '<html>%s<br><font color="silver" size="-2">on</font> %s%s</html>' % (data['title'], maps.getDisplayName(data['mapname']), modhtml)

        self.dialog.newEvent(pixmap, text, self.settings.popup_lifetime, self.settings.soundEnabled(eventType))

    def dialogClosed(self):
        if self.events:
            self.showEvent()
