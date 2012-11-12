from PyQt4 import QtCore, QtGui
from validations.validator import Validator

import util

class scenes3d(QtCore.QObject):
    scene3dInfoUpdated     = QtCore.pyqtSignal(Validator)
    
    def __init__(self, client, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.client = client
        self.animScenes = {}      
        self.client.mayaAnimUpdated.connect(self.processAnimSceneInfo)       

    def processAnimSceneInfo(self, message):
        uid = message["uid"]       
        if uid in self.animScenes: 
            self.animScenes[uid].update(message, self.client) 
        else :
            self.animScenes[uid] = Validator(uid)
            self.animScenes[uid].update(message, self.client)
            
        # we send a signal for whoever want it.   
        self.scene3dInfoUpdated.emit(self.animScenes[uid])
        self.client.validatorUpdated.emit(self.animScenes[uid])