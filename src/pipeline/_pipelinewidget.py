from PyQt4 import QtCore, QtGui
import util
import random

colors = {
0 : "white",
1 : "#ff9900",
2 : "darkCyan",
3 : "blue",
4 : "darkGreen",
5 : "darkYellow",
6 : "cyan",
7 : "darkBlue",
8 : "darkGray",
9 : "black"
}

class Task(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        
        self.pipelineId = None
        self.name       = None
        self.message    = None
        random.seed(uid)
        color = random.randint(0,9)
        self.color      = colors[color]
        

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.name       = message["name"]
        self.pipelineId = message["pipelineId"]
        self.message    = message
        
                
class Step(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        self.index      = None
        self.uidStep    = None
        self.message    = None

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.index      = message["index"]
        self.uidStep    = message["uidStep"]
        self.message    = message
        

class PipelineStep(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid         = uid
        self.name        = None
        self.message     = None
        self.moduleName  = None
        self.messageName = None

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.name       = message['name']
        self.message    = message['module_name']
        self.moduleName = message['message_name']
        self.message    = message


class pipeline(QtCore.QObject):
    pipelineStepUpdated     = QtCore.pyqtSignal(PipelineStep)
    stepUpdated             = QtCore.pyqtSignal(Step)
    taskUpdated             = QtCore.pyqtSignal(Task)
    def __init__(self, client, *args, **kwargs):       
        QtCore.QObject.__init__(self, *args, **kwargs)
        
        self.client         = client
        self.pipeline_steps = {}  
        self.steps          = {}
        self.tasks          = {}
        
        self.client.pipelineStepUpdated.connect(self.processPipelineStepInfo)
        self.client.stepUpdated.connect(self.processStepInfo)       
        self.client.taskUpdated.connect(self.processTaskInfo)
     
     
    def getName(self, uid):
        '''Cross-referencing all the known pipeline step to get the name of this project step '''
        uidStep = self.steps[uid].uidStep
        if uidStep :
            if not uidStep in self.client.pipeline.pipeline_steps :
                return  "Unknown - Server Error ?"
            else : 
                name = self.client.pipeline.pipeline_steps[uidStep].name
                return name 
        else :
            return "Unknown - Server Error ?"
     
        
    def getMaxIndex(self):
        '''
        This method get the highest index in the current pipeline
        '''
        if len(self.steps) > 0 :
            return max(self.steps)
        else :
            return 0
    
    def processTaskInfo(self, message):
        ''' 
        This manage all the task messages for the current project.
        '''        
        uid     = message["uid"]
        pipelineId = message["pipelineId"]
        
        if pipelineId in self.steps: 
            if uid in self.tasks :
                self.tasks[uid].update(message, self.client)
            else :
                self.tasks[uid] = Task(uid)
                self.tasks[uid].update(message, self.client)   
            
            self.taskUpdated.emit(self.tasks[uid]) 
        else :
            QtGui.QMessageBox.error(self, "Error !", "A step doesn't exists in the project. That shouldn't happen, please report this.")    
    
    def processStepInfo(self, message):
        ''' 
        This manage all the step messages for the current project.
        '''
        uid     = message["uid"]
        uidStep = message["uidStep"]
        
        if uidStep in self.pipeline_steps: 
            if uid in self.steps :
                self.steps[uid].update(message, self.client)
            else :
                self.steps[uid] = Step(uid)
                self.steps[uid].update(message, self.client)   
            
            self.stepUpdated.emit(self.steps[uid]) 
        else :
            QtGui.QMessageBox.error(self, "Error !", "A step doesn't exists in the project. That shouldn't happen, please report this.")

    def processPipelineStepInfo(self, message):
        ''' 
        This manage all the pipeline step message
        these messages exists for all projects
        '''
        uid = message["uid"]       
        if uid in self.pipeline_steps: 
            self.pipeline_steps[uid].update(message, self.client) 
        else :
            self.pipeline_steps[uid] = PipelineStep(uid)
            self.pipeline_steps[uid].update(message, self.client)
            
        self.pipelineStepUpdated.emit(self.pipeline_steps[uid])



        
        
