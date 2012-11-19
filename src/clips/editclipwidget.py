from PyQt4 import QtCore, QtGui


import util, re


FormClass, BaseClass = util.loadUiType("clips/editClip.ui")


class EditClipWidget(FormClass, BaseClass):
    def __init__(self, parent, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent

        self.setWindowTitle(("Edit clip : Scene %i Shot %i" % (self.parent.scene, self.parent.shot) ))
        
        self.start.setValue(self.parent.inClip)
        self.end.setValue(self.parent.outClip)
        self.handleIn.setValue(self.parent.handleIn)
        self.handleOut.setValue(self.parent.handleOut)
        
        self.setStyleSheet(self.parent.client.styleSheet())

