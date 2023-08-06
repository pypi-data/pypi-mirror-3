from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

silvaconf.extension_name("bethel.clustermgmt")
silvaconf.extension_title("Zope Cluster Management tools")


class IExtension(Interface):
    """Marker for silva extension bethel.clustermgmt"""

install = DefaultInstaller("bethel.clustermgmt", IExtension)

