# Package

from Products.Silva.Root import Root
from silva.core import conf as silvaconf
from silva.core.interfaces import IExtensionInstaller
from zope.interface import implements

silvaconf.extension_name("smitheme.bclear")
silvaconf.extension_title("SMI Theme BClear (Bethel Clear Skin)")
silvaconf.extension_depends(["Silva"])


BCLEAR_SKIN = 'smitheme.bclear.skin.ISMIBClearSkin'


class Installer(object):
    implements(IExtensionInstaller)

    def install(self, root):
        root._smi_skin = BCLEAR_SKIN

    def uninstall(self, root):
        root._smi_skin = Root._smi_skin

    def is_installed(self, root):
        return root._smi_skin == BCLEAR_SKIN


install = Installer()