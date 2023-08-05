from Products.CMFCore.DirectoryView import registerDirectory
from Products.PloneContentTemplates.config import SKINS_DIR, GLOBALS

registerDirectory(SKINS_DIR,GLOBALS)

from AccessControl import ModuleSecurityInfo

from zope.i18nmessageid import MessageFactory
PCTMessageFactory = MessageFactory('PloneContentTemplates')
ModuleSecurityInfo('Products.PloneContentTemplates').declarePublic('PCTMessageFactory')
