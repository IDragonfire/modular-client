from PyQt4 import QtCore, QtGui

import util, os, string

from _validationStep import ValidationStepWidget as ValidationStep

FormClass, BaseClass = util.loadUiType("validations/validations.ui")


class validatorContainer(object):
    def __init__(self):
        self.validators = {}
    
    def update(self, validator):
        uid = validator.uid
        if not uid in self.validators :
            self.validators[uid] = validator

class ValidationsWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.validationsTab.layout().addWidget(self)
        
        self.steps      = {}
        self.tasks      = {}
        self.validators = {}
           
        self.client.pipeline.stepUpdated.connect(self.stepUpdate)
        self.client.pipeline.taskUpdated.connect(self.taskUpdate)
    
        self.client.validatorUpdated.connect(self.validatorUpdate)
        
    def validatorUpdate(self, validator):
        ''' 
        This is the function we use when a module has received
        something relevant to the validation process 
        '''
        uid = validator.taskUid
        
        if not uid in self.validators :
            self.validators[uid] = validatorContainer()
        self.validators[uid].update(validator)
        if uid in self.tasks :
            pass
    
    def stepUpdate(self, step):
        if not step.uid in self.steps :
            self.steps[step.uid] = ValidationStep(self, step)
        
        self.horizontalLayout.insertWidget(step.index, self.steps[step.uid])
        self.horizontalLayout.addStretch()
    
    def taskUpdate(self, task):
        if task.pipelineId in self.steps :
            self.steps[task.pipelineId].addTask(task)
        
        # We've received a new task, we can check all the validator that are relevant to it.
        if task.uid in self.validators :
            validators = self.validators[task.uid]
            for uid in validators.validators :
                validator = validators.validators[uid]
                
                self.steps[task.pipelineId].addValidator(validator)
            
        
        