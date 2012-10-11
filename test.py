
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QStringList', 2)
sip.setapi('QList', 2)
sip.setapi('QProcess', 2)

import re

from PyQt4 import QtCore, QtXml
import os, re

path = os.path.join("//sledge/vol1/projects/Mc_Trony_P41652/Compositing/EDL/2012-10-08", 'Test xml_01.xml')

file = QtCore.QFile(path)

file.open(QtCore.QIODevice.ReadOnly)
datas = file.readAll()

file.close()


domDocument = QtXml.QDomDocument()
test = domDocument.setContent(datas)
print test
if test[0] == True :
    print "tt"

root = domDocument.documentElement()

nodelist = root.elementsByTagName("clipitem")

clips = []

for i in range(nodelist.count()) :
    child = nodelist.at(i)

    scene = None
    shoot = None
    
    inClip = 0
    outClip = 0
    duration = 0
    start = 0
    end = 0

    n = child.firstChild()
    
    while not n.isNull() :
        e = n.toElement()
        if not e.isNull() :
    
            if e.tagName() == "name" :
               
                p = re.compile('[a-zA-Z]*(\d+)_(\d+)')
                m = p.match(e.text())
                if p.match(e.text()):
                    
                    scene =  m.group(1)
                    shoot =  m.group(2)
                    
            elif e.tagName() == "in" :
                inClip = int(e.text())
            elif e.tagName() == "out" :
                outClip = int(e.text())
            elif e.tagName() == "start" :
                start = int(e.text())
            elif e.tagName() == "end" :
                end = int(e.text())            
            elif e.tagName() == "duration" :
                duration = int(e.text())
     
        n = n.nextSibling()

    if scene != None and shoot != None :
        clips.append(dict(idClip = i, scene = scene, shoot = shoot, inClip = inClip, outClip = outClip, start=start, end=end, duration=duration))



 
#print domDocument.firstChildElement().tagName()