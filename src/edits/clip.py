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
        zoom = max((item.outClip - item.inClip)+item.client.edits.zoom ,1)
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
        html.setHtml(self.FORMATTER_TIMELINERANGE.format(width = zoom -10, inClip = str(item.inClip).zfill(2), outClip=str(item.outClip).zfill(2)))

        painter.translate(0, 70)
        clip = QtCore.QRectF(0, 0, option.rect.width(), 30)
        html.drawContents(painter, clip)
        painter.restore()    

    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        item = index.model().data(index, QtCore.Qt.UserRole)   
        zoom = item.client.edits.zoom
        return QtCore.QSize(max((item.outClip - item.inClip) + zoom, 1) , 100 + zoom)  


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
        self.setText(0, str(self.parent.scene).zfill(3) + ' - ' + str(self.parent.shot).zfill(3))
        

    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        

        if self.parent.scene == other.parent.scene :
            return self.parent.shot > other.parent.shot
        else :
            return self.parent.scene > other.parent.scene

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
        self.comments   = QtGui.QTreeWidgetItem(self)
        self.user       = QtGui.QTreeWidgetItem(self)
        #self.setFont(0, QtGui.QFont("verdana", 10))       
        #self.setForeground(0, QtGui.QBrush(QtGui.QColor("white")))
    def update(self, item):
        self.item = item
        self.setText(0, self.item.filename + " (" + str(self.item.version) + ")")

        self.path.setText       (0,"file path : "   + item.path         )
        self.filename.setText   (0,"file name : "   + item.filename     )
        self.version.setText    (0,"version : "     + str(item.version) )
        self.state.setText      (0,"state : "       + str(item.state)   )
        self.comments.setText   (0,"comments : "    + str(item.comments))
        user = "Unknown"
        if item.userUid in self.item.client.users.users : 
            user = self.item.client.users.users[item.userUid].login
        self.user.setText       (0,"user : "        + user              )


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
        self.setText(self.FORMATTER_CLIP.format(scene = str(self.parent.scene).zfill(3), shot = str(self.parent.shot).zfill(3), inClip = str(self.parent.inClip).zfill(2), outClip = str(self.parent.outClip).zfill(2), handleIn = str(self.parent.handleIn).zfill(2), handleOut = str(self.parent.handleOut).zfill(2)))

    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.parent.client: return True # If not initialized...
        if not other.parent.client: return False;

        # Default: Alphabetical
        return self.parent.start < other.parent.start

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
       
        self.treeItem       = treeClip(self)
        self.timelineItem   = ClipTimeline(self)
        self.animTreeItem   = QtGui.QTreeWidgetItem(self.treeItem)
        self.commentsItem    = QtGui.QTreeWidgetItem(self.treeItem)

        self.animTreeItem.setText(0, "Animation Scenes")
        self.commentsItem.setText(0, "Comments")
        
        #self.treeItem.addChild(self.animTreeItem)
        self.inClip     = 0
        self.outClip    = 0
        self.start      = 0
        self.end        = 0
        self.duration   = 0
        self.handleIn   = 0
        self.handleOut  = 0
        self.comments   = None
        self.animScene  = {}
    
    def addAnimScene(self, scene):
        if scene.uid in self.animScene :
            self.animScene[scene.uid].update(scene)
        else :
            self.animScene[scene.uid] = animTreeItem(self.animTreeItem, scene)
            self.animTreeItem.addChild(self.animScene[scene.uid])
            self.animScene[scene.uid].update(scene)
            

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

        #remove all comments
        self.commentsItem.takeChildren()
        
        self.comments = self.client.comments.getComments(self.uid, 0)  
        for comment in self.comments :
            user = "Unknown"
            if comment.useruid in self.client.users.users : 
                user = self.client.users.users[comment.useruid].login
                c = QtGui.QTreeWidgetItem(self.commentsItem)
                print c
                print comment.comment
                c.setText(0, (user + " (" + comment.date.toString("dd-MM hh:mm") + ") :" + comment.comment))
        
        
        self.treeItem.update()
        self.timelineItem.update()
        
        self.setText(self.FORMATTER_CLIP.format(scene = str(self.scene).zfill(3), shot = str(self.shot).zfill(3), inClip = str(self.inClip).zfill(2), outClip = str(self.outClip).zfill(2), handleIn = str(self.handleIn).zfill(2), handleOut = str(self.handleOut).zfill(2)))
    
    def updateComment(self):
        #remove all comments
        self.commentsItem.takeChildren()
        
        self.comments = self.client.comments.getComments(self.uid, 0)  
        for comment in self.comments :
            user = "Unknown"
            if comment.useruid in self.client.users.users : 
                user = self.client.users.users[comment.useruid].login
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

        return self.start < other.start