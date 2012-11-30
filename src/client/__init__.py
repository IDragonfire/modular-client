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





# Initialize logging system
import logging
import util
logger = logging.getLogger("npm.client")
#logger.setLevel(logging.DEBUG)

VERSION        = 0
VERSION_STRING = "development"

#Load build number from version file.
if not util.developer():        
    VERSION_STRING = open("version").read()
    VERSION = int(VERSION_STRING.rsplit('.', 1)[1])


# Initialize all important globals
LOBBY_HOST = '192.168.100.97'
LOBBY_HOST = 'localhost'
LOBBY_PORT = 8001

# Important URLs

WEBSITE_URL = "http://www.nozon.com"

WIKI_URL = "http://vserver01/twiki/bin/view"
SUPPORT_URL = "http://www.faforever.com/forums/viewforum.php?f=3"
TICKET_URL = "http://bitbucket.org/thepilot/falobby/issues"


class ClientState:
    '''
    Various states the client can be in.
    '''
    SHUTDOWN  = -666  #Going... DOWN!
    DROPPED   = -2 # Connection lost
    REJECTED  = -1
    NONE      = 0
    ACCEPTED  = 1
    CREATED   = 2
    OUTDATED  = 9000
    UPTODATE  = 9001 #It's over nine thousaaand!



from _clientwindow import ClientWindow as Client

instance = Client()
