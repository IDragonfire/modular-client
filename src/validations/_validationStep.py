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





from PyQt4 import QtCore, QtGui

import util, os, string

FormClass, BaseClass = util.loadUiType("validations/validation_step.ui")

from validation import ValidationClip, ValidationClipItemDelegate

class ValidationStepWidget(FormClass, BaseClass):
    def __init__(self, validations, step, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.validations    = validations
        self.client         = validations.client
        self.step           = step       
        
        self.validations.horizontalLayout.addWidget(self)
            
        self.tasks      = {}
        self.tasksCheck = {}
        self.clips      = {}
        
        self.validationList.setItemDelegate(ValidationClipItemDelegate(self))
        
        for step in self.validations.client.pipeline.pipeline_steps :
            if self.step.uidStep == step :    
                self.stepGroup.setTitle(self.validations.client.pipeline.pipeline_steps[step].name)
                break

        self.getActualClips()
        
        self.client.clips.clipUpdated.connect(self.clipUpdate)
        self.client.clips.clipClicked.connect(self.clipSelection)
        self.client.clips.filterScene.textChanged.connect(self.eventFilterChanged)
        
        
        self.client.comments.commentInfoUpdated.connect(self.commentUpdate)        
        
        
        
        self.NothingCheckBox.stateChanged.connect(self.filterChanged)
        self.WipCheckBox.stateChanged.connect(self.filterChanged)
        self.ApprovalCheckBox.stateChanged.connect(self.filterChanged)
        self.ApprovedCheckBox.stateChanged.connect(self.filterChanged)
        self.RetakeCheckBox.stateChanged.connect(self.filterChanged)
        
        self.validationList.itemPressed.connect(self.itemPressed)
        
    def itemPressed(self, item):
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton:
            item.stepPressed()
        
    def eventFilterChanged(self):
        if self.client.clips.filterScene.text() == "" :
            for uid in self.clips :
                self.clips[uid].filtered = False
                self.clips[uid].update()      
        else :        
            filterText = filter(lambda x: x.isdigit(), self.client.clips.filterScene.text())
            
            if filterText == "" :
                return 
            for uid in self.clips :   
                if self.clips[uid].clip.scene == int(filterText) :
                    self.clips[uid].filtered = False
                else :
                    self.clips[uid].filtered = True
                self.clips[uid].update()
                    
    def filterChanged(self):
        ''' this function filter all clips depending of their state '''
        for uid in self.clips :
            self.clips[uid].update()
        
    def clipSelection(self, item):
        ''' we have selected a clip'''
        if item.uid in self.clips :
            self.validationList.setCurrentItem(self.clips[item.uid])            
    
    def clipRefresh(self, uid):
        if uid in self.clips :
            self.clips[uid].update()
    
    def clipUpdate(self, clip):
        uid = clip.uid
        if uid in self.clips :           
            self.clips[uid].update()
        else :
            self.clips[uid] = ValidationClip(clip, self)
            self.clips[uid].update()
            self.validationList.addItem(self.clips[uid])

    def getActualClips(self):
        for uid in self.client.clips.clips :
            self.clipUpdate(self.client.clips.clips[uid])

    def addValidator(self, validator):
        taskuid = validator.taskUid
        if taskuid in self.tasks :
            clipuid  = validator.clipUid
            if clipuid in self.clips :
                self.clips[clipuid].addValidator(validator)

    def commentUpdate(self, comment):
        print comment
        
    def addTask(self, task) :
        uid = task.uid
        if not uid in self.tasks :
            self.tasks[uid] = task
             
        if not uid in self.tasksCheck :
            self.tasksCheck[uid] = QtGui.QCheckBox(self)
            
        self.tasksCheck[uid].setText(self.tasks[uid].name)
        self.tasksCheck[uid].setChecked(True)
        self.tasksCheck[uid].setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgb(255, 255, 255), stop:1 "+task.color+")")        
        self.tasksGroup.layout().addWidget(self.tasksCheck[uid])
        
        #adding the task to the validator widget
        if not uid in self.validations.tasks :
            self.validations.tasks[uid] = self

        #TODO: for now, all clips have all tasks. We have to make it per clip
        for uid in self.clips :
            self.clips[uid].addTask(task)
