from PyQt4 import QtCore, QtGui
import util


class MayaAnimScene(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        self.client     = None
        self.clipUid    = None   
        self.userUid    = None
        self.path       = None
        self.filename   = None
        self.date       = None   
        self.message    = None
        self.version    = 0
        self.state      = 0

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.clipUid    = message['clipuid']        
        self.path       = message['path']
        self.filename   = message['filename']
        self.version    = message['version']
        self.state      = message['state']
        date            = message['date']
        self.date       = QtCore.QDateTime.fromString(date, "yyyy-MM-dd hh:mm:ss")
        self.userUid    = message['useruid']
        self.message    = message


class scenes3d(QtCore.QObject):
    scene3dInfoUpdated     = QtCore.pyqtSignal(MayaAnimScene)
    
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
            self.animScenes[uid] = MayaAnimScene(uid)
            self.animScenes[uid].update(message, self.client)
            
        # we send a signal for whoever want it.   
        self.scene3dInfoUpdated.emit(self.animScenes[uid])