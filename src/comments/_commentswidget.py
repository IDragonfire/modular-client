from PyQt4 import QtCore, QtGui
import util


class Comment(QtCore.QObject):
    def __init__(self, uid, *args, **kwargs):
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
        self.date = QtCore.QDateTime.fromString(date, "yyyy-MM-dd hh:mm:ss") 
        self.message    = message


class comments(QtCore.QObject):
    def __init__(self, client, *args, **kwargs):
        self.client = client
        self.comments = {}      
        self.client.commentUpdated.connect(self.processCommentInfo)       

    def processCommentInfo(self, message):
        uid = message["uid"]       
        if uid in self.comments: 
            self.comments[uid].update(message, self.client) 
        else :
            self.comments[uid] = Comment(uid)
            self.comments[uid].update(message, self.client)
            
        #update clips comments
        clipUid = self.comments[uid].clipuid
        if clipUid in self.client.storyboard.clips :
            self.client.storyboard.clips[clipUid].storyItem.update()
            
        if clipUid in self.client.edits.clips :
            self.client.edits.clips[clipUid].updateComment()
                
    def getComments(self, clipuid, typeuid):
        comments = []
        for uid in self.comments :
            comment = self.comments[uid]
            if comment.clipuid == clipuid and comment.typeuid == typeuid :
                comments.append(comment)
        return comments
        