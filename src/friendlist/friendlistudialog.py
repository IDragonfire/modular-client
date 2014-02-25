from PyQt4 import QtCore, QtGui
import util

FormClass, BaseClass = util.loadUiType("friendlist/friendlist.ui")
class FriendListDialog(FormClass, BaseClass):
    def __init__(self, client):
        BaseClass.__init__(self, client)
        self.setupUi(self)

        # Frameless
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)

        # later use rubberband
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle)