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

