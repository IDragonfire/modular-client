from PyQt4 import QtCore, QtGui

class ProjectGraph(QtGui.QGraphicsScene):
    def __init__(self, parent=None):
        super(ProjectGraph, self).__init__(parent) 
        
#        print "init"
#        self.setAcceptDrops(True)
        
    def dropEvent(self, event):
        print event.mimeData().text()
        print event.proposedAction()
        print "drop"
        event.acceptProposedAction()
        
    def dragEnterEvent(self, event) :
        print event
        event.acceptProposedAction()
        
    def dragMoveEvent(self, event):
        event.acceptProposedAction()