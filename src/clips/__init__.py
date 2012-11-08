import logging

logger = logging.getLogger("npm.clips")
logger.setLevel(logging.DEBUG)

# For use by other modules
from _clipswidget import ClipsWidget as Clips
