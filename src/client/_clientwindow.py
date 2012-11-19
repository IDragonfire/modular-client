'''
Created on Dec 1, 2011

@author: thygrrr
'''

from PyQt4 import QtCore, QtGui, QtNetwork
from types import IntType, FloatType, ListType, DictType

from client import logger, ClientState, WEBSITE_URL, WIKI_URL,\
     SUPPORT_URL, TICKET_URL, LOBBY_HOST,\
    LOBBY_PORT

import util
import relay

import json
import sys
import time
import os

from validations.validator import Validator

class ClientOutdated(StandardError):
    pass


FormClass, BaseClass = util.loadUiType("client/client.ui")

class ClientWindow(FormClass, BaseClass):
    '''
    This is the main lobby client that manages the server related connection and data,
    in particular projects, edits, users, etc.
    Its UI also houses all the other UIs for the sub-modules.
    '''
    #These signals are emitted when the client is connected or disconnected from FAF
    connected    = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()
    
    #This signal is emitted when the client is done rezising
    doneresize   = QtCore.pyqtSignal()
        
    #These signals propagate important client state changes to other modules
    userUpdated             = QtCore.pyqtSignal(dict)
    projectsUpdated         = QtCore.pyqtSignal(dict)
    editsUpdated            = QtCore.pyqtSignal(dict)
    clipUpdated             = QtCore.pyqtSignal(dict)
    validatorUpdated        = QtCore.pyqtSignal(dict)
    pipelineStepUpdated     = QtCore.pyqtSignal(dict)
    commentUpdated          = QtCore.pyqtSignal(dict)
    stepUpdated             = QtCore.pyqtSignal(dict)
    taskUpdated             = QtCore.pyqtSignal(dict)
    
    validatorObjUpdated     = QtCore.pyqtSignal(Validator)
    
    powerUpdated            = QtCore.pyqtSignal()
    makeIconUpdated         = QtCore.pyqtSignal(str, QtGui.QImage, list)

    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)        
        
        logger.debug("Client instantiating")
        
        #Can we really close this ?
        self.canClose = False
        
        
        self.threads = []
        
        # Hook to Qt's application management system
        QtGui.QApplication.instance().aboutToQuit.connect(self.cleanup)
               
        #Init and wire the TCP Network socket to communicate with faforever.com
        self.socket = QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.disconnectedFromServer)
        self.socket.error.connect(self.socketError)
        self.blockSize = 0

        self.sendFile = False
        self.progress = QtGui.QProgressDialog()
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)
        
        #connect the utility to load image from threads
        self.makeIconUpdated.connect(self.makeIcon)
        
        #Tray icon
        self.tray = QtGui.QSystemTrayIcon(self)
        self.tray.setToolTip("Nozon Project Manager")
        self.tray.setIcon(util.icon("client/tray_icon.png"))
        self.tray.activated.connect(self.trayEvent)
        self.tray.show()
        
        
        #tray menu
        self.traymenu = QtGui.QMenu(self)
        showLobby = QtGui.QAction("Control", self.traymenu)
        showLobby.triggered.connect(self.showLobby)       
        closeClient = QtGui.QAction("Close client", self.traymenu)
        closeClient.triggered.connect(self.closeClient)

        
        self.traymenu.addAction(showLobby)
        self.traymenu.addSeparator()
        self.traymenu.addAction(closeClient)

        self.tray.setContextMenu(self.traymenu)
        
        
        self.state = ClientState.NONE
        self.session = None

        #Timer for resize events
