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
        self.client.scenes3d.scene3dInfoUpdated.connect(self.processScene3dInfo)
   
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
#
#    def clipClicked(self, item):
#        ''' we have selected a clip'''
#        self.shotTree.setCurrentItem(item.treeItem)
#
#    def clipDoubleClicked(self, item):
#        ''' we have double clicked a clip'''
#        treeItem = item.treeItem
#        self.shotTree.setCurrentItem(treeItem)
#        
#        item.animTreeItem.setExpanded(1)
#        for uid in item.animScene :
#            item.animScene[uid].setExpanded(1)
#        
#
  
    
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
    
    def processScene3dInfo(self, scene3d):
        uid = scene3d.clipUid
        if uid in self.clips:
            self.clips[uid].updateScene3d(scene3d)   
    
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