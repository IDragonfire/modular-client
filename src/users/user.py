from PyQt4 import QtGui, QtCore
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


class User(QtGui.QListWidgetItem):

    '''
    A clip is the representation of a scene and a shot.
    '''

    TEXTWIDTH = 50
    CLIPSIZE = 25
    PADDING = 5
    
    WIDTH = TEXTWIDTH
    
    #FORMATTER_CLIP = unicode(util.readfile("storyboard/formatters/clip.qthtml"))
    
    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        
        self.client  = None
        
        self.uid        = uid
        self.login      = None
        self.ip         = None
        self.localip    = None
        self.project    = None
        self.power      = None
        self.online     = False
        
    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client  = client

        self.login      = message['login']
        self.ip         = message['ip']
        self.localip    = message['localip']                 
        self.project    = message['project']
        self.power      = message['power']
        self.online     = message['online']

        
        
        self.setText(self.login)
        
        if self.online :
            brush = QtGui.QBrush(QtGui.QColor("green"))
        else : 
            brush = QtGui.QBrush(QtGui.QColor("red"))
        
        self.setForeground(brush)
        
        
        
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;

        
        # Default: Alphabetical

        return self.login < other.login
        