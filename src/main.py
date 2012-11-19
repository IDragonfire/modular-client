
# CRUCIAL: This must remain on top.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QStringList', 2)
sip.setapi('QList', 2)
sip.setapi('QProcess', 2)

#Set up a robust logging system
import util
util.startLogging()


from PyQt4 import QtGui, QtCore, QtNetwork


import sys



excepthook_original = sys.excepthook
def excepthook(excType, excValue, tracebackobj): 
    '''
    This exception hook will stop the app if an uncaught error occurred, regardless where in the QApplication.
    '''
    logger.error("Uncaught exception", exc_info=(excType, excValue, tracebackobj))
    dialog = util.CrashDialog((excType, excValue, tracebackobj))
    answer = dialog.exec_()
        
    if (answer == QtGui.QDialog.Rejected):
        # Shut it down as nicely as possible.
        sys.excepthook = excepthook_original
        QtGui.QApplication.closeAllWindows()
        util.stopLogging()
        QtGui.QApplication.quit()
        sys.exit(1)


#Override our except hook.
sys.excepthook = excepthook


def runFAF():
    #Load theme from settings (one of the first things to be done)
    util.loadTheme()    
    
    #create client singleton and connect
    import client
        
    npm_client = client.instance

    #Connect and login, then load and show the UI if everything worked
    if npm_client.doConnect():
        if npm_client.waitSession() :
            npm_client.setup()
            if npm_client.doLogin():
                
                #Done setting things up, show the window to the user.
                if util.developer() : 
                    npm_client.show()                    
                
                #Main update loop    
                QtGui.QApplication.exec_()


class QtSingleApplication(QtGui.QApplication):

    messageReceived = QtCore.pyqtSignal(unicode)

    def __init__(self, id, *argv):

        super(QtSingleApplication, self).__init__(*argv)
        self._id = id
        self._activationWindow = None
        self._activateOnMessage = False

        # Is there another instance running?

        self._outSocket = QtNetwork.QLocalSocket()
        self._outSocket.connectToServer(self._id)
        self._isRunning = self._outSocket.waitForConnected()

        if self._isRunning:
            # Yes, there is.
            self._outStream = QtCore.QTextStream(self._outSocket)
            self._outStream.setCodec('UTF-8')
        else:
            # No, there isn't.
            self._outSocket = None
            self._outStream = None
            self._inSocket = None
            self._inStream = None
            self._server = QtNetwork.QLocalServer()
            self._server.listen(self._id)
            self._server.newConnection.connect(self._onNewConnection)

    def isRunning(self):
        return self._isRunning

    def id(self):
        return self._id

    def activationWindow(self):
        return self._activationWindow

    def setActivationWindow(self, activationWindow, activateOnMessage = True):
        self._activationWindow = activationWindow
        self._activateOnMessage = activateOnMessage

    def activateWindow(self):
        if not self._activationWindow:
            return
        self._activationWindow.setWindowState(
            self._activationWindow.windowState() & ~QtCore.Qt.WindowMinimized)
        self._activationWindow.raise_()
        self._activationWindow.activateWindow()

    def sendMessage(self, msg):
        if not self._outStream:
            return False
        self._outStream << msg << '\n'
        self._outStream.flush()
        return self._outSocket.waitForBytesWritten()

    def _onNewConnection(self):
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QtCore.QTextStream(self._inSocket)
        self._inStream.setCodec('UTF-8')
        self._inSocket.readyRead.connect(self._onReadyRead)
        if self._activateOnMessage:
            self.activateWindow()

    def _onReadyRead(self):
        while True:
            msg = self._inStream.readLine()
            if not msg: break
            self.messageReceived.emit(msg)
    
def WindowExists(process):
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_Process WHERE Name = '%s'" % process)

    if len(colItems) > 0 :
        return True
    else :
        return False

#Actual "main" method 
if __name__ == '__main__':      
    
    
    #Set up logging framework
    import logging
    logger = logging.getLogger("npm.main")
    logger.propagate = True
    
    #checking if nam service is running
    
    if not util.developer() :
        if not WindowExists("npmService.exe") :
            logger.info(">>> --------------------------- Service is not running")
            instance = QtCore.QProcess()
            instance.startDetached("\\\\server01\\shared\\SharedNpm\\service\\npmService.exe")
 
    #init application framework    
    
    appGuid = 'e0526851-f811-4596-9423-4aca9a830c27'
    
    if util.developer() :
        appGuid = "dev"
        
    app = QtSingleApplication(appGuid, sys.argv)
    if app.isRunning() :
        logger.info(">>> --------------------------- App is already running")
        sys.exit(0)
    
    logger.info(">>> --------------------------- Application Launch") 
    
    app.setWindowIcon(util.icon("window_icon.png", True))
    
    #Set application icon to nicely stack in the system task bar    
    import ctypes   
    if getattr(ctypes.windll.shell32, "SetCurrentProcessExplicitAppUserModelID", None) is not None: 
        myappid = 'com.npm.client'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

 
    runFAF()


    #End of show
    app.closeAllWindows()    
    app.quit()
    
    #End the application, perform some housekeeping
    logger.info("<<< --------------------------- Application Shutdown")    
    util.stopLogging()


    
    