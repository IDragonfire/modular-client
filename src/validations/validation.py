from PyQt4 import QtGui, QtCore
import util

class ValidationClipItemDelegate(QtGui.QStyledItemDelegate):
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
        clip = index.model().data(index, QtCore.Qt.UserRole)
        self.initStyleOption(option, index)
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(240)
        return QtCore.QSize(215, clip.height)  

class ValidationClip(QtGui.QListWidgetItem):
    '''
    A Validation clip is the representation of a clip task.
    '''
    FORMATTER_CLIP          = unicode(util.readfile("validations/formatters/validationclip.qthtml"))
    FORMATTER_CLIPHEADER    = unicode(util.readfile("validations/formatters/validationclipheader.qthtml"))
    
    def __init__(self, clip, parent, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        self.clip       = clip
        self.parent     = parent
        self.client     = self.clip.client
        self.validators = {}
        self.tasks      = {}
        self.filtered   = False
        self.height     = 50
        self.viewtext   = None
       
        self.approvalWait   = False
       
    def gradeColor(self, color, state):
        '''
        This function is decaying the color depending of the state of the task
        '''
        qtcolor = QtGui.QColor()
        qtcolor.setNamedColor(color)
        sat = 0
        if state    == -1 :
            sat = 0.2
        elif state  == 0 :
            sat = 0.4
        elif state  == 1 :
            sat = 0.6
        elif state  == 2 :
            sat = 0.8
        elif state  == 3 :
            sat = 1.0
        qtcolor.setHsvF(qtcolor.hueF(), sat, qtcolor.valueF())
        return qtcolor.name()

    def versionColor(self, color):
        qtcolor = QtGui.QColor()
        qtcolor.setNamedColor(color)
        qtcolor.setHsvF(qtcolor.hueF(), qtcolor.saturationF(), qtcolor.valueF()-.4)
        return qtcolor.name()              
        
    def update(self):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.height     = 30

        self.setHidden(True)
        self.approvalWait = False
        
        if self.filtered :
            return
        
        self.viewtext = self.FORMATTER_CLIPHEADER.format(scene = self.clip.scene, shot = self.clip.shot)

        for uid in self.tasks :
            self.height = self.height + 60
            task = self.tasks[uid]

            version   = 0
            displayvalidator = None
            for validuid in self.validators :
                # we need the highest version for now
                if self.validators[validuid].taskUid == uid :
                    validator = self.validators[validuid]
                    if validator.version > version :
                        displayvalidator = validator                     
      
            # color grading
            color = task.color
            if displayvalidator :
                state = displayvalidator.state
                
                if state == 0 and self.parent.WipCheckBox.checkState() :
                    self.setHidden(False)
                elif state == 1 and self.parent.ApprovalCheckBox.checkState() :
                    self.setHidden(False)
                    self.approvalWait = True
                elif state == 2 and self.parent.ApprovedCheckBox.checkState() :
                    self.setHidden(False)
                elif state == 3 and self.parent.RetakeCheckBox.checkState() :
                    self.setHidden(False)
                
                colorSat = self.gradeColor(color, state)
                self.viewtext  += self.FORMATTER_CLIP.format(color2 = color, color = colorSat, info = displayvalidator.filename, version = displayvalidator.version, date = displayvalidator.date.toString("dd-MM hh:mm")) 
            else :

                self.viewtext  += self.FORMATTER_CLIP.format(color2 = color, color = self.gradeColor(color, -1), info = "", version = "", date = "")
                if self.parent.NothingCheckBox.checkState() :
                    self.setHidden(False)

    def stepPressed(self):
        canDisplay = False
        menu = QtGui.QMenu(self.client)
        
        if self.approvalWait :
            canDisplay      = True
            actionValidate  = QtGui.QAction("Validate", menu)
    
            if self.client.power <= 16 :
                actionValidate.setDisabled(True)
        
        # Triggers
            actionValidate.triggered.connect(self.validate)
    
            menu.addAction(actionValidate)
        
        if canDisplay :    
            menu.popup(QtGui.QCursor.pos())


    def validate(self):
        tasksToValidate = {}
        for uid in self.tasks :
            task = self.tasks[uid]

            version   = 0
            displayvalidator = None
            for validuid in self.validators :
                # we need the highest version for now
                if self.validators[validuid].taskUid == uid :
                    validator = self.validators[validuid]
                    if validator.version > version :
                        displayvalidator = validator 
            
            if displayvalidator :
                if displayvalidator.state == 1 :    
                    tasksToValidate[task.name] = displayvalidator
            
        items = []    
        for name in tasksToValidate :
            items.append(name)
        item, ok = QtGui.QInputDialog.getItem(self.client, "Select the task to validate",
                "Task to validate:", items, 0, False)
        if ok and item:
            print tasksToValidate[item].uid
            #TODO : send validation to server
    
    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.display()  
        elif role == QtCore.Qt.UserRole :
            return self
        return super(ValidationClip, self).data(role)

    def display(self):
        return self.viewtext        
        
    def addValidator(self, validator):
        uid = validator.uid
        if not uid in self.validators :
            self.validators[uid] = validator
        self.update()
        
    def addTask(self, task):
        uid = task.uid
        if not uid in self.tasks :
            self.tasks[uid] = task
        self.update()
        
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;


        return self.clip.start < other.clip.start