#        self.resizeTimer = QtCore.QTimer(self)
#        self.resizeTimer.timeout.connect(self.resized)
#        self.preferedSize = 0
                      
        #Local Relay Server
        self.relayServer = relay.relayserver.RelayServer(self)
        
        #create user interface (main window) and load theme
        self.setupUi(self)
        self.setStyleSheet(util.readstylesheet("client/client.css"))
        self.setWindowTitle("Nozon Project Manager " + util.VERSION_STRING)

        #Wire all important signals
        self.mainTabs.currentChanged.connect(self.mainTabChanged)
        self.powerUpdated.connect(self.powerUpdate)
        
        #Verrry important step!
        self.loadSettings()            

        self.currentProject = None
        self.urls = {}          # user game location URLs - TODO: Should go in self.players
        
        
        self.friends = []       # names of the client's friends
                
        self.power = 0          # current user power        
        
        #Initialize the Menu Bar according to settings etc.
        self.initMenus()

        #Load the icons for the tabs
        self.mainTabs.setTabIcon(self.mainTabs.indexOf(self.projectsTab), util.icon("client/category.png"))
        self.mainTabs.setTabIcon(self.mainTabs.indexOf(self.editsTab), util.icon("client/showreel.png"))
        self.mainTabs.setTabIcon(self.mainTabs.indexOf(self.validationsTab), util.icon("client/order-162.png"))
        self.mainTabs.setTabIcon(self.mainTabs.indexOf(self.storyboardTab), util.icon("client/print.png"))
        self.mainTabs.setTabIcon(self.mainTabs.indexOf(self.usersTab), util.icon("client/customers.png"))       
        #self.mainTabs.setTabEnabled(self.mainTabs.indexOf(self.tourneyTab), False)


    def powerUpdate(self):
        '''Triggered when the user got new power'''
        if self.power >= 32 :
            self.actionRestartAllClients.setEnabled(1)
        else :
            self.actionRestartAllClients.setEnabled(1)

    def makeIcon(self, filename, image, widgetlist):
        util.makeIcon(filename, image, widgetlist)

    def trayEvent(self, reason):
        if reason == 2 :
            self.showLobby()

    def showLobby(self):
        self.show()   

    def closeClient(self):
        self.canClose = True
        self.close()

                
    def setup(self):
        ''' Here, we are importing all the differents modules that the client can use.
        A module can have his own interface (like clips, storyboard...), 
        or be a container for datas coming from the servers (like comments, scenes3d, ...)
        '''
        import projects
        import edits
        import storyboard
        import users
        import comments
        import clips
        import pipeline
        import validations
        
        self.clips          = clips.Clips(self)
        self.pipeline       = pipeline.Pipeline(self)
        self.comments       = comments.Comments(self)
        self.projects       = projects.Projects(self)
        self.edits          = edits.Edits(self)
        self.storyboard     = storyboard.Storyboard(self)
        self.users          = users.Users(self)
        self.validations    = validations.Validations(self)
        
        

    @QtCore.pyqtSlot()
    def cleanup(self):
        '''
        Perform cleanup before the UI closes
        '''        
        self.state = ClientState.SHUTDOWN

        self.progress.setWindowTitle("NPM is shutting down")
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)
        self.progress.setValue(0)
        self.progress.setCancelButton(None)
        self.progress.show()
                

        #Terminate Lobby Server connection
        if self.socket.state() == QtNetwork.QTcpSocket.ConnectedState:
            self.progress.setLabelText("Closing main connection.")
            self.socket.disconnectFromHost()
            

        #Terminate local ReplayServer
        if self.relayServer:
            self.progress.setLabelText("Terminating local relay server")
            self.relayServer.close()
            self.relayServer = None
        
#        #Clean up Chat
#        if self.chat:
#            self.progress.setLabelText("Disconnecting from IRC")
#            self.chat.disconnect()
#            self.chat = None
        
        # Get rid of the Tray icon        
        if self.tray:
            self.progress.setLabelText("Removing System Tray icon")
            self.tray.deleteLater()
            self.tray = None
                    
        #Terminate UI
        if self.isVisible():
            self.progress.setLabelText("Closing main window")
            self.close()

        self.progress.close()
        
        

    def closeEvent(self, event):
        logger.info("Close Event for Application Main Window")
        if self.canClose == False :
            self.hide()
            event.ignore()
            return
  
        self.saveWindow()
        return QtGui.QMainWindow.closeEvent(self, event)
        

