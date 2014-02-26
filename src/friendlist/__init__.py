from PyQt4 import QtCore, QtGui
from friendlist.friendlistudialog import FriendListDialog



class FriendList():

    def __init__(self, client):
        self.client = client
        self.dialog = FriendListDialog(client)
        self.users = set()

    def addUser(self, user):
        self.users.add(user)
        if self.client.isFriend(user):
            self.dialog.addFriend(0,user)
        #print 'addUser', user

    def removeUser(self, user):
        if user in self.users:
            self.users.remove(user)
        else:
            print 'not registered:', user

    def updateFriendList(self):
        print 'addFriend', self.client.friends
        for friend in self.client.friends:
            if friend in self.users:
                self.dialog.addFriend(0,friend)
            else:
                self.dialog.addFriend(1,friend)