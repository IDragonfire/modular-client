#-------------------------------------------------------------------------------
# Copyright (c) 2012 Gael Honorez.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#-------------------------------------------------------------------------------



import urllib2

from PyQt4 import QtCore, QtGui

import modvault
import util

FormClass, BaseClass = util.loadUiType("modvault/uimod.ui")


class UIModWidget(FormClass, BaseClass):
    FORMATTER_UIMOD = unicode(util.readfile("modvault/uimod.qthtml"))
    def __init__(self, parent, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        
        self.setStyleSheet(self.parent.client.styleSheet())
        
        self.setWindowTitle("Ui Mod Manager")

        self.doneButton.clicked.connect(self.doneClicked)
        self.modList.itemEntered.connect(self.hoverOver)
        allmods = modvault.getInstalledMods()
        self.uimods = {}
        for modname in allmods:
            mod = modvault.getModfromName(modname)
            if mod!=None and mod["ui_only"]:
                self.uimods[mod["name"]] = mod
                self.modList.addItem(mod["name"])

        names = [mod['name'] for mod in modvault.getActiveMods(uimods=True)]
        for name in names:
            l = self.modList.findItems(name, QtCore.Qt.MatchExactly)
            if l: l[0].setSelected(True)

        if len(self.uimods) != 0:
            self.hoverOver(self.modList.itemFromIndex(0))

    @QtCore.pyqtSlot()
    def doneClicked(self):
        selected_mods = [self.uimods[str(mod.text())] for mod in self.modList.selectedItems()]
        modvault.setActiveMods(selected_mods, False)
        QtGui.QMessageBox.information(None, "Error", "Could not set the active UI mods. Maybe something is wrong with your game.prefs file. Please send your log.")
        self.done(1)

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def hoverOver(self, item):
        mod = self.uimods[str(item.text())]
        self.modInfo.setText(FORMATTER_UIMOD.format(name=mod["name"], description=mod["description"]))
        
    
