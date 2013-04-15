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

FormClass, BaseClass = util.loadUiType("games/ladder2v2.ui")


class TeamLadderWidget(FormClass, BaseClass):
    '''
    This is the widget that appears if you click the 2v2-ladder button.
    It sends commands to the database of type 2v2ladder.
    These commands specify a 'type' parameter. This can be
    start: the widget has been opened, the database may send teammates_info messages
    stop: the widget has been closed, the database should stop sending teammates_info messages.
            The database should also send teammates_info messages with a 'remove' key to every player it concerns.
    update: The player has clicked or doubleclicked a certain player and this needs to be send to that
            respective player. Gives a uid and state argument as well.
    '''
    def __init__(self, parent, item, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        self.client = self.parent.client
        self.setStyleSheet(self.parent.client.styleSheet())
        
        self.setWindowTitle ("Finding 2v2 ladder partner")

        self.client.send(dict(command="2v2ladder",type="start")) # this command also sends client.login, so the server
                                                         # can know to which teams the player belongs.
        self.client.TeammatesInfo.connect(self.processTeammatesInfo)
        self.aboutToQuit.connect(self.quiting)
        self.PlayerList.setItemDelegate(PlayerItemDelegate(self))
        self.PlayerList.itemClicked.connect(self.playerclicked)
        self.PlayerList.itemDoubleClicked.connect(self.playerdoubleclicked)

        self.player = self.client.players[self.client.login]
        self.players = {}
        self.selected = [] #list of uid's of selected players
        self.doubleselected = None # the uid of the person that was double clicked

    @QtCore.pyqtSlot(dict)
    def processTeammatesInfo(self, message):
        '''
        Slot that stores the teammates_info information
        This is a dictionary that should be of this format
        message = {
        uid
        name = str(player name)
        rating_mean = int
        rating_deviation = int
        team = str(teamname)
        state = int     state = 0: nothing special, state = 1: player has selected you,
                        state = 2: player has doubleclicked you
        }
        Even though a player can belong to multiple team, it should give a message
        here for every team this player shares with the logged in player
        This means that the uid should be different every time.
        If the dictionary contains a key named 'remove' that player will be removed from the listing.
        '''
        uid = message["uid"]
        
        if uid not in self.players:
            if not message.has_key("remove"):
                self.players[uid] = PlayerItem(uid)
                self.PlayerList.addItem(self.games[uid])
                self.games[uid].update(message, self.client)
        else:
            if message.has_key("remove"): # a player has stopped searching
                self.PlayerList.removeItemWidget(self.players[uid])
                del self.players[uid]
            else:
                self.games[uid].update(message, self.client)
    
    @QtCore.pyqtSlot()
    def quiting(self):
        self.client.send(dict(command="2v2ladder",type="stop"))
        self.client.TeammatesInfo.disconnect(self.processTeammatesInfo)


    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def playerclicked(self, player):
        '''
        Makes the background colors of the player reflect that they have been clicked and send
        the commands to the database to inform the player on the other side that they have been (de)selected.
        i.e. They will recieve a teammates_info message that reflects the correct status.
        '''
        uid = player.uid
        if uid in self.selected:
            self.selected.remove(uid)
            if self.doubleselected == uid:
                self.doubleselected = None
            player.deselected()
            self.client.send(dict(command="2v2ladder",type="update",uid=uid,state=0))
        else:
            self.selected.append(uid)
            player.selected()
            self.client.send(dict(command="2v2ladder",type="update",uid=uid,state=1))
        

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def playerdoubleclicked(self, player):
        uid = player.uid
        if uid not in self.selected:
            self.selected.append(uid)
        if self.doubleselected != uid: # a new person was doubleclicked
            #de-doubleclick the old one
            self.client.send(dict(command="2v2ladder",type="update",uid=self.players[self.doubleselected],state=1))
            self.players[self.doubleselected].selected()
            #doubleclick the new one
            self.doubleselected = uid
            self.client.send(dict(command="2v2ladder",type="update",uid=uid,state=2))
            player.doubleselected()
        
# This whole thing is adapted from games.gameitem.GameItemDelegate, I don't really know what is going on here...
class PlayerItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        QtGui.QStyledItemDelegate.__init__(self, *args, **kwargs)

    def paint(self, painter, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
                
        painter.save()
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        
        icon = QtGui.QIcon(option.icon)
        iconsize = icon.actualSize(option.rect.size())

        icon.paint(painter, option.rect.adjusted(5-2, -2, 0, 0), QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        painter.translate(option.rect.left() + iconsize.width() + 10, option.rect.top()+10)
        clip = QtCore.QRectF(0, 0, option.rect.width()-iconsize.width() - 10 - 5, option.rect.height())
        html.drawContents(painter, clip)

        painter.restore()
        
    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(PlayerItem.TEXTWIDTH)
        return QtCore.QSize(PlayerItem.ICONSIZE + PlayerItem.TEXTWIDTH + PlayerItem.PADDING, PlayerItem.ICONSIZE)



class PlayerItem(QtGui.QListWidgetItem):
    TEXTWIDTH = 230
    ICONSIZE = 110
    PADDING = 10
    WIDTH = ICONSIZE + TEXTWIDTH

    FORMATTER_TEXT = unicode(util.readfile("games/formatters/player.qthtml"))

    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)
        self.uid = uid
        self.name = None
        self.client = None
        self.mean = None
        self.deviation = None
        self.rating = None
        self.team = None
        self.ready = False

    def update(self, message, client):
        foo = message
        message = copy.deepcopy(foo)

        self.client = client
        
        self.name       = message['name']
        self.mean       = message['rating_mean']
        self.deviation  = message['rating_deviation']
        self.team       = message['team']
        self.state      = message['ready'] # should be an int

        self.rating = self.mean - 3*self.deviation
        if self.ready == True: 
            readystr = "Ready"
        else:
            readystr = "Searching"

        self.setText(self.FORMATTER_TEXT.format(name = self.name, rating = self.rating, team = self.team, ready=readystr))

        #the next bit is taken from chat.chatter.Chatter.update. This should be probably be put in a helper function
        league = self.client.getUserLeague(self.name)
        if self.rating == 0:
            self.setIcon(util.icon("chat/rank/newplayer.png"))
        if league != None:
            elif league["league"] == 1:
                self.setIcon(util.icon("chat/rank/Aeon_Scout.png"))
            elif league["league"] == 2:
                self.setIcon(util.icon("chat/rank/Aeon_T1.png"))
            elif league["league"] == 3:
                self.setIcon(util.icon("chat/rank/Aeon_T2.png"))
            elif league["league"] == 4:
                self.setIcon(util.icon("chat/rank/Aeon_T3.png"))
            elif league["league"] == 5:
                self.setIcon(util.icon("chat/rank/Aeon_XP.png"))
        else:
            self.setIcon(util.icon("chat/rank/civilian.png"))






