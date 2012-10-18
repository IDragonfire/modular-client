from PyQt4 import QtGui, QtCore
from storyboard.story import Story

import util

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

    TEXTWIDTH = 50
    CLIPSIZE = 25
    PADDING = 5
    
    WIDTH = TEXTWIDTH
    
    FORMATTER_CLIP = unicode(util.readfile("storyboard/formatters/clip.qthtml"))
    
    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        
        self.client  = None
        
        self.uid = uid
        
        self.scene = None
        self.shot = None

        self.storyItem = Story(self)

        self.inClip = 0
        self.outClip = 0
        self.start = 0
        self.end = 0
        self.duration = 0
        self.handleIn = 0
        self.handleOut = 0
        self.comments = []

        
    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client  = client

        self.scene      = message['scene']
        self.shot       = message['shot']
        self.inClip     = message['inClip']
        self.outClip    = message['outClip']
        self.handleIn   = message['handleIn']
        self.handleOut  = message['handleOut']
        self.start      = message['start']
        self.end        = message['end']
        self.duration   = message['duration']

        self.storyItem.update()
       
        self.setText(self.FORMATTER_CLIP.format(scene = str(self.scene).zfill(3), shot = str(self.shot).zfill(3)))
    
    def getComments(self):
        self.comments = self.client.comments.getComments(self.uid, 0)          
        
        
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;

        
        # Default: Alphabetical
        return self.start < other.start