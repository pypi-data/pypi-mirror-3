from five import grok
from zope.interface import Interface
from silva.core.smi import smi
from silva.core.smi import preview

from Products.Silva.roleinfo import READER_ROLES

import skin

class SMIFooter(smi.SMIFooter):
    grok.context(Interface)
    grok.name('footer')
    grok.layer(skin.ISMIBClearLayer)

class SMIPathBar(smi.SMIPathBar):
    grok.context(Interface)
    grok.name('smipathbar')
    grok.layer(skin.ISMIBClearLayer)

    def can_access_object(self, obj):
        """tests user against roles available on obj to see if
           user is at least a reader on that object"""
        these_roles = obj.sec_get_all_roles()
        return len([val for val in READER_ROLES if val in these_roles])
    
class PreviewFrameset(preview.PreviewFrameset):
    grok.layer(skin.ISMIBClearLayer)
    rows = '157px,*'
