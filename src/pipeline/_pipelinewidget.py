from PyQt4 import QtCore, QtGui
import util


class Step(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        self.index      = None
        self.message    = None

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.index      = message['index']


class PipelineStep(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        self.name       = None
        self.message    = None

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.name       = message['name']
        self.message    = message


class pipeline(QtCore.QObject):
    pipelineStepUpdated     = QtCore.pyqtSignal(PipelineStep)
    stepUpdated             = QtCore.pyqtSignal(Step)
    def __init__(self, client, *args, **kwargs):       
        QtCore.QObject.__init__(self, *args, **kwargs)
        
        self.client = client
        self.pipeline_steps = {}  
        self.steps = {}
        
        self.client.pipelineStepUpdated.connect(self.processPipelineStepInfo)
        self.client.stepUpdated.connect(self.processStepInfo)       
        
    def getMaxIndex(self):
        '''
        This method get the highest index in the current pipeline
        '''
        if len(self.steps) > 0 :
            return max(self.steps)
        else :
            return 0
    
    def processStepInfo(self, message):
        ''' 
        This manage all the step message for the current project.
        '''
        uid = message["uid"]
        if uid in self.pipeline_steps: 
            if uid in self.steps :
                self.steps[uid].update(message, self.client)
            else :
                self.steps[uid] = Step(uid)
                self.steps[uid].update(message, self.client)   
            
            self.stepUpdated.emit(self.steps[uid])             
            
            
        else :
            QtGui.QMessageBox.error(self, "Error !", "A step doesn't exists in the clip. That shouldn't happen, please report this.")

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



        
        
