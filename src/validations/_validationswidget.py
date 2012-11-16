from PyQt4 import QtCore, QtGui

import util, os, string

from _validationStep import ValidationStepWidget as ValidationStep
from validator import Validator

FormClass, BaseClass = util.loadUiType("validations/validations.ui")

class ValidationsWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.validationsTab.layout().addWidget(self)
        
        self.steps          = {}
        self.tasks          = {}
        self.validators     = {}
           
        self.client.pipeline.stepUpdated.connect(self.stepUpdate)
        self.client.pipeline.taskUpdated.connect(self.taskUpdate)
    
        self.client.validatorUpdated.connect(self.validatorUpdate)

    def validatorUpdate(self, message):
        uid = message["uid"]       
        if uid in self.validators: 
            self.validators[uid].update(message, self.client) 
        else :
            self.validators[uid] = Validator(uid)
            self.validators[uid].update(message, self.client)
            
#        # we update the validator display
        if self.validators[uid].taskUid in self.tasks :
            self.tasks[self.validators[uid].taskUid].clipRefresh(self.validators[uid].clipUid)

        # we send a signal for whoever want it.   
        self.client.validatorObjUpdated.emit(self.validators[uid])

    
    def stepUpdate(self, step):
        if not step.uid in self.steps :
            self.steps[step.uid] = ValidationStep(self, step)
        self.horizontalLayout.insertWidget(step.index, self.steps[step.uid])
        self.horizontalLayout.addStretch()
    
    def taskUpdate(self, task):
        if task.pipelineId in self.steps :
            self.steps[task.pipelineId].addTask(task)
        
        # We've received a new task, we can check all the validator that are relevant to it.
        for uid in self.validators :
            if task.uid == self.validators[uid].taskUid :
                self.steps[task.pipelineId].addValidator(self.validators[uid])

                
            
        
        