from PyQt4 import QtCore, QtGui
import util

from projects.createprojectwidget import CreateProjectWidget
from projects.project import Project


FormClass, BaseClass = util.loadUiType("projects/projects.ui")


class ProjectWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
        
        self.setupUi(self)

        self.client = client
        self.client.projectsTab.layout().addWidget(self)
       
        self.projects = {}       # projects names known to the client, contains the player_info messages sent by the server
        
        self.projectName = None
        self.project3d = None
        self.compositingProject = None
        
        if self.client.power >= 16 :
            self.newProjectButton.pressed.connect(self.newProject)
        else :
            self.newProjectButton.setVisible(0)
            
        
        self.client.projectsUpdated.connect(self.processProjectsInfo)
    
        self.projectList.itemDoubleClicked.connect(self.projectDoubleClicked)


        self.loadProject()
        self.client.send(dict(command="projects", action="list"))

    def projectDoubleClicked(self, item):
        self.client.send(dict(command="projects", action="select", uid = item.uid))

        self.client.currentProject = item
  
        self.saveProject(item.uid)
 
  
    def newProject(self):
        createprojectwidget = CreateProjectWidget(self)  
        if createprojectwidget.exec_() == 1 :
            if self.projectName != "" and self.projectName != None :
                self.client.send(dict(command="projects", action="create", name = self.projectName, project3d=self.project3d, projectComp=self.compositingProject))

    def processProjectsInfo(self, message):
        ''' 
        Slot that interprets and propagates projects_info messages into Projects Items
        '''
        uid = message["uid"]            
        
        if uid in self.projects: 
            self.projects[uid].update(message, self.client) 
        else :
            self.projects[uid] = Project(uid)
            self.projectList.addItem(self.projects[uid])
            self.projects[uid].update(message, self.client)
        

    def saveProject(self, uid):
        util.settings.beginGroup("npm.projects")
        util.settings.setValue("project", uid)        
        util.settings.endGroup()             

    def loadProject(self):

        util.settings.beginGroup("npm.projects")
        projectId = util.settings.value("project", None)        
        util.settings.endGroup() 

        if projectId :
            self.client.send(dict(command="projects", action="select", uid = projectId))