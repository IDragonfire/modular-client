

import subprocess

app = "\\\\VSERVER01\\RoyalRender6\\bin\\win\\ffmpeg.exe -r 24 -i s:\\projects\\McT\\images\\playblasts\\003_012_004\\003_012_004.%04d.tga -y -an -qscale 1 -vcodec mpeg2video c:\\workspace\\playblast\\test.mpg"
args = [app, "-r 24 -i s:\projects\McT\images\playblasts\003_012_004\003_012_004.%04d.tga -y -an -qscale 1 -vcodec mpeg2video c:\workspace\playblast\test.mpg"]



path = "\\\\VSERVER01\\RoyalRender6\\bin\\win"




process = subprocess.Popen(app)

from PyQt4 import QtCore
instance = QtCore.QProcess()
instance.startDetached(app)        
