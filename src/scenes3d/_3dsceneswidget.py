from PyQt4 import QtCore, QtGui
import util


class MayaAnimScene(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
        self.uid        = uid
        self.client     = None
        self.clipUid    = None   
        self.userUid    = None
        self.path       = None
        self.filename   = None
        self.comments   = None   
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
        self.comments   = message['comments']
        self.userUid    = message['useruid']
        self.message    = message


class scenes3d(QtCore.QObject):
    def __init__(self, client, *args, **kwargs):
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
            
        # we have to link the scene with the edit clip.
        clipUid = self.animScenes[uid].clipUid
        if clipUid in self.client.edits.clips :
            #the clip exists
            self.client.edits.clips[clipUid].addAnimScene(self.animScenes[uid])
            
        