from PyQt4 import QtCore, QtGui


import util, re


FormClass, BaseClass = util.loadUiType("validations/retake.ui")


class RetakeWidget(FormClass, BaseClass):
    def __init__(self, parent, tasks, reason, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent

        self.taskListWidget.addItems(tasks)
        self.taskListWidget.setCurrentItem(self.taskListWidget.item(0))
        
        self.reasonTextEdit.setText(reason)
        self.reasonTextEdit.selectAll()
        self.reasonTextEdit.setFocus(QtCore.Qt.OtherFocusReason)
        

        self.setWindowTitle("Retake a clip")
        
        self.setStyleSheet(self.parent.client.styleSheet())


#
#        self.confirmButton.pressed.connect(self.retake)
#        self.cancelButton.pressed.connect(self.close)
#
#
#    def retake(self):
#        self.parent.projectName = self.projectName.text()
#        self.parent.project3d = self.project3dBox.currentText()
#        self.parent.compositingProject = self.projectCompBox.currentText()
#        self.done(1)

