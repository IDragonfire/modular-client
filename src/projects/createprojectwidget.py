from PyQt4 import QtCore, QtGui


import util, re


FormClass, BaseClass = util.loadUiType("projects/createProject.ui")


class CreateProjectWidget(FormClass, BaseClass):
    def __init__(self, parent, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)       

        self.setupUi(self)
        self.parent = parent
        
        #reset values
        self.parent.projectName = None
        self.parent.project3d = None
        self.parent.compositingProject = None
        
        self.setWindowTitle("Create DB project")
        
        self.setStyleSheet(self.parent.client.styleSheet())

        self.manualText = False

        self.project3dBox.addItems(util.list3dProjects())       
        self.projectCompBox.addItems(util.compositingProjects())
        

        self.project3dBox.currentIndexChanged.connect(self.project3dChanged)
        self.projectCompBox.currentIndexChanged.connect(self.projectCompChanged)
        self.projectName.textChanged.connect(self.textEdited)
        
       
    
        self.confirmButton.pressed.connect(self.createProject)
        self.cancelButton.pressed.connect(self.close)

    def textEdited(self):
        self.manualText = True

    def createProject(self):
        self.parent.projectName = self.projectName.text()
        self.parent.project3d = self.project3dBox.currentText()
        self.parent.compositingProject = self.projectCompBox.currentText()
        self.done(1)
    
    def project3dChanged(self, idx):
        
        if self.projectName.text() == ""  or self.manualText == False :
        
            project = self.project3dBox.itemText(idx)
            self.projectName.setText(project)
            self.manualText = False
        
        
        


    def projectCompChanged(self, idx):
        
        if self.projectName.text() == ""  or self.manualText == False :
        
            projectP = self.projectCompBox.itemText(idx)
            project = projectP
            p = re.compile('^(.+)(_P\d+$)')
    
        
            m = p.match(projectP)
            if p.match(projectP):
                project = m.group(1)
            
            self.projectName.setText(project)
            self.manualText = False
            
