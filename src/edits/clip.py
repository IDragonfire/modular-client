from PyQt4 import QtGui, QtCore
import util
import math

class TimelineItemDelegate(QtGui.QStyledItemDelegate):
    FORMATTER_TIMELINERANGE = unicode(util.readfile("edits/formatters/timelinerange.qthtml"))
    def __init__(self, *args, **kwargs):
        QtGui.QStyledItemDelegate.__init__(self, *args, **kwargs)
    

    def paint(self, painter, option, index, *args, **kwargs):
        self.initStyleOption(option, index)    
        item = index.model().data(index, QtCore.Qt.UserRole)
        zoom = max((item.clip.outClip - item.clip.inClip)+item.client.edits.zoom ,1)
        painter.save()    
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        option.text = ""  
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)
        
        #Frame around
        pen = QtGui.QPen()
        pen.setWidth(1);
        pen.setBrush(QtGui.QColor("#303030"));  #FIXME: This needs to come from theme.
        pen.setCapStyle(QtCore.Qt.RoundCap);
        painter.setPen(pen)
        
        painter.drawRect(option.rect.left(), option.rect.top(), zoom -5, 95)   
        #shadow
        painter.fillRect(option.rect.left(), option.rect.top(), zoom -2, 97, QtGui.QColor("#202020"))
        
        #clip
        
        if option.state & QtGui.QStyle.State_MouseOver :
            backColor = QtGui.QColor("gray")
        else :
            backColor = QtGui.QColor("darkCyan")
            
        painter.fillRect(option.rect.left(), option.rect.top(), zoom -5, 95, backColor)
        
        #Description
        painter.translate(option.rect.left(), option.rect.top())
        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
        html.drawContents(painter, clip)
        

        html = QtGui.QTextDocument()
        html.setHtml(self.FORMATTER_TIMELINERANGE.format(width = zoom -10, inClip = str(item.clip.inClip).zfill(2), outClip=str(item.clip.outClip).zfill(2)))

        painter.translate(0, 70)
        clip = QtCore.QRectF(0, 0, option.rect.width(), 30)
        html.drawContents(painter, clip)
        painter.restore()    

    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        item = index.model().data(index, QtCore.Qt.UserRole)   
        zoom = item.client.edits.zoom
        return QtCore.QSize(max((item.clip.outClip - item.clip.inClip) + zoom, 1) , 100 + zoom)  


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


class treeClip(QtGui.QTreeWidgetItem):
    ''' same clip for tree widget '''
    def __init__(self, parent, *args, **kwargs):
        QtGui.QTreeWidgetItem.__init__(self, *args, **kwargs)
        
        self.parent = parent
        self.setFont(0, QtGui.QFont("verdana", 10))       
        self.setForeground(0, QtGui.QBrush(QtGui.QColor("white")))

    def update(self):
        self.setText(0, str(self.parent.clip.scene).zfill(3) + ' - ' + str(self.parent.clip.shot).zfill(3))
        

    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        

        if self.parent.clip.scene == other.parent.clip.scene :
            return self.parent.clip.shot > other.parent.clip.shot
        else :
            return self.parent.clip.scene > other.parent.clip.scene

class animTreeItem(QtGui.QTreeWidgetItem):
    ''' Item for animation scenes '''
    def __init__(self, parent, item, *args, **kwargs):
        QtGui.QTreeWidgetItem.__init__(self, *args, **kwargs)
        
        self.parent     = parent
        self.item       = item 
        self.path       = QtGui.QTreeWidgetItem(self)
        self.filename   = QtGui.QTreeWidgetItem(self)
        self.version    = QtGui.QTreeWidgetItem(self)
        self.state      = QtGui.QTreeWidgetItem(self)
        self.date       = QtGui.QTreeWidgetItem(self)
        self.user       = QtGui.QTreeWidgetItem(self)
        #self.setFont(0, QtGui.QFont("verdana", 10))       
        #self.setForeground(0, QtGui.QBrush(QtGui.QColor("white")))
    def update(self, item):
        self.item = item
        self.setText(0, self.item.filename + " (" + str(self.item.version) + ")")

        self.path.setText       (0,"file path : "   + item.path                         )
        self.filename.setText   (0,"file name : "   + item.filename                     )
        self.version.setText    (0,"version : "     + str(item.version)                 )
        self.state.setText      (0,"state : "       + str(item.state)                   )
        self.date.setText       (0,"comments : "    + item.date.toString("dd-MM hh:mm") )
        user = "Unknown"

        if item.userUid in self.item.client.users.users :
                 
            user = self.item.client.users.users[item.userUid].login
        self.user.setText       (0,"user : "        + user                              )


