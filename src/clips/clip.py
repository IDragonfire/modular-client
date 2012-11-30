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





from PyQt4 import QtGui, QtCore
import util

from editclipwidget import EditClipWidget

class ClipItemDelegate(QtGui.QStyledItemDelegate):
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
        painter.translate(option.rect.left(), option.rect.top())
        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
        html.drawContents(painter, clip)
        painter.restore()
        
    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(Clip.TEXTWIDTH)
        return QtCore.QSize(Clip.TEXTWIDTH + Clip.PADDING, Clip.CLIPSIZE)  


class Clip(QtGui.QListWidgetItem):

    '''
    A clip is the representation of a scene and a shot.
    '''

    TEXTWIDTH = 150
    CLIPSIZE = 25
    PADDING = 5
    WIDTH = TEXTWIDTH
    
    FORMATTER_CLIP = unicode(util.readfile("edits/formatters/clip.qthtml"))
    
    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        
        self.client  = None
        
        self.uid = uid
        
        self.scene = None
        self.shot = None

        self.inClip     = 0
        self.outClip    = 0
        self.start      = 0
        self.end        = 0
        self.duration   = 0
        self.handleIn   = 0
        self.handleOut  = 0
        self.comments   = None

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.scene      = message['scene']
        self.shot       = message['shot']
        self.inClip     = message['inClip']
        self.outClip    = message['outClip']
        self.handleIn   = message['handleIn']
        self.handleOut  = message['handleOut']
        self.start      = message['start']
        self.end        = message['end']
        self.duration   = message['duration']
        
        self.setText(self.FORMATTER_CLIP.format(scene = str(self.scene).zfill(3), shot = str(self.shot).zfill(3), inClip = str(self.inClip).zfill(2), outClip = str(self.outClip).zfill(2), handleIn = str(self.handleIn).zfill(2), handleOut = str(self.handleOut).zfill(2)))

    def editClip(self):
        editclip = EditClipWidget(self)
        if editclip.exec_() == 1 :
            self.client.send(dict(command='edits', action = 'edit', uid=self.uid, inClip = editclip.start.value(), outClip = editclip.end.value(), handleIn = editclip.handleIn.value(), handleOut = editclip.handleOut.value() ))
            
   
    def clicked(self):
        '''
        A clip was clicked
        '''
        menu = QtGui.QMenu(self.client)
        actionEdit = QtGui.QAction("Edit clip", menu)
    
        if self.client.power <= 16 :
            actionEdit.setDisabled(True)
        
        # Triggers
        actionEdit.triggered.connect(self.editClip)
    
        menu.addAction(actionEdit)
        menu.popup(QtGui.QCursor.pos())        
   
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;

        # Default: Alphabetical

        return self.start < other.start
    
