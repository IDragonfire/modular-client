#-------------------------------------------------------------------------------
# Copyright (c) 2013 Gael Honorez.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#-------------------------------------------------------------------------------





from PyQt4 import QtCore, QtNetwork

import functools

import logging

FAF_PROXY_HOST = "direct.faforever.com"
FAF_PROXY_PORT = 9124

UNIT16 = 8

class proxies(QtCore.QObject):
    __logger = logging.getLogger("faf.fa.proxies")
    __logger.setLevel(logging.DEBUG)

    def __init__(self, parent=None):
        super(proxies, self).__init__(parent)

        self.client = parent

        self.proxies = {}
        self.proxiesDestination = {}
        port = 12000
        for i in range(11) :
            port = port + 1
            self.proxies[i] = QtNetwork.QUdpSocket(self)
            if not self.proxies[i].bind(QtNetwork.QHostAddress.LocalHost, port) :
                self.__logger.warn("Can't bind socket %i" % i)
            else :
                self.__logger.info("binding socket %i on port %i" % (i, self.proxies[i].localPort()))
                self.proxies[i].readyRead.connect(functools.partial(self.processPendingDatagrams, i))
                self.proxiesDestination[i] = None

        self.proxySocket = QtNetwork.QTcpSocket(self)
        self.proxySocket.connected.connect(self.connectedProxy)
        self.proxySocket.readyRead.connect(self.readData) 
        
        self.blockSize = 0
        self.uid = None
    
    def setUid(self, uid):
        self.uid = uid
    
    def connectedProxy(self):
        ''' Setting the socket option correctly'''
        # we want the low delay for performance.
        self.__logger.debug("Setting low delay on socket.")
        self.proxySocket.setSocketOption(QtNetwork.QAbstractSocket.LowDelayOption, 1)

    def connectToProxy(self):
        self.proxySocket.connectToHost(FAF_PROXY_HOST, FAF_PROXY_PORT)
        if self.proxySocket.waitForConnected(10000):
            self.__logger.info("Connected to proxy server " + self.proxySocket.peerName() + ":" + str(self.proxySocket.peerPort()))
        
        self.sendUid()
            
    def bindSocket(self, port, uid):
        self.proxiesDestination[port] = uid
        if not self.proxySocket.state() == QtNetwork.QAbstractSocket.ConnectedState :
            self.connectToProxy()
        return self.proxies[port].localPort()
        
    def releaseSocket(self, port):
        self.proxiesDestination[port] = None

    def tranfertToUdp(self, port, packet):
        self.proxies[port].writeDatagram(packet, QtNetwork.QHostAddress.LocalHost, self.client.gamePort)

    def readData(self):
        if self.proxySocket.isValid() :           
            if self.proxySocket.bytesAvailable() == 0 :
                return
            ins = QtCore.QDataStream(self.proxySocket)
            ins.setVersion(QtCore.QDataStream.Qt_4_2)
            while ins.atEnd() == False :                             
                if self.proxySocket.isValid() :
                    if self.blockSize == 0:
                        if self.proxySocket.isValid() :
                            if self.proxySocket.bytesAvailable() < 4:
                                return

                            self.blockSize = ins.readUInt32()
                        else :
                            return
        
                    if self.proxySocket.isValid() :
                        if self.proxySocket.bytesAvailable() < self.blockSize:
                            return

                    else :
                        return  
                    port = ins.readUInt16()
                    packet  = ins.readQVariant()
                    
                    self.tranfertToUdp(port, packet)
                    
                    self.blockSize = 0
      
                else : 
                    return    
            return                

    def sendUid(self, *args, **kwargs) :
        if self.uid:
            self.__logger.warn("sending our uid to the server")
            reply = QtCore.QByteArray()
            stream = QtCore.QDataStream(reply, QtCore.QIODevice.WriteOnly)
            stream.setVersion(QtCore.QDataStream.Qt_4_2)
            stream.writeUInt32(0)           
                
            stream.writeUInt16(self.uid)        
            stream.device().seek(0)
            
            stream.writeUInt32(reply.size() - 4)
    
            if self.proxySocket.write(reply) == -1 :
                self.__logger.warn("error writing to proxy server !")

    def sendReply(self, port, uid, packet, *args, **kwargs) :
        reply = QtCore.QByteArray()
        stream = QtCore.QDataStream(reply, QtCore.QIODevice.WriteOnly)
        stream.setVersion(QtCore.QDataStream.Qt_4_2)
        stream.writeUInt32(0)           
            
        stream.writeUInt16(port)
        stream.writeUInt16(uid)        
        stream.writeQVariant(packet)
        stream.device().seek(0)
        
        stream.writeUInt32(reply.size() - 4)

        if self.proxySocket.write(reply) == -1 :
            self.__logger.warn("error writing to proxy server !")

    def closeSocket(self):
        if self.proxySocket.state() == QtNetwork.QAbstractSocket.ConnectedState :
            self.__logger.info("disconnecting from proxy server")
            self.proxySocket.disconnectFromHost()
    
    def processPendingDatagrams(self, i):
        udpSocket = self.proxies[i]
        while udpSocket.hasPendingDatagrams():
            datagram, _, _ = udpSocket.readDatagram(udpSocket.pendingDatagramSize())
            self.sendReply(i, self.proxiesDestination[i], QtCore.QByteArray(datagram))

            