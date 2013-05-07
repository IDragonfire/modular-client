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

from games import logger
from games.teamsettingswidget import TeamSettingsWidget
import util

import copy

FormClass, BaseClass = util.loadUiType("games/ladder2v2.ui")

#some dummy stuff to test it out.
class DummyClient(object):
    def send(self,dic):
        logger.info("Widget sent fake message: %s" % str(dic))

    login = {"name": "Johnie102", "rating_mean": 1300, "rating_deviation": 80}

tminfo1 = {"uid": 10, "name": "player1","rating_mean": 1000, "rating_deviation":500, "state":0, "teamname":"TAG"}
tminfo2 = {"uid": 15, "name": "paulo","rating_mean": 800, "rating_deviation":200, "state":0, "teamname":"Glorious"}
tminfo3 = {"uid": 20, "name": "clarice","rating_mean": 1500, "rating_deviation":100, "state":1, "teamname":"DIK"}
tminfo4 = {"uid": 22, "name": "devilpoopook9","rating_mean": 1328, "rating_deviation":28, "state":2, "teamname":"ErrO"}


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
    def __init__(self, parent, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        #self.client = self.parent.client
        self.client = DummyClient()
        self.setStyleSheet(self.parent.client.styleSheet())
        
        self.setWindowTitle ("Finding 2v2 ladder partner")

        self.client.send(dict(command="2v2ladder",type="start")) # this command also sends client.login, so the server
                                                         # can know to which teams the player belongs.
        #self..client.TeammatesInfo.connect(self.processTeammatesInfo)
        #self.aboutToQuit.connect(self.quiting)
        self.PlayerList.setItemDelegate(PlayerItemDelegate(self))
        self.PlayerList.itemClicked.connect(self.playerclicked)
        self.PlayerList.itemDoubleClicked.connect(self.playerdoubleclicked)

        self.player = self.parent.client.players[parent.client.login]
        print self.player
        self.players = {}
        self.selected = [] #list of uid's of selected players
        self.doubleselected = None # the uid of the person that was double clicked
        self.dialog = None
        
        logger.info("Done with the teamladder dialog stuff")
        #test stuff
        self.processTeammatesInfo(tminfo1)
        self.processTeammatesInfo(tminfo2)
        self.processTeammatesInfo(tminfo3)
        self.processTeammatesInfo(tminfo4)

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
        teamname = str(teamname)
        state = int     state = 0: nothing special, state = 1: player has selected you,
                        state = 2: player has doubleclicked you
        }
        Even though a player can belong to multiple team, it should give a message
        here for every team this player shares with the logged in player
        This means that the uid should be different every time.
        If the dictionary contains a key named 'remove' that player will be removed from the listing.
        '''
        uid = message["uid"]
        if message.has_key("teammessage"):
            return #Ignore this message, it is meant for the second dialog.
        if uid not in self.players:
            if not message.has_key("remove"):
                self.players[uid] = self.createPlayerItem(message)
        else:
            if message.has_key("remove"): # a player has stopped searching
                self.PlayerList.removeItemWidget(self.players[uid])
                del self.players[uid]
                if uid in self.selected:
                    self.selected.remove(uid)
                if self.doubleselected == uid:
                    self.doubleselected = None
            else:
                self.PlayerList.removeItemWidget(self.players[uid])
                self.players[uid] = self.createPlayerItem(message)
                if uid in self.selected:
                    self.players[uid].setSelected(True)
                if self.doubleselected == uid and self.players[uid].state == 2:
                    self.openTeamDialog(self.players[uid])

    def createPlayerItem(self, message):
        state = message["state"]
        uid = message["uid"]
        if state == 0: item = PlayerItemSearching(uid)
        if state == 1: item = PlayerItemInterested(uid)
        if state == 2: item = PlayerItemReady(uid)
        self.PlayerList.addItem(item)
        item.update(message, self.client)
        return item
        
                    
    
    def closeEvent(self,event):
        self.client.send(dict(command="2v2ladder",type="stop"))
        #self.client.TeammatesInfo.disconnect(self.processTeammatesInfo)
        logger.info("Closed search dialog")
        if self.dialog != None:
            self.dialog.done(0)
        self.parent.teamladderwidget = None
        self.parent.rankedtype = 1
        self.parent.Button2v2.setChecked(False)
        self.parent.Button1v1.setChecked(True)
        event.accept()


    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def playerclicked(self, player):
        '''
        Makes the background colors of the player reflect that they have been clicked and send
        the commands to the database to inform the player on the other side that they have been (de)selected.
        i.e. They will recieve a teammates_info message that reflects the correct status.
        '''
        uid = player.uid
        if uid in self.selected and uid!=self.doubleselected:
            self.selected.remove(uid)
            player.setSelected(False)
            self.client.send(dict(command="2v2ladder",type="update",uid=uid,state=0))
        elif uid!=self.doubleselected:
            self.selected.append(uid)
            player.setSelected(True)
            self.client.send(dict(command="2v2ladder",type="update",uid=uid,state=1))
        

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def playerdoubleclicked(self, player):
        uid = player.uid
        if uid not in self.selected:
            self.selected.append(uid)
        if self.doubleselected != uid and self.doubleselected != None: # a new person was doubleclicked
            #de-doubleclick the old one
            self.players[self.doubleselected].special = False
            self.players[self.doubleselected].setSelected(True)
            self.client.send(dict(command="2v2ladder",type="update",uid=self.doubleselected,state=1))

        self.doubleselected = uid
        player.special = True
        player.setSelected(True)
        self.client.send(dict(command="2v2ladder",type="update",uid=uid,state=2))
        if player.state == 2: # Ready to play a game
            self.openTeamDialog(player)
            

    def openTeamDialog(self, teammate):
        if self.dialog != None:
            return
        self.dialog = TeamSettingsWidget(self, teammate)
        self.dialog.setModal(0)
        self.dialog.show()
        self.client.send(dict(command="2v2ladder",type="busy",busy=True))
        
        
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

        option.icon = QtGui.QIcon()     
        option.text = ""
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)
        
        icon.paint(painter, option.rect.adjusted(0, 0, 0, 0), QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        painter.translate(option.rect.left() + iconsize.width() + 8, option.rect.top()+0)
        clip = QtCore.QRectF(0, 0, option.rect.width()-iconsize.width() - 10 - 5, option.rect.height())
        html.drawContents(painter, clip)

        painter.restore()
        
    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(PlayerItem.TEXTWIDTH)
        return QtCore.QSize(PlayerItem.ICONSIZE + PlayerItem.TEXTWIDTH + PlayerItem.PADDING, PlayerItem.ICONSIZE)


# This class is subclassed, so different background can be defined in the CSS stylesheet.
# There probably is a more elegant way to do this.
class PlayerItem(QtGui.QListWidgetItem):
    TEXTWIDTH = 200
    ICONSIZE = 25
    PADDING = 5
    WIDTH = ICONSIZE + TEXTWIDTH
    #COLOR_DEFAULT = QtGui.QColor(238,106,167) #hotpink2
    #COLOR_SELECTED = QtGui.QColor(134,42,81) #plum pudding
    #COLOR_SPECIAL = QtGui.QColor(255,0,102) #Broadwaypink

    FORMATTER_TEXT = unicode(util.readfile("games/formatters/player.qthtml"))
    FORMATTER_TEXT_SELECTED = unicode(util.readfile("games/formatters/playerselected.qthtml"))
    FORMATTER_DOUBLESELECTED = unicode(util.readfile("games/formatters/playerdoubleselected.qthtml"))
    TEXT_COLOR = "silver"

    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)
        self.uid = uid
        self.name = None
        self.client = None
        self.mean = None
        self.deviation = None
        self.rating = None
        self.teamname = None
        self.state = False
        self.special = False
        self.formatter = self.FORMATTER_TEXT

    def update(self, message, client):
        foo = message
        message = copy.deepcopy(foo)

        self.client = client
        
        self.name       = message['name']
        self.mean       = message['rating_mean']
        self.deviation  = message['rating_deviation']
        self.teamname       = message['teamname']
        self.state      = message['state'] # should be an int

        self.rating = self.mean - 3*self.deviation

        self.updatetext()

        
        '''
        #the next bit is taken from chat.chatter.Chatter.update. This should be probably be put in a helper function
        league = self.client.getUserLeague(self.name)
        if self.rating == 0:
            self.setIcon(util.icon("chat/rank/newplayer.png"))
        if league != None:
            if league["league"] == 1:
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
            self.setIcon(util.icon("chat/rank/newplayer.png"))
        '''
        self.setIcon(util.icon("chat/rank/civilian.png"))

    def setSelected(self, state):
        QtGui.QListWidgetItem.setSelected(self, state)
        if state: self.formatter = self.FORMATTER_TEXT_SELECTED
        else: self.formatter = self.FORMATTER_TEXT
        if self.special: self.formatter = self.FORMATTER_DOUBLESELECTED
        self.updatetext()

    def updatetext(self):
        if self.state == 0: 
            readystr = "Searching"
        elif self.state == 1:
            readystr = "Interested"
        elif self.state == 2:
            readystr = "Ready"
        self.setText(self.formatter.format(color=self.TEXT_COLOR, name = self.name, rating = self.rating, team = self.teamname, ready=readystr))

    def __ge__(self, other):
        return not self.__lt__(self, other)

    def __lt__(self, other):
        if not self.name: return True
        if not other.name: return False
        return self.name.lower() < other.name.lower()

class PlayerItemSearching(PlayerItem):
    pass
class PlayerItemInterested(PlayerItem):
    TEXT_COLOR = "white"
class PlayerItemReady(PlayerItem):
    TEXT_COLOR = "yellow"


