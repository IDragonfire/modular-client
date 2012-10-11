from PyQt4 import QtCore, QtGui

from edits.editclip import EditClip, EditClipItemDelegate
from edits.clip import Clip, ClipItemDelegate 

import util, os

import base64, zlib

FormClass, BaseClass = util.loadUiType("edits/edits.ui")


class EditsWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.editsTab.layout().addWidget(self)

        self.clips = {}

        self.shotList.setItemDelegate(EditClipItemDelegate(self))
        self.projectList.setItemDelegate(ClipItemDelegate(self))
        
        self.parseXmlButton.pressed.connect(self.submitXml)
        self.validateEditButton.pressed.connect(self.validateEdit)
        
        self.validateEditButton.setVisible(0)
        self.shotList.setVisible(0)
        
        
        
        self.client.editsUpdated.connect(self.processEditsInfo)       
        self.client.clipUpdated.connect(self.processClipInfo)
        
        
    def processClipInfo(self, message):
        
        
        uid = message["uid"]
        
        if uid in self.clips: 
            self.clips[uid].update(message, self.client) 
        else :
            self.clips[uid] = Clip(uid)
            self.projectList.addItem(self.clips[uid])
            self.clips[uid].update(message, self.client)
        
        
        
        
    def processEditsInfo(self, message):
        self.shotTree.setVisible(0)
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
        self.shotTree.setVisible(1)
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