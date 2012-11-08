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

    def update(self):
        '''     
        Updates this item
        '''
        
        uid = self.step.uid
        name = self.client.pipeline.pipeline_steps[uid].name

        self.setText(str(self.step.index) + " " + name)
        #self.setText(self.FORMATTER_CLIP.format(index = step.index, name = name))
    
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