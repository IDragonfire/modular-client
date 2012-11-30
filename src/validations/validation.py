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
from random import choice
import util

from retakewidget import RetakeWidget

REASONS = ["C'est d\'la merde !", 
           "Faut arreter de deconner maintenant !", 
           "J\'ai vomi dans ma bouche.", 
           "Ton C4 est pret sur mon bureau.", 
           "J\'ai honte pour toi.",
           "J\'en ai vu des trucs moches, mais des comme ca, rarement !.",
           "AAAAAAAH MES YEUX FONDENT !!"
           ]

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
        self.clip           = clip
        self.parent         = parent
        self.client         = self.clip.client
        self.validators     = {}
        self.tasks          = {}
        self.filtered       = False
        self.height         = 50
        self.viewtext       = None
        self.tooltipText    = None
       
        self.approvalWait   = False
        self.approved       = False
       
    def gradeColor(self, color, state):
        '''
        This function is decaying the color depending of the state of the task
        '''
        qtcolor = QtGui.QColor()
        qtcolor.setNamedColor(color)
        sat = 0
        value = qtcolor.valueF()
        if state    == -1 :
            sat = 0.0
        elif state  == 0 :
            sat = 0.2
        elif state  == 1 :
            sat = 0.6
        elif state  == 3 :
            value = .7
            sat = 0.5
        elif state  == 2 :
            sat = 1.0

        qtcolor.setHsvF(qtcolor.hueF(), sat, value)
        return qtcolor.name()

    def versionColor(self, color):
        qtcolor = QtGui.QColor()
        qtcolor.setNamedColor(color)
        qtcolor.setHsvF(qtcolor.hueF(), qtcolor.saturationF(), qtcolor.valueF()-.4)
        return qtcolor.name()              
        
    def addClip(self, color, clip):
        if clip :
            
            state = clip.state
            add = False
            if state == 0 and self.parent.WipCheckBox.checkState() :
                self.setHidden(False)
                add = True
            elif state == 1 and self.parent.ApprovalCheckBox.checkState() :
                self.setHidden(False)
                self.approvalWait = True
                add = True
            elif state == 2 and self.parent.ApprovedCheckBox.checkState() :
                self.approved = True
                self.setHidden(False)
                add = True
            elif state == 3 and self.parent.RetakeCheckBox.checkState() :
                self.setHidden(False)
                self.retake = True
                add = True
                
            user = self.client.getUserName(clip.userUid)            
            colorSat = self.gradeColor(color, state)
            if add :
                self.height = self.height + 60
                self.viewtext  += self.FORMATTER_CLIP.format(color2 = color, color = colorSat, info = clip.filename, version = clip.version, user = user, date = clip.date.toString("dd-MM hh:mm")) 

    def getClipToDisplay(self, uid, state):
        returnValidator = None
        for validuid in self.validators :
            if self.validators[validuid].taskUid == uid :
                validator = self.validators[validuid]
                if state :
                    stateCheck = state
                else :
                    stateCheck = validator.state
                
                if validator.state == stateCheck :
                    if returnValidator :
                        if validator.version > returnValidator.version :
                            returnValidator = validator
                    else :
                        returnValidator = validator                
        return returnValidator
        
    
    def getComments(self):
        self.tooltipText = ''
        for uid in self.client.comments.comments :
            comment = self.client.comments.comments[uid]
            
            if comment.clipuid == self.clip.uid and comment.typeuid == self.client.pipeline.getModuleUid(self.parent.step.uidStep) :
                user = self.clip.client.getUserName(comment.useruid)
                
                self.tooltipText += user + " (" + comment.date.toString("dd-MM hh:mm") +") : \n" + comment.comment +"\n" 
                
        self.setToolTip(self.tooltipText)
    
    def update(self):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.height     = 30

        self.setHidden(True)
        self.approvalWait   = False
        self.approved       = False
        self.retake         = False
         
        if self.filtered :
            return
        
        self.viewtext = self.FORMATTER_CLIPHEADER.format(scene = self.clip.scene, shot = self.clip.shot)
        for uid in self.tasks :
            task = self.tasks[uid]

            ValidLastVersion    = self.getClipToDisplay(uid, None)
            ValidForValidation  = self.getClipToDisplay(uid, 1)
            ValidValidated      = self.getClipToDisplay(uid, 2)
            ValidRetake         = self.getClipToDisplay(uid, 3)

            # in some cases, we don't need to display some clips :
            if ValidLastVersion == ValidForValidation :
                ValidForValidation  = None
            
            if ValidLastVersion == ValidValidated :
                ValidValidated      = None
                self.approved       = False
            
            if ValidLastVersion == ValidRetake :
                ValidRetake         = None
                self.retake         = False
            # not displaying the last retake if we have a scene newer for validation or already approved
            
            if ValidRetake and ValidForValidation :
                if ValidRetake.version <  ValidForValidation.version :
                    ValidRetake         = None
                    self.retake         = False
            
            if ValidRetake and ValidValidated :
                if ValidRetake.version <  ValidValidated.version :
                    ValidRetake         = None
                    self.retake         = False
                
            
            # color grading
            color = task.color

            self.addClip(color, ValidValidated      )
            self.addClip(color, ValidForValidation  )
            self.addClip(color, ValidRetake         )
            self.addClip(color, ValidLastVersion    )
            
            if not ValidLastVersion and not ValidForValidation and not ValidRetake and not ValidValidated :
                self.height = self.height + 60
                self.viewtext  += self.FORMATTER_CLIP.format(color2 = color, color = self.gradeColor(color, -1), info = "", version = "", date = "", user = "")
                if self.parent.NothingCheckBox.checkState() :
                    self.setHidden(False)

            if self.retake :
                self.getComments()
                
    def stepPressed(self):
        canDisplay = False
        menu = QtGui.QMenu(self.client)

        if self.approvalWait :
            canDisplay      = True
            actionValidate  = QtGui.QAction("Validate", menu)
            actionRetake    = QtGui.QAction("Send to re-take", menu)
    
            if self.client.power <= 16 :
                actionValidate.setDisabled(True)
                actionRetake.setDisabled(True)        
                
            # Triggers
            actionRetake.triggered.connect(self.retake)
            actionValidate.triggered.connect(self.validate)
            menu.addAction(actionValidate)
            menu.addAction(actionRetake)
        
        elif self.approved :
            canDisplay      = True
            actionRetake    = QtGui.QAction("Send to re-take", menu)
            
            if self.client.power <= 16 :
                actionRetake.setDisabled(True)            

            # Triggers    
            actionRetake.triggered.connect(self.retake)
            menu.addAction(actionRetake)
        
        if canDisplay :    
            menu.popup(QtGui.QCursor.pos())

    def retake(self):
        tasksToRetake = {}
        for uid in self.tasks :
            task = self.tasks[uid]

            ValidLastVersion = self.getClipToDisplay(uid, 2)
            if ValidLastVersion :
                tasksToRetake[task.name] = ValidLastVersion   
            else :
                ValidLastVersion = self.getClipToDisplay(uid, 1)
                if ValidLastVersion :
                    tasksToRetake[task.name] = ValidLastVersion   
                    
        items = []    
        for name in tasksToRetake :
            items.append(name)
        if len(items) > 0 :
            retake = RetakeWidget(self, items, choice(REASONS))
            if retake.exec_() == 1 :
                reason  = retake.reasonTextEdit.toPlainText()
                task    = retake.taskListWidget.currentItem().text()
                
                if reason != '' :
                    if task in tasksToRetake :
                        clip = tasksToRetake[task]
                        moduleuid = self.client.pipeline.getModuleUid(self.parent.step.uidStep)
                        self.client.send(dict(command='validation', action = 'retake', uid=clip.uid, moduleuid=moduleuid, reason=reason))
                    else :
                        QtGui.QMessageBox.critical(self.client, "Error", "This clip has no task, I don't even know how you were able to click on it.")
                else :
                    QtGui.QMessageBox.critical(self.client, "Error", "You must enter a comment so the user knows what was wrong with his work.")

    def validate(self):
        tasksToValidate = {}
        for uid in self.tasks :
            task = self.tasks[uid]
            ValidLastVersion = self.getClipToDisplay(uid, 1)
   
            if ValidLastVersion :
                tasksToValidate[task.name] = ValidLastVersion   

        items = []    
        for name in tasksToValidate :
            items.append(name)
        if len(items) > 0 :
            item, ok = QtGui.QInputDialog.getItem(self.client, "Select the task to validate",
                    "Task to validate:", items, 0, False)
            if ok and item:
                clip = tasksToValidate[item]
                moduleuid = self.client.pipeline.getModuleUid(self.parent.step.uidStep)           
                self.client.send(dict(command='validation', action = 'validate', uid=clip.uid, moduleuid=moduleuid))            

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
