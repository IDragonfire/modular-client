#-------------------------------------------------------------------------------
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------





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

        self.storyboardList.itemDoubleClicked.connect(self.storyDoubleClicked)
        self.storyboardList.itemPressed.connect(self.storyPressed)
        
        self.client.clips.clipUpdated.connect(self.processClipInfo)
        self.client.clips.clipClicked.connect(self.clipSelection)
        self.client.clips.filterScene.textChanged.connect(self.eventFilterChanged)
         
        self.client.comments.commentInfoUpdated.connect(self.processCommentInfo)
        
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

    def eventFilterChanged(self):
        if self.client.clips.filterScene.text() == "" :
            for uid in self.story :
                self.story[uid].setHidden(0)    
        else :        
            filterText = filter(lambda x: x.isdigit(), self.client.clips.filterScene.text())
            
            if filterText == "" :
                return
            
            for uid in self.story :                
                if self.story[uid].clip.scene == int(filterText) :
                    self.story[uid].setHidden(0)
                else :
                    self.story[uid].setHidden(1)

    def clipSelection(self, item):
        ''' we have selected a clip'''
        if item.uid in self.story :
            self.storyboardList.setCurrentItem(self.story[item.uid])
