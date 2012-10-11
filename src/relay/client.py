import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QStringList', 2)
sip.setapi('QList', 2)
sip.setapi('QProcess', 2)

from PyQt4 import QtCore
from PyQt4 import QtNetwork
import util
import logging
import json

logger= logging.getLogger("npm.client")
logger.setLevel(logging.INFO)

class npmClient(object) :
    def __init__(self) :
        self.socket = QtNetwork.QTcpSocket()  
        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.disconnectedFromServer)
        self.blockSize = 0
        
        self.socket.connectToHost("localhost", 7001)    
      
      
    def stop(self) :
        if self.socket.state() == QtNetwork.QTcpSocket.ConnectedState:
            self.socket.disconnectFromHost()
    
        
        
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
        try:
            message = json.loads(action)
            if "debug" in message:
                logger.info(message['debug'])
            if "relay" in message:
                logger.info("message for a client" + str(message["relay"]))
                self.relayServer.dispatch(message["relay"], message)
            elif "command" in message:                
                cmd = "handle_" + message['command']
                if hasattr(self, cmd):
                    getattr(self, cmd)(message)
                else:                
                    logger.error("Unknown command for JSON." + message['command'])
                    raise "StandardError"
            else:
                logger.debug("No command in message.")                
        except:
            raise #Pass it on to our caller, Malformed Command

    def writeToServer(self, action, *args, **kw):
        '''
        This method is the workhorse of the client, and is used to send messages, queries and commands to the server.
        '''
        logger.debug("Client: " + action)
        
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
                logger.warn("Uninterpreted Data Type: " + str(type(arg)) + " sent as str: " + str(arg))
                out.writeQString(str(arg))

        out.device().seek(0)        
        out.writeUInt32(block.size() - 4)
        self.bytesToSend = block.size() - 4
    
        self.socket.write(block)

    def send(self, message, qfile = None):
        data = json.dumps(message)
        if qfile == None :
            logger.info("Outgoing JSON Message: " + data)
            self.writeToServer(data)
        else :
            logger.info("Outgoing JSON Message + file: " + data)
            self.writeToServer(data, qfile)



    def disconnectedFromServer(self) :
        pass