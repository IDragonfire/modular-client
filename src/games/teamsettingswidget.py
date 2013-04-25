#-------------------------------------------------------------------------------
# Copyright (c) 2012 Gael Honorez.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#-------------------------------------------------------------------------------





from PyQt4 import QtCore, QtGui

import util

import copy

FormClass, BaseClass = util.loadUiType("games/ladder2v2team.ui")


class TeamSettingsWidget(FormClass, BaseClass):
    '''
    
    '''
    FORMATTER_INFO = unicode(util.readfile("games/formatters/teaminfo.qthtml"))
    def __init__(self, parent, teammate, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        self.teammate = teammate
        self.client = self.parent.client
        self.setStyleSheet(self.parent.parent.client.styleSheet())
        
        self.setWindowTitle ("Prepare your ACU'S")

        self.client.send(dict(command="2v2ladder",type="team")) # this command also sends client.login, so the server
                                                         # can know to which teams the player belongs.
        #self.client.TeammatesInfo.connect(self.processTeammatesInfo)
        self.FactionSelect.currentIndexChanged.connect(self.factionchanged)
        self.CheckReady.toggled.connect(self.statechanged)
        self.ready = False
        self.friendready = False
        self.foundOtherTeam = False

        self.factions = {0: "Random",1: "UEF",2: "Cybran",3: "Aeon",4: "Seraphim"}
        self.graphics = {0: util.icon("games/automatch/random.png",pix=True),
                         1: util.icon("games/automatch/uef.png",pix=True),
                         2: util.icon("games/automatch/cybran.png",pix=True),
                         3: util.icon("games/automatch/aeon.png",pix=True),
                         4: util.icon("games/automatch/seraphim.png",pix=True)}
        self.FactionGraphic1.setPixmap(self.graphics[0])
        self.FactionGraphic2.setPixmap(self.graphics[0])
        player = self.client.login
        self.TeamInfo.setText(self.FORMATTER_INFO.format(player1=player["name"],
                player2=self.teammate.name,
                ratingglobal1=player["rating_mean"] - 3*player["rating_deviation"],
                ratingglobal2=self.teammate.rating - 3* self.teammate.deviation,
                rating2v21=0, rating2v22=0,
                team=self.teammate.teamname))

        self.TextLine.returnPressed.connect(self.addLine)

        
    @QtCore.pyqtSlot(dict)
    def processTeammatesInfo(self, message):
        '''
        Slot that stores the teammates_info information
        This function only parses messages that have a 'team' key.
        If it doesn't have this key then this message is meant for
        the first dialog.
        '''
        uid = message["uid"]
        
        if not message.has_key("team"):
            return
        t = message["type"]
        if t == "text":
            self.addLine(message["text"],True)
        elif t == "faction":
            self.FactionFriend.setText(self.factions[message["faction"]])
            self.FactionGraphic1.setPixmap(self.graphics[index])
        elif t == "state":
            self.friendready = message["state"]
            self.FriendReady.setChecked(bool(message["state"]))
            if self.friendready and self.ready and self.foundOtherTeam:
                self.client.send(dict(command="2v2ladder",team="",type="label",label=2))
        elif t == "label":
            l = message["label"]
            if l == 0:
                self.foundOtherTeam = False
                m = "Finding opponent team..."
            elif l == 1:
                self.foundOtherTeam = True
                m = "Found opponent team. Waiting for them to ready."
                if self.friendready and self.ready: #this command means that the opponent team will recieve 2 messages that the other team is ready. This shouldn't be a problem.
                    self.client.send(dict(command="2v2ladder",team="",type="label",label=2))
            elif l == 2:
                self.foundOtherTeam = True
                m = "Other team is waiting for you..."
                if self.ready and self.friendready:
                    self.client.send(dict(command="2v2ladder",team="",type="label",label=2))
                    self.client.send(dict(command="2v2ladder", team="", type="start"))
            self.StatusLabel.setText(m)
        elif t == "quit": #other player has left this dialog
            QtGui.QMessageBox.warning(None, "Other player has left lobby")
            self.done(0)
        elif t == "text":
            self.TextBox.append(message["text"])
        else:
            raise AssertionError, "Que? No comprendo di messago."

    
    def closeEvent(self, event):
        self.client.send(dict(command="2v2ladder",team="",type="quit"))
        #self.client.TeammatesInfo.disconnect(self.processTeammatesInfo)
        self.parent.dialog = None
        self.parent.client.send(dict(command="2v2ladder",type="busy",busy=False))
        event.accept()

    @QtCore.pyqtSlot(int)
    def factionchanged(self, index):
        self.FactionGraphic1.setPixmap(self.graphics[index])
        self.client.send(dict(command="2v2ladder", team="", type="faction", faction=index))

    @QtCore.pyqtSlot(bool)
    def statechanged(self, state):
        self.ready = state
        self.client.send(dict(command="2v2ladder",team="",type="state",state=state))

    @QtCore.pyqtSlot()
    def addLine(self):
        text = "%s: %s" % (self.client.login["name"],self.TextLine.text())
        self.TextBox.append(text)
        self.client.send(dict(command="2v2ladder",team="",type="text",text=text))
        self.TextLine.setText("")
