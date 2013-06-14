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
from util import strtodate, datetostr, now
import util

FormClass, BaseClass = util.loadUiType("modvault/mod.ui")


class ModWidget(FormClass, BaseClass):
    def __init__(self, parent, mod, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        
        self.setStyleSheet(self.parent.client.styleSheet())
        
        self.setWindowTitle(mod.name)
        self.Title.setText(mod.name)
        self.Description.setText(mod.description)
        modtext = ""
        if mod.isuimod: modtext = "UI mod\n"
        elif mod.isbigmod: modtext = "Big mod\n"
        elif mod.issmallmod: modtext = "Small mod\n"
        self.Info.setText(modtext + "By %s\nUploaded %s" % (mod.author,
                                    str(mod.date)))
        if mod.thumbnail == None:
            self.Picture.setPixmap(util.pixmap("games/unknown_map.png"))
        else:
            self.Picture.setPixmap(mod.thumbnail)

        self.Comments.setItemDelegate(CommentItemDelegate(self))
        self.BugReports.setItemDelegate(CommentItemDelegate(self))
        
        self.DownloadButton.clicked.connect(self.download)
        self.LineComment.returnPressed.connect(self.addComment)
        self.LineBugReport.returnPressed.connect(self.addBugReport)

        for item in mod.comments:
            comment = CommentItem(self,item["uid"])
            comment.update(item)
            self.Comments.addItem(comment)
        for item in mod.bugreports:
            comment = CommentItem(self,item["uid"])
            comment.update(item)
            self.BugReports.addItem(comment)

        self.mod = mod
        
    @QtCore.pyqtSlot()
    def download(self):
        if not self.mod.name in self.parent.installedMods:
            self.parent.downloadMod(self.mod)
        else:
            show = QtGui.QMessageBox.question(self.client, "Already got the Mod", "Seems like you already have that mod!<br/><b>Would you like to see it?</b>", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if show == QtGui.QMessageBox.Yes:
                util.showInExplorer(modvault.modToFilename(mod))

    @QtCore.pyqtSlot()
    def addComment(self):
        if self.LineComment.text() == "": return
        comment = {"author":self.parent.client.login, "text":self.LineComment.text(),
                   "date":datetostr(now()), "uid":"%s-%s" % (self.mod.uid, str(len(self.mod.bugreports)+len(self.mod.comments)).zfill(3))}
        
        self.parent.client.send(dict(command="modvault",type="addcomment",moduid=self.mod.uid,comment=comment))
        c = CommentItem(self, comment["uid"])
        c.update(comment)
        self.Comments.addItem(c)
        self.mod.comments.append(comment)
        self.LineComment.setText("")

    @QtCore.pyqtSlot()
    def addBugReport(self):
        if self.LineBugReport.text() == "": return
        bugreport = {"author":self.parent.client.login, "text":self.LineBugReport.text(),
                   "date":datetostr(now()), "uid":"%s-%s" % (self.mod.uid, str(len(self.mod.bugreports) + +len(self.mod.comments)).zfill(3))}
        
        self.parent.client.send(dict(command="modvault",type="addbugreport",moduid=self.mod.uid,bugreport=bugreport))
        c = CommentItem(self, bugreport["uid"])
        c.update(bugreport)
        self.BugReports.addItem(c)
        self.mod.bugreports.append(bugreport)
        self.LineBugReport.setText("")

class CommentItemDelegate(QtGui.QStyledItemDelegate):
    TEXTWIDTH = 350
    TEXTHEIGHT = 60
    def __init__(self, *args, **kwargs):
        QtGui.QStyledItemDelegate.__init__(self, *args, **kwargs)
        
    def paint(self, painter, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
                
        painter.save()
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
                
        option.text = ""  
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)
        

        #Description
        painter.translate(option.rect.left() + 10, option.rect.top()+10)
        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
        html.drawContents(painter, clip)
  
        painter.restore()
        

    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(self.TEXTWIDTH)
        return QtCore.QSize(self.TEXTWIDTH, self.TEXTHEIGHT)

class CommentItem(QtGui.QListWidgetItem):
    FORMATTER_COMMENT = unicode(util.readfile("modvault/comment.qthtml"))
    def __init__(self, parent, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)

        self.parent = parent
        self.uid = uid
        self.text = ""
        self.author = ""
        self.date = None

    def update(self, dic):
        self.text = dic["text"]
        self.author = dic["author"]
        self.date = strtodate(dic["date"])
        self.setText(self.FORMATTER_COMMENT.format(text=self.text,author=self.author,date=str(self.date)))

    def __ge__(self, other):
        return self.date > other.date

    def __lt__(self, other):
        return self.date <= other.date