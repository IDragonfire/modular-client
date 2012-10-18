from PyQt4 import QtGui, QtCore
import util
from users.user import User


FormClass, BaseClass = util.loadUiType("users/users.ui")


class UsersWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client

        self.client.usersTab.layout().addWidget(self)
        self.users = {}

        print self.client.userUpdated
        self.client.userUpdated.connect(self.processUserInfo)
    
    def processUserInfo(self, message):
        uid = message["uid"]
        if uid in self.users: 
            self.users[uid].update(message, self.client) 
        else :
            self.users[uid] = User(uid)
            self.userList.addItem(self.users[uid])
            self.users[uid].update(message, self.client)        