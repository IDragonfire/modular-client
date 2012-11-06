from PyQt4 import QtCore, QtGui
import util


class Comment(QtCore.QObject):

    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        self.clipuid    = None
        self.useruid    = None
        self.typeuid    = 0   
        self.comment    = None
        self.date       = None

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.clipuid    = message['clipuid']
        self.useruid    = message['useruid']
        self.typeuid    = message['typeuid']
        self.comment    = message['comment']
        date            = message['date']      
        self.date       = QtCore.QDateTime.fromString(date, "yyyy-MM-dd hh:mm:ss") 
        self.message    = message


class comments(QtCore.QObject):
    commentInfoUpdated     = QtCore.pyqtSignal(Comment)
    
    def __init__(self, client, *args, **kwargs):       
        QtCore.QObject.__init__(self, *args, **kwargs)
        
        self.client = client
        self.comments = {}      
        self.client.commentUpdated.connect(self.processCommentInfo)       
        #self.client.clips.clipUpdated.connect(self.clipUpdated)

    def processCommentInfo(self, message):
        uid = message["uid"]       
        if uid in self.comments: 
            self.comments[uid].update(message, self.client) 
        else :
            self.comments[uid] = Comment(uid)
            self.comments[uid].update(message, self.client)
            
        self.commentInfoUpdated.emit(self.comments[uid])


    
    def getComments(self, clipuid, typeuid):
        comments = []
        for uid in self.comments :
            comment = self.comments[uid]
            if comment.clipuid == clipuid and comment.typeuid == typeuid :
                comments.append(comment)
        return comments

        
        