class ClipTimeline(QtGui.QListWidgetItem):
    FORMATTER_CLIP = unicode(util.readfile("edits/formatters/timeline.qthtml"))
    
    def __init__(self, parent, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)     
        self.parent     = parent
        self.viewText   = ""
        


    def data(self, role):
#        if role == QtCore.Qt.DisplayRole:
#            return self.display()  
        if role == QtCore.Qt.UserRole :
            return self.parent
        return super(ClipTimeline, self).data(role)

    def display(self):
        return self.text()


    def update(self):
        self.setText(self.FORMATTER_CLIP.format(scene = str(self.parent.clip.scene).zfill(3), shot = str(self.parent.clip.shot).zfill(3), inClip = str(self.parent.clip.inClip).zfill(2), outClip = str(self.parent.clip.outClip).zfill(2), handleIn = str(self.parent.clip.handleIn).zfill(2), handleOut = str(self.parent.clip.handleOut).zfill(2)))

    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.parent.client: return True # If not initialized...
        if not other.parent.client: return False;

        # Default: Alphabetical
        return self.parent.clip.start < other.parent.clip.start

class Clip(QtGui.QListWidgetItem):

    '''
    A clip is the representation of a scene and a shot.
    '''

    TEXTWIDTH = 150
    CLIPSIZE = 25
    PADDING = 5
    WIDTH = TEXTWIDTH
    
    FORMATTER_CLIP = unicode(util.readfile("edits/formatters/clip.qthtml"))
    
    def __init__(self, clip, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        
        self.clip = clip
        self.client = self.clip.client

       
        self.treeItem       = treeClip(self)
        self.timelineItem   = ClipTimeline(self)
        self.animTreeItem   = QtGui.QTreeWidgetItem(self.treeItem)
        self.commentsItem    = QtGui.QTreeWidgetItem(self.treeItem)

        self.animTreeItem.setText(0, "Animation Scenes")
        self.commentsItem.setText(0, "Comments")
        
        self.treeItem.addChild(self.animTreeItem)
        
        self.comments = {}
        self.animScene  = {}
    
    def update(self):
        '''     
        Updates this item
        '''

        #remove all comments
        self.commentsItem.takeChildren()

        self.treeItem.update()
        self.timelineItem.update()
        
        self.setText(self.FORMATTER_CLIP.format(scene = str(self.clip.scene).zfill(3), shot = str(self.clip.shot).zfill(3), inClip = str(self.clip.inClip).zfill(2), outClip = str(self.clip.outClip).zfill(2), handleIn = str(self.clip.handleIn).zfill(2), handleOut = str(self.clip.handleOut).zfill(2)))
    
    
    def updateScene3d(self, scene):
        if scene.uid in self.animScene :
            self.animScene[scene.uid].update(scene)
        else :
            self.animScene[scene.uid] = animTreeItem(self.animTreeItem, scene)
            self.animTreeItem.addChild(self.animScene[scene.uid])
            self.animScene[scene.uid].update(scene)        
    
    def updateComment(self, comment):
        uid = comment.useruid
        self.comments[uid] = comment
        self.updateComments()

        
    def updateComments(self):
        self.commentsItem.takeChildren()
        for uid in self.comments :
            comment = self.comments[uid]
            user = "Unknown"
            if comment.useruid in self.clip.client.users.users :
                user = self.clip.client.users.users[comment.useruid].login
            c = QtGui.QTreeWidgetItem(self.commentsItem)          
            c.setText(0, (user + " (" + comment.date.toString("dd-MM hh:mm") + ") : " + comment.comment))
        
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;

        # Default: Alphabetical

        return self.clip.start < other.clip.start