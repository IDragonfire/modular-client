from PyQt4 import QtCore, QtGui
import util
from PyQt4.Qt import QModelIndex

FormClass, BaseClass = util.loadUiType("friendlist/friendlist.ui")
class FriendListDialog(FormClass, BaseClass):
    def __init__(self, client):
        BaseClass.__init__(self, client)
        self.setupUi(self)

        self.model = FriendListModel([FriendGroup('online'), FriendGroup('offline')], client)
        self.friendlist.setModel(self.model)

        self.friendlist.header().setStretchLastSection(False);
        self.friendlist.header().resizeSection (1, 48)
        self.friendlist.header().resizeSection (2, 64)
        self.friendlist.header().resizeSection (3, 18)

        # stretch first column
        self.friendlist.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.friendlist.expandAll()

        # Frameless
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)

        # later use rubberband
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle)

    def addFriend(self, groupIndex, username):
        n = len(self.model.root[groupIndex].users)
        self.model.beginInsertRows(self.model.index(groupIndex, 0, QtCore.QModelIndex()), n, n)
        self.model.root[groupIndex].addUser(username)
        self.model.endInsertRows()
        #self.model.emit(QtCore.SIGNAL('dataChanged'), QtCore.QModelIndex(), QtCore.QModelIndex())

    def removeFriend(self, groupIndex, username):
        row = self.model.root[groupIndex].getRowOfUser(username)
        if row > 0:
            self.model.beginRemoveRows(self.model.index(groupIndex, 0, QtCore.QModelIndex()), row, row)
            del self.model.root[groupIndex].users[row]
            self.model.endRemoveRows()
        #self.model.emit(QtCore.SIGNAL('dataChanged'), QtCore.QModelIndex(), QtCore.QModelIndex())

class FriendGroup():
    def __init__(self, name):
        self.name = name
        self.users = []

    def addUser(self, user):
        self.users.append(User(user, self))

    def getRowOfUser(self, user):
        for i in xrange(0, len(self.users)):
            if self.users[i].username == user:
                return i
        return -1

class User():
    def __init__(self, username, group):
        self.username = username
        self.group = group

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username


class FriendListModel(QtCore.QAbstractItemModel):
    def __init__(self, groups, client):
        QtCore.QAbstractItemModel.__init__(self)
        self.root = groups
        self.client = client

        self.header = ['Player', 'land', 'rating', '#']

    def columnCount(self, parent):
        return len(self.header);

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parentIndex):
        pointer = parentIndex.internalPointer()
        # if root level
        if pointer is None:
            return len(self.root)
        # if on FriendGroup level
        if hasattr(pointer, 'users'):
            return len(pointer.users)
        return 0

    def index(self, row, column, parentIndex):
        pointer = parentIndex.internalPointer()
        # if root element, use root list
        if pointer is None:
            return self.createIndex(row, column, self.root[row])
        # if on FriendGroup level
        if hasattr(pointer, 'users'):
            return self.createIndex(row, column, pointer.users[row])
        return self.createIndex(row, column, None)

    def data(self, index, role):
        if not index.isValid():
            return None
        pointer = index.internalPointer()
        if role == QtCore.Qt.DecorationRole and hasattr(pointer, 'username') and index.column() == 0:
            indent = 6
            pix = QtGui.QPixmap(40+16 + indent, 20)
            pix.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pix)

            avatar =  self.client.getUserAvatar(pointer.username)
            if avatar:
                avatar = util.respix(avatar["url"])
                if avatar:
                    painter.drawPixmap(0, 0, avatar)

            country = self.client.getUserCountry(pointer.username)
            if country != None:
                painter.drawPixmap(40 + indent, 2, util.icon("chat/countries/%s.png" % country.lower(), pix=True))
            painter.end()

            return pix


        if role == QtCore.Qt.DisplayRole:
            if hasattr(pointer, 'name'):
                if index.column() == 0:
                    return pointer.name
                return None
            else:
                if index.column() == 1:
                    return self.client.getUserCountry(pointer.username)
                if index.column() == 2:
                    return self.client.getUserRanking(pointer.username)
                if index.column() == 3:
                    return '#'
                return pointer.username

        return None

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        pointer = index.internalPointer()
        if hasattr(pointer, 'users'):
            return QtCore.QModelIndex()
        else:
            row = 0 if pointer.group == 'online' else 1
            return self.createIndex(row, 0, pointer.group)
