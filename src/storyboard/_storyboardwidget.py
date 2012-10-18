from PyQt4 import QtCore, QtGui

from storyboard.clip import Clip, ClipItemDelegate 
from storyboard.story import StoryItemDelegate
import util, os, string

import base64, zlib

FormClass, BaseClass = util.loadUiType("storyboard/storyboard.ui")


class StoryboardWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.storyboardTab.layout().addWidget(self)

        self.clips = {}

        self.storyboardList.setItemDelegate(StoryItemDelegate(self))
        self.clipList.setItemDelegate(ClipItemDelegate(self))
        self.clipList.itemClicked.connect(self.clipClicked)


        self.storyboardList.itemDoubleClicked.connect(self.storyDoubleClicked)
        self.storyboardList.itemPressed.connect(self.storyPressed)
        
        self.filterScene.textChanged.connect(self.eventFilterChanged)      
        self.client.clipUpdated.connect(self.processClipInfo)
        
    def processClipInfo(self, message):
        uid = message["uid"]

        if uid in self.clips: 
            self.clips[uid].update(message, self.client) 
        else :
            self.clips[uid] = Clip(uid)
            self.clipList.addItem(self.clips[uid])
            self.storyboardList.addItem(self.clips[uid].storyItem)           
            self.clips[uid].update(message, self.client)            
              
  

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def storyPressed(self, item):
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton:            
            #Look up the associated tourney object        
            item.pressed(item)

    def storyDoubleClicked(self, item):
        pass


    def clipClicked(self, item):
        ''' we have selected a clip'''
        self.storyboardList.setCurrentItem(item.storyItem)

    def clipDoubleClicked(self, item):
        ''' we have double clicked a clip'''
        treeItem = item.treeItem
        self.shotTree.setCurrentItem(treeItem)
        
        item.animTreeItem.setExpanded(1)
        for uid in item.animScene :
            item.animScene[uid].setExpanded(1)
        

    def eventFilterChanged(self):
        filterText = self.filterScene.text().strip(string.ascii_letters)
        if filterText != "" :
            for uid in self.clips :
                
                if self.clips[uid].scene == int(filterText) :
                    self.clips[uid].setHidden(0)
                else :
                    self.clips[uid].setHidden(1)
        else :
            for uid in self.clips :
                self.clips[uid].setHidden(0)
