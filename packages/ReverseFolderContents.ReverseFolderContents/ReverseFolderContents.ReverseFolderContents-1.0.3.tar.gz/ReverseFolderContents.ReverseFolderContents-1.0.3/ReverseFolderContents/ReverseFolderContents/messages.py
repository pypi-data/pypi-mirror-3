from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

RFCMF = MessageFactory('ReverseFolderContents.ReverseFolderContents')
ModuleSecurityInfo('ReverseFolderContents.ReverseFolderContents').declarePublic('RFCMF')
