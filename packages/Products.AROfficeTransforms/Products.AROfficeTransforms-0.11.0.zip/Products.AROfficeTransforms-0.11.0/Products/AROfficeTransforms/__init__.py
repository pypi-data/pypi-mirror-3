import logging
from Products.AROfficeTransforms.config import PROJECTNAME

logger = logging.getLogger('Products.AROfficeTransforms')

def initialize(context):
    logger.info("Install")
    from transforms import *
