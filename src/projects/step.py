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

class Step(QtGui.QListWidgetItem):
    '''
    A Step in the project.
    '''
    TEXTWIDTH = 150
    CLIPSIZE = 25
    PADDING = 5
    WIDTH = TEXTWIDTH
    
    FORMATTER_CLIP = unicode(util.readfile("edits/formatters/clip.qthtml"))
    
    def __init__(self, step, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)    
        
        self.step = step
        self.client = self.step.client
        self.tasks = {}

    def update(self):
        '''     
        Updates this item
        '''
        self.updateText()
   
    def stepPressed(self):
        '''
        A step was clicked
        '''
        menu = QtGui.QMenu(self.client)
        actionTask = QtGui.QAction("Add task", menu)
    
        if self.client.power <= 16 :
            actionTask.setDisabled(True)
        
        # Triggers
        actionTask.triggered.connect(self.addTask)
    
        menu.addAction(actionTask)
        menu.popup(QtGui.QCursor.pos())
        
    def addingTask(self, task):
        if not task.uid in self.tasks :
            self.tasks[task.uid] = task
        self.updateText()

    def updateText(self):
        uid = self.step.uid
        name = self.client.pipeline.getName(uid)   
           
        text = str(self.step.index) + ". " + name
        print name, text
        if len (self.tasks) > 0 :
            text += "\nTasks :\n"
            for uid in self.tasks :
                text += self.tasks[uid].name + "\n" 
        self.setText(text)
         
    def addTask(self):
        '''
        Adding a task to a step.
        '''
        text, ok = QtGui.QInputDialog.getText(self.client, "Adding a new task",
                "Task:", QtGui.QLineEdit.Normal,
                "")
        if ok and text != '':
            self.client.send(dict(command="pipeline", action="add_task", uid = self.step.uid, name = text))
    
    def __ge__(self, other):
        ''' 
        Comparison operator used for item list sorting 
        '''        
        return not self.__lt__(other)
    
    def __lt__(self, other):
        ''' 
        Comparison operator used for item list sorting 
        '''        
        if not self.client: return True # If not initialized...
        if not other.client: return False;

        # Default: Alphabetical
        return self.step.index < other.step.index