#    def resizeEvent(self, size):
#        self.resizeTimer.start(400)
#        
#    def resized(self):
#        self.resizeTimer.stop()
#        self.doneresize.emit()
     
    def initMenus(self):
                
        self.actionRestartAllClients.triggered.connect(self.restartClients)
        self.actionRestartAllClients.setEnabled(0)
        
        self.actionLinkWebsite.triggered.connect(self.linkWebsite)
        self.actionLinkWiki.triggered.connect(self.linkWiki)

        self.actionWiki.triggered.connect(self.linkWiki)
        self.actionReportBug.triggered.connect(self.linkReportBug)
        self.actionShowLogs.triggered.connect(self.linkShowLogs)
        self.actionTechSupport.triggered.connect(self.linkTechSupport)
        self.actionAbout.triggered.connect(self.linkAbout)
        
        
        self.actionClearCache.triggered.connect(self.clearCache)        
        self.actionClearSettings.triggered.connect(self.clearSettings)        
        self.actionClearGameFiles.triggered.connect(self.clearGameFiles)

        #Toggle-Options
        self.actionSetAutoLogin.triggered.connect(self.updateOptions)
        self.actionSetSoundEffects.triggered.connect(self.updateOptions)
        
        
        #Init themes as actions.
        themes = util.listThemes()
        for theme in themes:
            action = self.menuTheme.addAction(str(theme))
            action.triggered.connect(self.switchTheme)
            action.theme = theme
            action.setCheckable(True)            
            
            if util.getTheme() == theme:
                action.setChecked(True)
        
        # Nice helper for the developers
        self.menuTheme.addSeparator()
        self.menuTheme.addAction("Reload Stylesheet", lambda: self.setStyleSheet(util.readstylesheet("client/client.css")))
        
        
    @QtCore.pyqtSlot()
    def restartClients(self):
        self.send(dict(command="admin", action="restart_all"))
        
    @QtCore.pyqtSlot()
    def updateOptions(self):
        self.autologin = self.actionSetAutoLogin.isChecked()
        self.soundeffects = self.actionSetSoundEffects.isChecked()
        self.opengames = self.actionSetOpenGames.isChecked()
        self.joinsparts = self.actionSetJoinsParts.isChecked()
        self.livereplays = self.actionSetLiveReplays.isChecked()
        self.gamelogs = self.actionSaveGamelogs.isChecked()
                 
        self.saveChat()
        self.saveCredentials()
        pass
    
    
    @QtCore.pyqtSlot()
    def switchTheme(self):
        util.setTheme(self.sender().theme, True)

       
    @QtCore.pyqtSlot()
    def clearSettings(self):
        result = QtGui.QMessageBox.question(None, "Clear Settings", "Are you sure you wish to clear all settings, login info, etc. used by this program?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if (result == QtGui.QMessageBox.Yes):
                        
            util.settings.clear()
            util.settings.sync()
            QtGui.QMessageBox.information(None, "Restart Needed", "FAF will quit now.")
            QtGui.QApplication.quit()

    @QtCore.pyqtSlot()
    def clearGameFiles(self):
        util.clearDirectory(util.BIN_DIR)
        util.clearDirectory(util.GAMEDATA_DIR)   
    
    @QtCore.pyqtSlot()
    def clearCache(self):
        changed = util.clearDirectory(util.CACHE_DIR)
        if changed:
            QtGui.QMessageBox.information(None, "Restart Needed", "FAF will quit now.")
            QtGui.QApplication.quit()
        
    

    @QtCore.pyqtSlot()
    def linkWebsite(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(WEBSITE_URL))

    @QtCore.pyqtSlot()
    def linkWiki(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(WIKI_URL))

    @QtCore.pyqtSlot()
    def linkReportBug(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(TICKET_URL))
        #from util.report import ReportDialog
        #ReportDialog(self).show()

    @QtCore.pyqtSlot()
    def linkTechSupport(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(SUPPORT_URL))

    @QtCore.pyqtSlot()
    def linkShowLogs(self):
        util.showInExplorer(util.LOG_DIR)
        
    @QtCore.pyqtSlot()
    def linkAbout(self):
        dialog = util.loadUi("client/about.ui")
        dialog.exec_()

    def getUserName(self, uid):
        user = "Unknown"
        if uid in self.users.users :
            user = self.users.users[uid].login      
        return user
        
    def getUserUid(self):
        for uid in self.users.users :
            if self.users.users[uid].login == self.login :
                return uid

       
    def saveCredentials(self):
        util.settings.beginGroup("user")
        util.settings.setValue("user/remember", self.remember) #always remember to remember
        if self.remember:            
            util.settings.setValue("user/login", self.login)
            util.settings.setValue("user/password", self.password)
            util.settings.setValue("user/autologin", self.autologin) #only autologin if remembering 
        else:
            util.settings.setValue("user/login", None)
            util.settings.setValue("user/password", None)
            util.settings.setValue("user/autologin", False)
        util.settings.endGroup()
        util.settings.sync()

    def clearAutologin(self):
        self.autologin = False
        self.actionSetAutoLogin.setChecked(False)
        
        util.settings.beginGroup("user")
        util.settings.setValue("user/autologin", False)
        util.settings.endGroup()
        util.settings.sync()
        
    def saveWindow(self):
        util.settings.beginGroup("window")
        util.settings.setValue("geometry", self.saveGeometry())
        util.settings.endGroup()        
        util.settings.sync()
                
    @QtCore.pyqtSlot()
    def saveChat(self):        
        util.settings.beginGroup("chat")
        util.settings.setValue("soundeffects", self.soundeffects)
        util.settings.setValue("livereplays", self.livereplays)
        util.settings.setValue("opengames", self.opengames)
        util.settings.setValue("joinsparts", self.joinsparts)
        util.settings.endGroup()
        
        
    def loadSettings(self):
        util.settings.beginGroup("window")
        geometry =  util.settings.value("geometry", None)
        if geometry:
            self.restoreGeometry(geometry)
        util.settings.endGroup()        
                
        util.settings.beginGroup("user")
        self.login = util.settings.value("user/login")
        self.password = util.settings.value("user/password")
        self.remember = (util.settings.value("user/remember") == "true")
        
        # This is the new way we do things.
        self.autologin = (util.settings.value("user/autologin") == "true")
        self.actionSetAutoLogin.setChecked(self.autologin)        
        util.settings.endGroup()
        
        #self.loadChat()
        
        
    def loadChat(self):        
        try:
            util.settings.beginGroup("chat")        
            self.soundeffects = (util.settings.value("soundeffects", "true") == "true")
            self.opengames = (util.settings.value("opengames", "true") == "true")
            self.joinsparts = (util.settings.value("joinsparts", "false") == "true")
            self.livereplays = (util.settings.value("livereplays", "true") == "true")
            util.settings.endGroup()

            self.actionSetSoundEffects.setChecked(self.soundeffects)
            self.actionSetLiveReplays.setChecked(self.livereplays)
            self.actionSetOpenGames.setChecked(self.opengames)
            self.actionSetJoinsParts.setChecked(self.joinsparts)
        except:
            pass
        
          
    def doConnect(self, reconnect=False):  
        if not self.relayServer.doListen():
            return False

        self.progress.setCancelButtonText("Cancel")
        self.progress.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        self.progress.setAutoClose(False)
        self.progress.setAutoReset(False)
        self.progress.setModal(1)
        if reconnect == False :
            self.progress.setWindowTitle("Connecting...")
            self.progress.setLabelText("Establishing connection ...")
        else :
            self.progress.setWindowTitle("Connection to server lost...")
            self.progress.setLabelText("Re-establishing connection ...")           
        self.progress.show()                

        # Begin connecting.        
        self.socket.setSocketOption(QtNetwork.QTcpSocket.KeepAliveOption, 1)
        self.socket.connectToHost(LOBBY_HOST, LOBBY_PORT)

        while (self.socket.state() != QtNetwork.QAbstractSocket.ConnectedState) and self.progress.isVisible():
            QtGui.QApplication.processEvents()                                        
            if self.socket.state() ==  QtNetwork.QAbstractSocket.UnconnectedState :
                self.socket.connectToHost(LOBBY_HOST, LOBBY_PORT)
                

        self.state = ClientState.NONE    
        self.localIP = str(self.socket.localAddress().toString())

#        #Perform Version Check first        
        if not self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.progress.close() # in case it was still showing...
            # We either cancelled or had a TCP error, meaning the connection failed..
            if self.progress.wasCanceled():
                logger.warn("doConnect() aborted by user.")
            else:
                logger.error("doConnect() failed with clientstate " + str(self.state) + ", socket errorstring: " + self.socket.errorString())
            return False
        else:     
  
            return True       

    def waitSession(self):
        self.send(dict(command="ask_session"))
        while self.session == None :
            QtGui.QApplication.processEvents()  
        return True  
        
    def doLogin(self):
        #Determine if a login wizard needs to be displayed and do so
        if not self.autologin or not self.password or not self.login:        
            import loginwizards
            if not loginwizards.LoginWizard(self).exec_():
                return False;
        
        self.progress.setLabelText("Logging in...")
        self.progress.reset()
        self.progress.show()                       
         
      
        logger.info("Attempting to login as: " + str(self.login))
        self.state = ClientState.NONE

        self.send(dict(command="hello", version=util.VERSION, login=self.login, password = self.password, local_ip = self.localIP))
        
        while (not self.state) and self.progress.isVisible():
            QtGui.QApplication.processEvents()
            

        if self.progress.wasCanceled():
            logger.warn("Login aborted by user.")
            return False
        
        self.progress.close()

        if self.state == ClientState.OUTDATED :
                logger.warn("Client is OUTDATED.")

        elif self.state == ClientState.ACCEPTED:
            logger.info("Login accepted.")
            util.report.BUGREPORT_USER = self.login
            util.crash.CRASHREPORT_USER = self.login

            #success: save login data (if requested) and carry on
            self.actionSetAutoLogin.setChecked(self.autologin)
            self.updateOptions()

            self.progress.close()

            #This is a triumph... I'm making a note here: Huge success!
            self.connected.emit()
            self.projects.loggedInSetup()
            return True            
        elif self.state == ClientState.REJECTED:
            logger.warning("Login rejected.")
            self.clearAutologin()
            return self.doLogin()   #Just try to login again, slightly hackish but I can get away with it here, I guess.
        else:
            # A more profound error has occurrect (cancellation or disconnection)
            return False




    def loginCreation(self, result):
        '''
        Simply acknowledges the answer the server gave to our account creation attempt,
        and sets the client's state accordingly so the Account Creation Wizard
        can continue its work.
        '''
        logger.debug("Account name free and valid: " + result)

        if result == "yes" :
            self.state = ClientState.CREATED
        else:
            self.state = ClientState.REJECTED
    #Color table used by the following method
    # CAVEAT: This will break if the theme is loaded after the client package is imported
    colors = json.loads(util.readfile("client/colors.json"))

    @QtCore.pyqtSlot(int)
    def mainTabChanged(self, index):
        '''
        The main visible tab (module) of the client's UI has changed.
        In this case, other modules may want to load some data or cease
        particularly CPU-intensive interactive functionality.
        LATER: This can be rewritten as a simple Signal that each module can then individually connect to.
        '''
        new_tab = self.mainTabs.widget(index)

    def loginWriteToFaServer(self, action, *args, **kw):
        '''
        This is a specific method that handles sending Login-related and update-related messages to the server.
        '''        
        self.state = ClientState.NONE
        
        logger.debug("Login Write: " + action)
        
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
            else:
                logger.warn("Uninterpreted Data Type: " + str(type(arg)) + " of value: " + str(arg))
                out.writeQString(str(arg))
        
        out.device().seek(0)
        out.writeUInt32(block.size() - 4)
        self.socket.write(block)   
        QtGui.QApplication.processEvents()

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
        out.writeQString(self.login)
        out.writeQString(self.session)        
        
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

    @QtCore.pyqtSlot()
    def readFromServer(self):
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
            self.process(action, ins)
            self.blockSize = 0
                                
    @QtCore.pyqtSlot()
    def disconnectedFromServer(self):
        logger.warn("Disconnected from lobby server.")
        
        if self.state == ClientState.ACCEPTED:
            #QtGui.QMessageBox.warning(QtGui.QApplication.activeWindow(), "Disconnected from the server", "The client lost the connection to the server.<br/>Try reconnecting a little later!</b>", QtGui.QMessageBox.Close)
            self.state = ClientState.DROPPED
            #while self.socket.state() != QtNetwork.QAbstractSocket.ConnectedState :
            logger.warn("Reconnecting.")
            #QtCore.QCoreApplication.processEvents()
            if self.doConnect(reconnect=True):
                if self.waitSession() :
                    self.doLogin()

    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketError)
    def socketError(self, error):
        logger.error("TCP Socket Error: " + self.socket.errorString())
        #if self.state > ClientState.NONE:   # Positive client states deserve user notification.
            #QtGui.QMessageBox.critical(None, "TCP Error", "A TCP Connection Error has occurred:<br/><br/><b>" + self.socket.errorString()+"</b>", QtGui.QMessageBox.Close)        
                    
    def process(self, action, stream):
        logger.debug("Server: " + action)

        if action == "PING":
            self.writeToServer("PONG")
    
        elif action == "LOGIN_AVAILABLE" :
            result = stream.readQString()
            name = stream.readQString()
            logger.info("LOGIN_AVAILABLE: " + name + " - " + result)
            self.loginCreation(result)
        
        elif action == 'ACK' :
            bytesWritten = stream.readQString()
            logger.debug("Acknowledged %s bytes" % bytesWritten)
            
            if self.sendFile == True :
                self.progress.setValue(int(bytesWritten)* 100 / self.bytesToSend)
                if int(bytesWritten) >= self.bytesToSend :
                    self.progress.close()
                    self.sendFile = False                    

        elif action == 'ERROR' :
            message = stream.readQString()
            data = stream.readQString()
            logger.error("Protocol Error, server says: " + message + " - " + data)


        elif action == "MESSAGE":
            stream.readQString()
            stream.readQString()
            pass
    
        else:
            try:
                self.dispatch(json.loads(action))
            except:
                logger.error("Error dispatching JSON: " + action, exc_info=sys.exc_info())


    def dispatchToClient(self, message):
        if message["action"] == "get_user" :
            result = self.getUserName(message["useruid"])
            self.relayServer.dispatch(message["relay"], dict(requestid=message["requestid"], command="client", action = message["action"], username = result))
            
    # 
    # JSON Protocol v3 Implementation below here
    #
    def send(self, message, qfile = None):
        
        command = message.get('command', '')
        if command == "client" :
            self.dispatchToClient(message)
            return
        
        data = json.dumps(message)
        if qfile == None :
            logger.info("Outgoing JSON Message: " + data)
            self.writeToServer(data)
        else :
            logger.info("Outgoing JSON Message + file: " + data)
            self.writeToServer(data, qfile)
        
    def dispatch(self, message):
        '''
        A fairly pythonic way to process received strings as JSON messages.
        '''
        try:
            if "debug" in message:
                logger.info(message['debug'])
            if "relay" in message:
                logger.info("message for a client : " + str(message["relay"]))
                self.relayServer.dispatch(message["relay"], message)
            elif "command" in message:                
                cmd = "handle_" + message['command']
                if hasattr(self, cmd):
                    getattr(self, cmd)(message)
                else:                
                    logger.error("Unknown command for JSON." + message['command'])
                    raise StandardError 
            else:
                logger.debug("No command in message.")                
        except:
            raise #Pass it on to our caller, Malformed Command
      
    def handle_welcome(self, message):
        
        if "session" in message :
            self.session = str(message["session"])
        
        if "update" in message : 
            
            if not util.developer():
                logger.warn("Server says that Updating is needed.")
                self.progress.close()
                self.state = ClientState.OUTDATED
            else:
                logger.debug("Skipping update because this is a developer version.")
                logger.debug("Login success" )
                self.state = ClientState.ACCEPTED
                
        else :
            logger.debug("Login success" )
            self.state = ClientState.ACCEPTED
            
    
    def handle_social(self, message):
        if "power" in message:
            self.power = message["power"]
            self.powerUpdated.emit()

    def handle_user_info(self, message):
        self.userUpdated.emit(message)
    
    def handle_clip_info(self, message):
        self.clipUpdated.emit(message)    
    
    def handle_projects_info(self, message): 
        self.projectsUpdated.emit(message)            
     
    def handle_edits_info(self, message):
        self.editsUpdated.emit(message)
     
    def handle_comment_info(self, message):
        self.commentUpdated.emit(message) 
    
    def handle_validator_info(self, message):
        self.validatorUpdated.emit(message)

    def handle_pipeline_step_info(self, message):
        self.pipelineStepUpdated.emit(message)

    def handle_step_info(self, message):
        self.stepUpdated.emit(message)

    def handle_task_info(self, message):
        self.taskUpdated.emit(message)
     
    def handle_notice(self, message):
        if "text" in message:
            if message["style"] == "error" :
                if self.state != ClientState.NONE :
                    QtGui.QMessageBox.critical(self, "Error from Server", message["text"])
                else :
                    QtGui.QMessageBox.critical(self, "Login Failed", message["text"])
                    self.state = ClientState.REJECTED
    
            elif message["style"] == "warning":
                QtGui.QMessageBox.warning(self, "Warning from Server", message["text"])
           
            else:
                QtGui.QMessageBox.information(self, "Notice from Server", message["text"])

        if message["style"] == "restart":
            logger.info("Server is asking for client restart.")
            QtGui.QApplication.quit()
