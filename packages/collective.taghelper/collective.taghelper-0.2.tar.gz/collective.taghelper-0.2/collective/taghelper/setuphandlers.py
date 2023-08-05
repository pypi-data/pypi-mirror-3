import logging
from Products.CMFCore.utils import getToolByName
from collective.taghelper.config import PROJECTNAME

PROFILE_ID = 'profile-%s:default' % PROJECTNAME

def upgrade_registry(context, logger=None):
    """Re-import the portal configuration registry settings.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.taghelper')
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')
    logger.info("imported registry settings")
    return
