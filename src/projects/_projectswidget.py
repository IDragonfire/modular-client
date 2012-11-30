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
import util

from projects.createprojectwidget import CreateProjectWidget
from projects.project import Project, ProjectItemDelegate
from projects.step import Step  #, TimelineItemDelegate

FormClass, BaseClass = util.loadUiType("projects/projects.ui")


class ProjectWidget(FormClass, BaseClass):
    def __init__(self, client, *args, **kwargs):
        
        BaseClass.__init__(self, *args, **kwargs)        
 
        self.setupUi(self)
        self.client = client
        self.client.projectsTab.layout().addWidget(self)
       
        self.projects = {}      # Projects names known to the client, contains the player_info messages sent by the server
        self.steps    = {}      # Steps for the current projects
        
        self.projectName = None
        self.project3d = None
        self.compositingProject = None
        
        self.projectList.setItemDelegate(ProjectItemDelegate(self))
        self.projectList.itemDoubleClicked.connect(self.projectDoubleClicked)
        
        self.stepsList.itemPressed.connect(self.stepPressed)

        
        self.client.projectsUpdated.connect(self.processProjectsInfo)
        self.client.powerUpdated.connect(self.powerUpdate)
        self.client.pipeline.stepUpdated.connect(self.stepUpdate)
        self.client.pipeline.taskUpdated.connect(self.taskUpdate)

    def powerUpdate(self):
        if self.client.power >= 16 :
            self.addStepButton.pressed.connect(self.addPipelineStep)
            self.newProjectButton.pressed.connect(self.newProject)
        else :
            self.newProjectButton.setVisible(0)
            self.addStepButton.setVisible(0)        

    def stepPressed(self, item):
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton:
            item.stepPressed()

    def taskUpdate(self, task):
        #TODO : we should be able to update a task that has no step yet, even it shouldn't happen.
        uid = task.pipelineId
        if uid in self.steps :
            self.steps[uid].addingTask(task)

    def stepUpdate(self, step):
        uid = step.uid
        if uid in self.steps : 
            self.steps[uid].update() 
        else :
            self.steps[uid] = Step(step)
            self.steps[uid].update()           
            self.stepsList.addItem(self.steps[uid])

    def loggedInSetup(self):
        self.loadProject()
        self.client.send(dict(command="projects", action="list"))
        
    def projectDoubleClicked(self, item):
        self.client.send(dict(command="projects", action="select", uid = item.uid))
        self.client.currentProject = item
        self.saveProject(item.uid)
        self.stepsList.clear()
  
    def addPipelineStep(self):
        '''
        We are adding a new step to the pipeline.
        Each shot will get these steps by default, but each clip can have an arbitrary number of tasks
        '''
        items = []
        for step in self.client.pipeline.pipeline_steps :
            items.append(self.client.pipeline.pipeline_steps[step].name)
            
        item, ok = QtGui.QInputDialog.getItem(self, "Adding a step to the pipeline",
                "Step:", items, 0, False)
        if ok and item:
            for step in self.client.pipeline.pipeline_steps :
                if self.client.pipeline.pipeline_steps[step].name == item :
                    self.client.send(dict(command="pipeline", action="add_step", uid = step, index = self.client.pipeline.getMaxIndex()+1))
                    return
                    
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
