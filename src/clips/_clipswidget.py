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
            
    def clipClick(self, item):
        ''' we have selected a clip
        We re-emit a signal for all modules interested in that. '''
        self.clipClicked.emit(item)

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