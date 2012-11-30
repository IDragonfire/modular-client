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

from edits.editclip import EditClip, EditClipItemDelegate 
from edits.clip import Clip, ClipItemDelegate, TimelineItemDelegate

import util, os, string

import base64, zlib

FormClass, BaseClass = util.loadUiType("edits/edits.ui")


class EditsWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.editsTab.layout().addWidget(self)

        self.clips = {}
        self.zoom = 1
#
        self.shotList.setItemDelegate(EditClipItemDelegate(self))
#        self.clipList.setItemDelegate(ClipItemDelegate(self))
        self.timelineList.setItemDelegate(TimelineItemDelegate(self))
#
#        self.clipList.itemClicked.connect(self.clipClicked)
#        self.clipList.itemDoubleClicked.connect(self.clipDoubleClicked)
#        
        self.zoomSlider.sliderMoved.connect(self.zoomChanged)
#        
        self.validateEditButton.setVisible(0)
        self.shotList.setVisible(0)
#        
#        self.filterScene.textChanged.connect(self.eventFilterChanged)      
#        
        self.client.editsUpdated.connect(self.processEditsInfo)       
        self.client.powerUpdated.connect(self.powerUpdate)
        
        self.client.clips.clipUpdated.connect(self.processClipInfo)
        self.client.comments.commentInfoUpdated.connect(self.processCommentInfo)
        self.client.validatorObjUpdated.connect(self.processValidatorInfo)
   
    def zoomChanged(self, value):
        self.zoom = value
        self.timelineList.viewport().update()     
        self.timelineList.setIconSize(QtCore.QSize(value,0))
     
    def powerUpdate(self):
        if self.client.power >= 16 :
            self.parseXmlButton.pressed.connect(self.submitXml)
            self.validateEditButton.pressed.connect(self.validateEdit)
        else :
            self.parseXmlButton.setVisible(0)    
  
    
    def processClipInfo(self, clip):
        uid = clip.uid

        if uid in self.clips: 
            self.clips[uid].update() 
        else :
            self.clips[uid] = Clip(clip)

            
            self.timelineList.addItem(self.clips[uid].timelineItem)

            self.shotTree.addTopLevelItem(self.clips[uid].treeItem)
           
            #self.clips[uid].treeItem.setExpanded(1)            
            self.clips[uid].update()

    def processCommentInfo(self, comment):
        if comment.typeuid == 0 :
            uid = comment.clipuid
            if uid in self.clips:
                self.clips[uid].updateComment(comment)
    
    def processValidatorInfo(self, validator):
        uid = validator.clipUid
        if uid in self.clips:
            self.clips[uid].updateScene3d(validator)   
    
    def processEditsInfo(self, message):
        self.topTabs.setVisible(0)
        self.shotList.setVisible(1)
        self.shotList.clear()
        self.clips = {}
        
        clips = message.get('clips', [])
        
        for clip in clips :
            uid = clip["uid"]
        
            if uid in self.clips: 
                self.clips[uid].update(clip, self.client) 
            else :
                self.clips[uid] = EditClip(uid)
                self.shotList.addItem(self.clips[uid])
                self.clips[uid].update(clip, self.client)
        self.validateEditButton.setVisible(1)
    
    def validateEdit(self):
        clips = []
        for clip in self.clips :
           
            clips.append(dict(scene = self.clips[clip].scene, shot = self.clips[clip].shot, inClip = self.clips[clip].inClip, outClip = self.clips[clip].outClip, start = self.clips[clip].start, end = self.clips[clip].end, duration = self.clips[clip].duration))
        
        self.client.send(dict(command="edits", action="validate", clips=clips))
        
        self.validateEditButton.setVisible(0)
        self.shotList.clear()
        self.clips = {}
        self.topTabs.setVisible(1)
        self.shotList.setVisible(0)
        
    def submitXml(self):
        
        if self.client.currentProject != None :
            compProject = os.path.join("//sledge/vol1/projects", self.client.currentProject.projectComp, "Compositing/EDL") 
        
            options = QtGui.QFileDialog.Options()
            
            options |= QtGui.QFileDialog.DontUseNativeDialog
            
            fileName = QtGui.QFileDialog.getOpenFileName(self.client,
                    "Select the XML file",
                    compProject,
                    "All Files (*);;Text Files (*.xml)", options)
            if fileName:
                file = QtCore.QFile(fileName)
                file.open(QtCore.QIODevice.ReadOnly)
                fileDatas = base64.b64encode(zlib.compress(file.readAll()))
                file.close()      
 
                self.client.send(dict(command="edits", action="submit", file = fileDatas))
