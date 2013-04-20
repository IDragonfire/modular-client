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


class TeamLadderWidget(FormClass, BaseClass):
    '''
    
    '''
    def __init__(self, parent, teammate, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        self.teammate = teammate
        self.client = self.parent.client
        self.setStyleSheet(self.parent.client.styleSheet())
        
        self.setWindowTitle ("Prepare your ACU'S")

        self.client.send(dict(command="2v2ladder",type="team")) # this command also sends client.login, so the server
                                                         # can know to which teams the player belongs.
        self.client.TeammatesInfo.connect(self.processTeammatesInfo)
        self.aboutToQuit.connect(self.quiting)
        self.FactionSelect.currentIndexChanged.connect(self.factionchanged)
        self.CheckReady.toggled.connect(self.statechanged)
        self.ready = False
        self.friendready = False

        self.factions = {0: "Random",1: "UEF",2: "Cybran",3: "Aeon",4: "Seraphim"}
        self.graphics = {0: util.icon("games/automatch/random.png",pix=True),
                         1: util.icon("games/automatch/uef.png",pix=True),
                         2: util.icon("games/automatch/cybran.png",pix=True),
                         3: util.icon("games/automatch/aeon.png",pix=True),
                         4: util.icon("games/automatch/seraphim.png",pix=True)}
        self.FactionGraphic1.setPixmap(self.graphics[0])
        self.FactionGraphic2.setPixmap(self.graphics[0])

        
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
            self.setTeamIcon(message["faction"], True)
        elif t == "state":
            self.friendready = message["state"]
            self.FriendReady.setChecked(bool(message["state"]))
        elif t == "label":
            l = message["label"]
            if l == 0:
                m = "Finding opponent team..."
            if l == 1:
                m = "Found opponent team. Waiting for them to ready."
            if l == 2:
                m = "Other team is waiting for you..."
                if self.ready and self.friendready:
                    pass #start the actual game
            self.StatusLabel.setText(message["label"])
        elif t == "quit": #other player has left this dialog
            QtGui.QMessageBox.warning(None, "Other player has left lobby")
            self.done(0)
        else:
            raise AssertionError, "Que? No comprendo di messago."

    
    @QtCore.pyqtSlot()
    def quiting(self):
        self.client.send(dict(command="2v2ladder",team="",type="quit"))
        self.client.TeammatesInfo.disconnect(self.processTeammatesInfo)

    @QtCore.pyqtSlot(int)
    def factionchanged(self, index):
        self.setTeamIcon(index, False)
        self.client.send(dict(command="2v2ladder", team="", type="faction", faction=index))

    @QtCore.pyqtSlot(bool)
    def statechanged(self, state):
        self.ready = state
        self.client.send(dict(command="2v2ladder",team="",type="state",state=state))
        
