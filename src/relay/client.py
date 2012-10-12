#import site 
#site.addsitedir(r"c:/Python26/Lib/site-packages/")
#
#import sys
#
#sys.path.append("c:/workspace/nam_client/src")
#
#import relay.client as client
#reload(client)
#npmclient = client.npmClient()
#
#npmclient.send(dict(action= "select", command= "projects", uid= 1))
#
#
#npmclient.stop()


import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QStringList', 2)
sip.setapi('QList', 2)
sip.setapi('QProcess', 2)

from PyQt4 import QtCore, QtGui
from PyQt4 import QtNetwork
import util
import logging
import time
import json

logger= logging.getLogger("npm.client")
logger.setLevel(logging.DEBUG)

class npmClient(object) :
    def __init__(self, app = None) :
        self.socket = QtNetwork.QLocalSocket()  

        self.blockSize = 0   
        

        self.app = app
        
        self.answered = []
        self.breakWait = False
        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.disconnectedFromServer)
        
        self.socket.connectToServer("npmClient")
        if not self.socket.waitForConnected(1000) :
            self.displayMessage("error", "Cannot connect to the server.")
            self.stop()


     
    def stop(self) :
        if self.socket.state() == QtNetwork.QLocalSocket.ConnectedState:
            self.socket.disconnectFromServer()
        
    def readFromServer(self) :
        
        ins = QtCore.QDataStream(self.socket)        
        ins.setVersion(QtCore.QDataStream.Qt_4_2)
        
        while ins.atEnd() == False :
            if self.blockSize == 0:
                if self.socket.bytesAvailable() < 4:
                    return
                self.blockSize = ins.readUInt32()            
            if self.socket.bytesAvailable() < self.blockSize:
                return
            
            action = ins.readQString()
            self.process(action)
            self.blockSize = 0

    def process(self, action):
        '''
        A fairly pythonic way to process received strings as JSON messages.
        '''
        
        action = json.loads(action)
        
        if "command" in action :
            if action["command"] == "notice" :
                self.displayMessage(action["style"], action["text"])
                self.breakWait = True
                return
        self.answered.append(action)
       
        self.function(self.answered, *self.args)
        

        
    def writeToServer(self, action, function, *args, **kw):
        '''
        This method is the workhorse of the client, and is used to send messages, queries and commands to the server.
        '''
        logger.debug("Client: " + action)
        
        block = QtCore.QByteArray()
        out = QtCore.QDataStream(block, QtCore.QIODevice.ReadWrite)
        out.setVersion(QtCore.QDataStream.Qt_4_2)

        out.writeUInt32(0)
        out.writeQString(action)

        out.device().seek(0)        
        out.writeUInt32(block.size() - 4)
        self.bytesToSend = block.size() - 4
        
        self.socket.write(block)
        self.answered = []
        self.function = function
        self.args = args
        

    def send(self, message, function, *args):
        data = json.dumps(message)
        logger.info("Outgoing JSON Message: " + data)
        self.writeToServer(data, function, *args)


    def askQuestion(self, question):
        if self.app :
            reply = QtGui.QMessageBox.question(self.app, "Question from server",
                    question,
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Yes:
                return True
            elif reply == QtGui.QMessageBox.No:
                return False
            else:
                return False

        return False


    def displayMessage(self, style, message):
        if style == "error" :
            if self.app :
                QtGui.QMessageBox.critical(self.app, "Error from Server", message)
            else :
                logger.error(message)
        elif style == "warning":
            if self.app :
                QtGui.QMessageBox.warning(self.app, "Warning from Server", message)
            else :
                logger.warn(message)
        else:
            if self.app :         
                QtGui.QMessageBox.information(self.app, "Notice from Server", message)
            else :
                logger.info(message)

    def waitForAnswer(self):
        startTime = time.time()
        while self.answered == [] and self.breakWait == False :            
            if time.time() - startTime > 1 :
                self.displayMessage("error", "No answer from the server.")
                break
            QtCore.QCoreApplication.processEvents()
        return self.answered

    def disconnectedFromServer(self) :
        pass