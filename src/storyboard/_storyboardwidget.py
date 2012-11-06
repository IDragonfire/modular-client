from PyQt4 import QtCore, QtGui

from storyboard.story import Story, StoryItemDelegate
import util, os, string

import base64, zlib

FormClass, BaseClass = util.loadUiType("storyboard/storyboard.ui")


class StoryboardWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.storyboardTab.layout().addWidget(self)

        self.story = {}

        self.storyboardList.setItemDelegate(StoryItemDelegate(self))
        #self.clipList.setItemDelegate(ClipItemDelegate(self))
        


        self.storyboardList.itemDoubleClicked.connect(self.storyDoubleClicked)
        self.storyboardList.itemPressed.connect(self.storyPressed)
        
        
        self.client.clips.clipUpdated.connect(self.processClipInfo)
        self.client.clips.clipClicked.connect(self.clipSelection)
         
        self.client.comments.commentInfoUpdated.connect(self.processCommentInfo)
        #self.client.clipUpdated.connect(self.processClipInfo)
        
        
    def processCommentInfo(self, comment):
        if comment.typeuid == 0 :
            uid = comment.clipuid
            if uid in self.story:
                self.story[uid].updateComment(comment)
           
    def processClipInfo(self, clip):
        uid = clip.uid
        if uid in self.story:
            self.story[uid].update()
        else :
            self.story[uid] = Story(clip)
            self.storyboardList.addItem(self.story[uid])                      
            self.story[uid].update()            
              
    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def storyPressed(self, item):
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton:            
            #Look up the associated tourney object        
            item.pressed(item)

    def storyDoubleClicked(self, item):
        pass


    def clipSelection(self, item):
        ''' we have selected a clip'''
        if item.uid in self.story :
            self.storyboardList.setCurrentItem(self.story[item.uid])
#
#    def clipDoubleClicked(self, item):
#        ''' we have double clicked a clip'''
#        treeItem = item.treeItem
#        self.shotTree.setCurrentItem(treeItem)
#        
#        item.animTreeItem.setExpanded(1)
#        for uid in item.animScene :
#            item.animScene[uid].setExpanded(1)
        

#    def eventFilterChanged(self):
#        filterText = self.filterScene.text().strip(string.ascii_letters)
#        if filterText != "" :
#            for uid in self.clips :
#                
#                if self.clips[uid].scene == int(filterText) :
#                    self.clips[uid].setHidden(0)
#                else :
#                    self.clips[uid].setHidden(1)
#        else :
#            for uid in self.clips :
#                self.clips[uid].setHidden(0)
