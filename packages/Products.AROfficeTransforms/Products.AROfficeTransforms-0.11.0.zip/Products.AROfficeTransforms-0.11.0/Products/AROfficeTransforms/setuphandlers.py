from Products.MimetypesRegistry import MimeTypeItem
from Products.CMFCore.utils import getToolByName

from Products.AROfficeTransforms.config import TRANSFORMS
from Products.AROfficeTransforms import logger


def install(self):
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if self.readDataFile('Products.AROfficeTransforms-tranforms.txt') is None:
        return
    #
    transform_tool = getToolByName(self, 'portal_transforms')
    for transform in TRANSFORMS:
        logger.info("Adding %s transform..." % transform)
        # Remove existing transform, if any
        if transform in transform_tool.objectIds():
            logger.info("%s transform already exists" % transform)
            logger.info("Deleting %s transform..." % transform)
            try:
                transform_tool.manage_delObjects([transform])
                logger.info("%s deleted" % transform)
            except Exception, e:
                logger.exception(e.__class__.__name__, str(e))
        transform_tool.manage_addTransform(transform, 'Products.AROfficeTransforms.transforms.'+transform)
        logger.info("%s added" % transform)


def uninstall(self):
    transform_tool = getToolByName(self, 'portal_transforms')
    for transform in TRANSFORMS:
        logger.info("Deleting %s transform..." % transform)
        if transform in transform_tool.objectIds():
            try:
                transform_tool.manage_delObjects([transform])
                logger.info("%s deleted" % transform)
            except Exception, e:
                logger.exception(e.__class__.__name__, str(e))
        else:
            logger.info("%s transform not exists" % transform)
