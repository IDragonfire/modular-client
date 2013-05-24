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





from PyQt4 import QtGui, QtCore
import util

class ProjectItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        QtGui.QStyledItemDelegate.__init__(self, *args, **kwargs)
        
    def paint(self, painter, option, index, *args, **kwargs):
        self.initStyleOption(option, index)

                
        painter.save()
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        
       
        option.text = ""  
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)
        
        #Description
        painter.translate(option.rect.left(), option.rect.top())
        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
        html.drawContents(painter, clip)
  
        painter.restore()
        

    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)
        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(Project.TEXTWIDTH)
        return QtCore.QSize(Project.TEXTWIDTH + Project.PADDING, Project.CLIPSIZE)  


class Project(QtGui.QListWidgetItem):

    '''
    A project is the representation of a project on the server.
    '''
    
    TEXTWIDTH = 230
    CLIPSIZE = 25
    PADDING = 5
    
    WIDTH = TEXTWIDTH
    
    FORMATTER_PROJECT = unicode(util.readfile("projects/formatters/project.qthtml"))    


    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        
        self.uid = uid
        self.client  = None
        self.name = None
        self.project3d = None
        self.projectComp = None
        self.selected = False
        
    
        
    def update(self, message, client):
        '''
        Updates this item from the message dictionary supplied
        '''
        
        self.client  = client
               
        if "selected" in message :
            self.selected       = message.get('selected', False) 
            if self.selected :          
                for project in self.client.projects.projects :
                    if project != self.uid : 
                        self.client.projects.projects[project].update(dict(selected=False), self.client)

                self.client.currentProject = self
            color = "silver"
            if self.selected :
                color = "yellow"
            self.setText(self.FORMATTER_PROJECT.format(color = color, name = self.name))
            return
 
        self.name           = message['name']
        self.project3d      = message['project3d']
        self.projectComp    = message['projectCompo']
        date                = message['date']      
        self.date = QtCore.QDateTime.fromString(date, "yyyy-MM-dd hh:mm:ss") 
        
        color = "silver"
        if self.selected :
            color = "yellow"
        self.setText(self.FORMATTER_PROJECT.format(color = color, name = self.name))
         
        tooltipstring = ("3d folder : %s<br/>Compo folder : %s " % (self.project3d, self.projectComp))
        self.setToolTip(tooltipstring)
        
       
        
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;

        
        # Default: Alphabetical
        return self.date < other.date
