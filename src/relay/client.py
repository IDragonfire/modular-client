#-------------------------------------------------------------------------------
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------





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
import random
#import win32com.client

logger= logging.getLogger("npm.client")
logger.setLevel(logging.DEBUG)

class npmClient(object) :
    def __init__(self, app = None, parent = None) :
        
#        if not self.WindowExists("npmService.exe") :
#            logger.info(">>> --------------------------- Service is not running")
#            instance = QtCore.QProcess()
#            instance.startDetached("\\\\server01\\shared\\SharedNpm\\service\\npmService.exe")
        
        self.socket = QtNetwork.QLocalSocket()  

        self.blockSize = 0   
        
        self.app    = app
        self.parent = parent
        self.requests = {}
        
        self.breakWait = False
        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.disconnectedFromServer)
        
        self.socket.connectToServer("npmClient")
        if not self.socket.waitForConnected(1000) :
            self.displayMessage("error", "Cannot connect to the server.")
            self.stop()

#    def WindowExists(self, process):
#        strComputer = "."
#        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
#        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
#        colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_Process WHERE Name = '%s'" % process)
#        if len(colItems) > 0 :
#            return True
#        else :
#            return False

    def isConnected(self):
        return self.socket.isValid()

    def stop(self) :
        if self.parent :
            if hasattr(self.parent, "cleaning"):
                self.parent.cleaning()
        self.requests = {}
        if self.socket.state() == QtNetwork.QLocalSocket.ConnectedState:
            self.socket.disconnectFromServer()
    
    def cleanRequests(self):
        self.requests = {}
    
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
        try :
            action = json.loads(action)
            if "command" in action :
                if action["command"] == "notice" :
                    self.displayMessage(action["style"], action["text"])
                    self.breakWait = True
                    return        
            requestid = action.get("requestid", None)
            
            if requestid :
                if requestid in self.requests :               
                    function = self.requests[requestid]["function"]
                    args     = self.requests[requestid]["args"]
                    function(action, *args)
        except :
            logger.error("cannot decode command")
            logger.error(action)
            
    def writeToServer(self, action, requestid, function, *args, **kw):
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
        self.requests[requestid] = dict(function=function, args = args)     

    def send(self, message, function, *args):
        #we create an id for this request.
        requestid = int(random.getrandbits(32))
        message["requestid"] = requestid 
        
        data = json.dumps(message)
        logger.info("Outgoing JSON Message: " + data)
        self.writeToServer(data, requestid, function, *args)
        return requestid

    def launchExe(self, app, *args):
        instance = QtCore.QProcess()
        instance.startDetached(app)        

    def askChoice(self, question, choices):
        if self.app :
            item, ok = QtGui.QInputDialog.getItem(self.app, "Selection from the server",
                    question, choices, 0, False)
            if ok and item:
                return item
            else:
                return None
        return None

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
        self.socket.disconnected.disconnect()
        now = time.time()
        while time.time() - now < 6 :
            QtCore.QCoreApplication.processEvents()
            self.socket.connectToServer("npmClient")
            if self.socket.waitForConnected(6000) :
                self.socket.disconnected.connect(self.disconnectedFromServer)
                break
            
        if not self.isConnected() :
            self.displayMessage("error", "Connection to the server lost and cannot (re-)connect.")
            self.stop()

            
            
