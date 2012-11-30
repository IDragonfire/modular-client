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

