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





from PyQt4 import QtCore, QtGui

class Validator(QtCore.QObject):
    ''' 
    This class can be used by any module to create a validation info clip.
    This can be sur-classed to add infos to it, but this is the minimal infos required.
    '''
    def __init__(self, uid, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.uid        = uid
        self.client     = None
        self.clipUid    = None   
        self.userUid    = None
        self.taskUid    = None
        self.path       = None
        self.filename   = None
        self.date       = None   
        self.version    = 0
        self.state      = 0
        

    def infoMessage(self):
        return self.message

    def update(self, message, client):
        '''     
        Updates this item from the message dictionary supplied
        '''
        self.client     = client
        self.clipUid    = message['clipuid']  
        self.taskUid    = message['taskuid']
        self.path       = message['path']
        self.filename   = message['filename']
        self.version    = message['version']
        self.state      = message['state']
        date            = message['date']
        self.date       = QtCore.QDateTime.fromString(date, "yyyy-MM-dd hh:mm:ss")
        self.userUid    = message['useruid']
        self.message    = message
