from silva.core.smi.interfaces import ISMILayer
from silva.core.layout.jquery.interfaces import IJQueryResources
from silva.core import conf as silvaconf

class ISMIBClearLayer(ISMILayer):
    pass


class ISMIBClearSkin(ISMIBClearLayer):
    silvaconf.resource('bclear.css')
    silvaconf.resource('jquery.smi.js')
