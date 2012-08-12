from PyQt4 import QtGui
import util
import client


# These mods are always on top

mods = {}

mod_crucial = ["faf"]

# These mods are not shown in the game list
mod_invisible = []

mod_favourites = []  # LATER: Make these saveable and load them from settings

class ModItem(QtGui.QListWidgetItem):
    def __init__(self, message, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)

        self.mod  = message["name"]
        self.name = message["fullname"]
        self.options = message["options"]
        #Load Icon and Tooltip

        tip = message["desc"]      
        self.setToolTip(tip)
        
        if message["icon"] == None :
            icon = util.icon("games/mods/faf.png")        
            self.setIcon(icon)
        else :
            # TODO : download the icon from the remote path.
            pass
        
        
        if  self.mod in mod_crucial:
            color = client.instance.getColor("self")
        else:
            color = client.instance.getColor("player")
            
        self.setTextColor(QtGui.QColor(color))
        self.setText(self.name)


    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        
        # Crucial Mods are on top
        if (self.mod in mod_crucial) and not (other.mod in mod_crucial): return True
        if not (self.mod in mod_crucial) and (other.mod in mod_crucial): return False
        
        # Favourites are also ranked up top
        if (self.mod in mod_favourites) and not (other.mod in mod_favourites): return True
        if not(self.mod in mod_favourites) and (other.mod in mod_favourites): return False
        
        # Default: Alphabetical
        return self.name.lower() < other.mod.lower()
    



