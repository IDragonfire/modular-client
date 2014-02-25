from PyQt4 import QtCore, QtGui
from friendlist.friendlistudialog import FriendListDialog



class FriendList():

    def __init__(self, client):
        self.client = client
        self.dialog = FriendListDialog(client)

    def addUser(self, user):
        print 'addUser'

    def addFriend(self, username):
        print 'addFriend'