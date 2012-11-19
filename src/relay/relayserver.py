from PyQt4 import QtCore, QtNetwork, QtGui


from types import IntType, FloatType, ListType, DictType
import os
import logging
import util
import time
import json
import random



class Relayer(QtCore.QObject): 
    '''
    This is a simple class that takes all the FA data input from its socket 
    and relays it to an internet server via its relaySocket.
    '''
    __logger = logging.getLogger("npm.npm.relayer")
    __logger.setLevel(logging.DEBUG)
    
    def __init__(self, parent, client, local_socket, session, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        
        self.parent = parent
        self.socket = local_socket
        self.client = client

        self.blockSize = 0
        self.relay = session

        self.socket.readyRead.connect(self.readDatas)
        self.socket.disconnected.connect(self.inputDisconnected)
        self.__logger.info("client connected locally.")  

        
    def __del__(self):
        #Find out whether this really does what it should (according to docs, sockets should be manually deleted to conserver resources)
        self.socket.deleteLater()
        self.__logger.debug("destructor called")        

    def readDatas(self):
        ins = QtCore.QDataStream(self.socket)        
        ins.setVersion(QtCore.QDataStream.Qt_4_2)
        
        while ins.atEnd() == False :
            if self.blockSize == 0:
                if self.socket.bytesAvailable() < 4:
                    return
                self.blockSize = ins.readUInt32()            
            if self.socket.bytesAvailable() < self.blockSize:
                return
            
            action = json.loads(ins.readQString())           
            action["relay"] = self.relay
            self.client.send(action)

            self.blockSize = 0
    
    def dispatch(self, message):
        data = json.dumps(message)
        self.__logger.info("Outgoing JSON Message: " + data)
        self.writeToClient(data)
            
    # 
    # JSON Protocol v2 Implementation below here
    #
    def send(self, message):
        
        data = json.dumps(message)
        self.__logger.info("Outgoing JSON Message: " + data)
        self.writeToClient(data)

    def writeToClient(self, action, *args, **kw):
        '''
        This method is the workhorse of the client, and is used to send messages, queries and commands to the server.
        '''
        self.__logger.debug("Client: " + action)
        
        block = QtCore.QByteArray()
        out = QtCore.QDataStream(block, QtCore.QIODevice.ReadWrite)
        out.setVersion(QtCore.QDataStream.Qt_4_2)

        out.writeUInt32(0)
        out.writeQString(action)     
        
        for arg in args :
            if type(arg) is IntType:
                out.writeInt(arg)
            elif isinstance(arg, basestring):
                out.writeQString(arg)
            elif type(arg) is FloatType:
                out.writeFloat(arg)
            elif type(arg) is ListType:
                out.writeQVariantList(arg)
            elif type(arg) is DictType:
                out.writeQString(json.dumps(arg))                                
            elif type(arg) is QtCore.QFile :       
                arg.open(QtCore.QIODevice.ReadOnly)
                fileDatas = QtCore.QByteArray(arg.readAll())
                #seems that that logger doesn't work
                #logger.debug("file size ", int(fileDatas.size()))
                out.writeInt(fileDatas.size())
                out.writeRawData(fileDatas)

                # This may take a while. We display the progress bar so the user get a feedback
                self.sendFile = True
                self.progress.setLabelText("Sending file to server")
                self.progress.setCancelButton(None)
                self.progress.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
                self.progress.setAutoClose(True)
                self.progress.setMinimum(0)
                self.progress.setMaximum(100)
                self.progress.setModal(1)
                self.progress.setWindowTitle("Uploading in progress")
 
                self.progress.show()
                arg.close()
            else:
                self.__logger.warn("Uninterpreted Data Type: " + str(type(arg)) + " sent as str: " + str(arg))
                out.writeQString(str(arg))

        out.device().seek(0)        
        out.writeUInt32(block.size() - 4)
        self.bytesToSend = block.size() - 4
    
        self.socket.write(block)

    def done(self):
        self.__logger.info("remove relay")
        self.parent.removeRelay(self.relay)


    @QtCore.pyqtSlot()
    def inputDisconnected(self):
        self.__logger.info("NPM client disconnected locally.")      
        self.done()



class RelayServer(QtNetwork.QLocalServer):
    ''' 
    This is a local listening server that NPM can send its data to.    
    '''
    __logger = logging.getLogger("npm.relay.relayserver")
    __logger.setLevel(logging.DEBUG)

    def __init__(self, client, *args, **kwargs):
        QtNetwork.QLocalServer.__init__(self, *args, **kwargs)
        self.relayers = {}
        self.client = client
      
        self.__logger.debug("initializing...")
        self.newConnection.connect(self.acceptConnection)
        
        
    def doListen(self):
        while not self.isListening():
            self.listen("npmClient")
            if (self.isListening()):
                self.__logger.info("relay listening on name " + self.serverName())
            else:
                self.__logger.error("cannot listen, port probably used by another application ")
                answer = QtGui.QMessageBox.warning(None, "Port Occupied", "Couldn't start its local server, which is needed for third party apps.", QtGui.QMessageBox.Retry, QtGui.QMessageBox.Abort)
                if answer == QtGui.QMessageBox.Abort:
                    return False
        return True
              
    def removeRelay(self, relay):
        if relay in self.relayers: 
            del self.relayers[relay]
            
    def dispatch(self, relay, message):
        if relay in self.relayers :
            self.relayers[relay].dispatch(message)
        else :
            self.__logger.warn("The client is not found ! " + str(relay))

    @QtCore.pyqtSlot()       
    def acceptConnection(self):
        socket = self.nextPendingConnection()
        self.__logger.debug("incoming connection to relay server...")
        session = int(random.getrandbits(32))
        if not session in self.relayers : 
            self.relayers[session] = Relayer(self, self.client, socket, session)
        pass

