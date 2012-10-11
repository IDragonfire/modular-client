
import logging

logger = logging.getLogger("npm.projects")
logger.setLevel(logging.DEBUG)



# For use by other modules
from _projectswidget import ProjectWidget as Projects
