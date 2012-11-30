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
import util
import string

FormClass, BaseClass = util.loadUiType("clips/clips.ui")

from clips.clip import Clip, ClipItemDelegate

class ClipsWidget(FormClass, BaseClass):
    clipUpdated     = QtCore.pyqtSignal(Clip)
    clipClicked     = QtCore.pyqtSignal(Clip)
    
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.clipDockWidget.layout().addWidget(self)
        
        self.clips = {}
        self.clipList.setItemDelegate(ClipItemDelegate(self))
        self.client.clipUpdated.connect(self.processClipInfo)
        self.clipList.itemClicked.connect(self.clipClick)
        self.clipList.itemPressed.connect(self.clipPressed)
        
        self.filterScene.textChanged.connect(self.eventFilterChanged)
        
    def processClipInfo(self, message):
        uid = message["uid"]

        if uid in self.clips: 
            self.clips[uid].update(message, self.client) 
        else :
            self.clips[uid] = Clip(uid)

            self.clipList.addItem(self.clips[uid])
            #self.timelineList.addItem(self.clips[uid].timelineItem)

            #self.shotTree.addTopLevelItem(self.clips[uid].treeItem)
           
            #self.clips[uid].treeItem.setExpanded(1)            
            self.clips[uid].update(message, self.client)
            
            self.clipUpdated.emit(self.clips[uid])
    
    def clipPressed(self, item):
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton :  
            item.clicked()
                        
    def clipClick(self, item):
        ''' we have selected a clip
        We re-emit a signal for all modules interested in that. '''

        self.clipClicked.emit(item)
        

    def eventFilterChanged(self):
        if self.filterScene.text() == "" :
            for uid in self.clips :
                self.clips[uid].setHidden(0)      
        else :        
            filterText = filter(lambda x: x.isdigit(), self.filterScene.text())
            
            if filterText == "" :
                return
            

            for uid in self.clips :
                
                if self.clips[uid].scene == int(filterText) :
                    self.clips[uid].setHidden(0)
                else :
                    self.clips[uid].setHidden(1)

          
