from PyQt4 import QtGui, QtCore
import util, os

class textEditorDelegate(QtGui.QWidget):
    editingFinished = QtCore.pyqtSignal()   
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        
        qv = QtGui.QVBoxLayout( self )
        qh = QtGui.QHBoxLayout( )
        self.confirmed = False
        qh.addSpacing(420)
        self.qlabel = QtGui.QLabel()
        self.qlabel.setText( "Comments :" )
        qh.addWidget( self.qlabel )
        self.editor = QtGui.QTextEdit()
        qh.addWidget(self.editor)
        
        self.confirm = QtGui.QPushButton()
        self.confirm.setText("Confirm")

        qh2 = QtGui.QHBoxLayout( )
        qh2.addSpacing(420 + self.qlabel.width())
        
        qh2.addWidget(self.confirm)
        
        qv.insertLayout(0,qh)
        qv.insertLayout(1,qh2)

        self.confirm.pressed.connect(self.confirmEdit)
        
    def setText(self, text):
        self.editor.setText(text)

    def confirmEdit(self):
        self.confirmed = True
        self.editingFinished.emit()

class StoryItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent, *args, **kwargs):
        QtGui.QStyledItemDelegate.__init__(self, parent, *args, **kwargs)       
        self.parent = parent
        
    def paint(self, painter, option, index, *args, **kwargs):
        self.initStyleOption(option, index)     
        painter.save()
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        
        icon = QtGui.QIcon(option.icon)
        iconsize = icon.actualSize(option.rect.size())
      
        #clear icon and text before letting the control draw itself because we're rendering these parts ourselves
        option.icon = QtGui.QIcon()        
        option.text = ""  
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)
        #Shadow
        painter.fillRect(option.rect.left()+8-1, option.rect.top()+8-1, iconsize.width(), iconsize.height(), QtGui.QColor("#202020"))
        #Icon
        icon.paint(painter, option.rect.left()+5-2, option.rect.top()+5-2, iconsize.width(), iconsize.height(), QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        
        #Frame around the icon
        pen = QtGui.QPen()
        pen.setWidth(1);
        pen.setBrush(QtGui.QColor("#303030"));  #FIXME: This needs to come from theme.
        pen.setCapStyle(QtCore.Qt.RoundCap);
        painter.setPen(pen)
        painter.drawRect(option.rect.left()+5-2, option.rect.top()+5-2, iconsize.width(), iconsize.height())                
           
        #paint all the separations
        pen.setBrush(QtGui.QColor("silver"));  #FIXME: This needs to come from theme.
        painter.setPen(pen)
        painter.drawLine(iconsize.width()+60+8, option.rect.top()+5-2, iconsize.width()+60+8, option.rect.bottom()-5+2)
        
        #Description
        painter.translate(option.rect.left() + iconsize.width() + 10, option.rect.top()+10)
        clip = QtCore.QRectF(0, 0, option.rect.width()-iconsize.width() - 10 - 5, option.rect.height())
        html.drawContents(painter, clip)
        painter.restore()
    
    def createEditor(self, parent, styleOption, index):
        editor = textEditorDelegate(parent)
        editor.editingFinished.connect(self.commitAndCloseEditor)       
        return editor

    def setEditorData( self, editor, index ):
        value = index.model().data(index, QtCore.Qt.EditRole)
        #comments = value.getComments()
        for comment in value.comments :
            if comment.useruid in value.client.users.users :
                if value.client.users.users[comment.useruid].login == value.client.login :
                    editor.setText(comment.comment)
                    return
        editor.setText("")
        return

    def setModelData(self, editor, model, index):
        value = editor.editor.toPlainText()
        item = index.model().data(index, QtCore.Qt.UserRole) 
        if editor.confirmed :
            self.parent.client.send(dict(command="comments", action="submit", type = 0, comment=value, scene = item.parent.scene, shot = item.parent.shot))

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QtGui.QAbstractItemDelegate.NoHint)

    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)       
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(Story.TEXTWIDTH)
        return QtCore.QSize(Story.TEXTWIDTH + Story.PADDING, Story.ICONSIZE)  


class Story(QtGui.QListWidgetItem):

    '''
    A clip is the representation of a scene and a shot.
    '''
    TEXTWIDTH = 230
    ICONSIZE = 210
    PADDING = 10
    
    WIDTH = ICONSIZE + TEXTWIDTH
    FORMATTER_CLIP      = unicode(util.readfile("storyboard/formatters/story.qthtml"))
    FORMATTER_COMMENT   = unicode(util.readfile("storyboard/formatters/comment.qthtml"))
    
    def __init__(self, parent, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        self.parent = parent
        self.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        self.viewText = ""
      
    def update(self):
        '''     
        Updates this item from the message dictionary supplied
        '''
        imagePath = None
        icon = None
        
        if self.parent.client.currentProject.projectComp != None :
            imageName = ( "SC"+str(self.parent.scene).zfill(2)+"_"+str(self.parent.shot).zfill(2) + ".jpg") 
            imagePath = os.path.join("//sledge/vol1/projects", self.parent.client.currentProject.projectComp, "Production_info/Story/images", imageName) 
        if os.path.isfile(imagePath) :
            imagePath = util.cache(os.path.join(self.parent.client.currentProject.projectComp, "storyboard"), imagePath)
            util.delayedicon(imagePath, self, self.parent.client)
        else :
            icon = util.icon("storyboard/no_preview.jpg")

            self.setIcon(icon)
        #QtCore.QCoreApplication.processEvents()
        
        self.parent.getComments()
        commentText = ""
        for comment in self.parent.comments :
            user = "Unknown"
            if comment.useruid in self.parent.client.users.users : 
                user = self.parent.client.users.users[comment.useruid].login
            commentText = commentText + self.FORMATTER_COMMENT.format(comment = comment.comment, author = user, date = comment.date.toString("dd-MM hh:mm"))
        
        self.viewText = (self.FORMATTER_CLIP.format(comments = commentText, scene = str(self.parent.scene).zfill(3), shot = str(self.parent.shot).zfill(3), inClip=self.parent.inClip, outClip=self.parent.outClip ))

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.display()  
        elif role == QtCore.Qt.EditRole :
            return self.parent
        elif role == QtCore.Qt.UserRole :
            return self
        return super(Story, self).data(role)

    def display(self):
        return self.viewText

    def pressed(self, item):
        menu = QtGui.QMenu(self.parent.client)
        actionUploadImage = QtGui.QAction("Upload image", menu)
        actionUploadImage.triggered.connect(self.uploadImage)
        menu.addAction(actionUploadImage)
        menu.popup(QtGui.QCursor.pos())

    def uploadImage(self):
        compProject = os.path.join("//sledge/vol1/projects", self.client.currentProject.projectComp, "Production_info/Story/images") 
        options = QtGui.QFileDialog.Options()            
        options |= QtGui.QFileDialog.DontUseNativeDialog  
        fileName = QtGui.QFileDialog.getOpenFileName(self.parent.client,
        "Select the picture",
        compProject,
        "Jpg Files (*.jpg);;Png Files (*.png);;All Files (*)", options) 
        if fileName:
            self.client.send(dict(command="storyboard", action="image", file = fileName, clipuid = self.parent.uid))
  
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)

    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.parent.client: return True # If not initialized...
        if not other.parent.client: return False;
   
        # Default: Alphabetical
        return self.parent.start < other.parent.start