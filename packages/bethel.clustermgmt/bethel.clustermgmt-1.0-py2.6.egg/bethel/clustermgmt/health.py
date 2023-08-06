import urllib
from types import StringTypes

from zope import schema
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from five import grok
from zExceptions import Redirect, BadRequest
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from silva.core import conf as silvaconf
from silva.core.services.base import ZMIObject
from zeam.form.silva import form as silvaforms
from zeam.form.base import Actions
from zeam.form.base.datamanager import BaseDataManager
from zeam.form.ztk.actions import EditAction

from .interfaces import IHealthReporter


class HealthReporter(ZMIObject):
    """A health reporter is used to as the health checker for zope nodes in a 
       cluster.
       
       It has a ZMI manage screen to set the list of nodes (hosts), and to
       manually take nodes offline.
       
       It also has a REST interface to programmatically take nodes offline.
       [ this method is used by Bethel's Fabric deployment script ]
    """
    meta_type = "Cluster Health Reporter"
    grok.implements(IHealthReporter)
    silvaconf.factory('manage_addHealthReporterForm')
    silvaconf.factory('manage_addHealthReporter')
    silvaconf.icon('healthreporter.png')
    
    manage_options=({'label': 'Manage',
                     'action': 'managenodes'},) + ZMIObject.manage_options

    def __init__(self, id):
        super(HealthReporter, self).__init__(id)
        self.id = id
        self.nodes_in_cluster = set()
        self.offline_nodes = set()
        
    def set_node_status(self, node, status):
        """Update the status of a node.
           `status` is either 'online' or 'offline'
        """
        
        if node not in self.nodes_in_cluster:
            raise KeyError, "unknown node in cluster"
        if status == "online" and node in self.offline_nodes:
            self.offline_nodes.remove(node)
        if status == "offline":
            self.offline_nodes.add(node)
        self._p_changed = 1


manage_addHealthReporterForm = PageTemplateFile(
    "healthReporterAdd", globals(),
    __name__="manage_addHealthReporterForm")
def manage_addHealthReporter(self, name=None, REQUEST=None):
    """Add a Health Reporter
    """
    
    hr = HealthReporter(name)
    self._setObject(name, hr)
    
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST.has_key('submit_edit'):
        u = "%s/%s" % (u, urllib.quote(name))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    else:
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''


class DefaultView(grok.View):
    """Called to perform the actual status check.  If the supplied node is to
       be taken out of service, will raise an error.
       
       Status probes on the load balancer should call this view, explicitly
       passing in the "node to check", e.g. a status probe for node 'zope1'
       may look like: http://backend_host/path/to/checker?node=zope1
       
       The node is explicitly passed in, as some load balancers do not pass
       in enough information to enable the HealthReporter to accurately
       determine the desired node.
    """
    grok.context(IHealthReporter)
    grok.name('index')
    
    def render(self):
        node = self.request.form.get('node', None)
        if not node:
            raise BadRequest("node not present in request")
        if node not in self.context.nodes_in_cluster:
            raise BadRequest("specified node not found")
        if node in self.context.offline_nodes:
            raise BadRequest("node is offline")
        return 'OK'


class ManageMain(grok.View):
    """Redirects the manage_main zmi screen to managenodes
    """
    grok.context(IHealthReporter)
    grok.name('manage_main')
    
    def render(self):
        raise Redirect(self.context.absolute_url() + '/managenodes')


@grok.provider(IContextSourceBinder)
def nodes_source(context):
    """The full list of nodes
    """
    terms = []
    for node in context.nodes_in_cluster:
        terms.append(SimpleTerm(value=node,
                                title=node,
                                token=node
                                ))
    return SimpleVocabulary(terms)


class NodesDataManager(BaseDataManager):
    """Custom data manager to convert the "nodes_in_cluster" value to/from
       a string with newlines into a set.  Since neither zope.schema nor
       zeam.ztk.widgets appears to have a "Lines" field! Bah!
    """
    
    def get(self, id):
        if id == 'nodes_in_cluster':
            return '\n'.join(self.content.nodes_in_cluster)
        else:
            return getattr(self.content, id)
        
    def set(self, id, value):
        if id == 'nodes_in_cluster':
            self.content.nodes_in_cluster = set(value.split())
        else:
            setattr(self.content, id, value)


class IManageNodesSchema(Interface):
    """ Describes the fields for managing the list of nodes in a cluster.
    """
    
    nodes_in_cluster = schema.Text(
        title=u"Nodes",
        description=u"Name of nodes, one per line",
        required=True
        )


class IOfflineNodesSchema(Interface):
    """ Schema for managing which nodes are offline 
    """

    offline_nodes = schema.Set(
        title=u"Offline Nodes",
        description=u"The following nodes are offline",
        required=False,
        value_type=schema.Choice(title=u"node",
                                 source=nodes_source)
        )


class ManageNodes(silvaforms.ZMIComposedForm):
    """A composed form to contain the ZMI management actions.
    """
    
    grok.context(IHealthReporter)
    grok.require("zope2.ViewManagementScreens")
    
    label = u"Manage Cluster Nodes"


class NodeList(silvaforms.ZMISubForm):
    """This subform manages the list of nodes in this cluster.
    """
    grok.view(ManageNodes)
    
    label = u"List of Nodes"
    fields = silvaforms.Fields(IManageNodesSchema)
    ignoreContent = False
    actions = Actions(EditAction(title="Save Nodes"))
    dataManager = NodesDataManager
    prefix = u"nodelist"


class OfflineNodes(silvaforms.ZMISubForm):
    """This subform is a ZMI interface to manage which nodes are reported
       as offline.
    """
    grok.view(ManageNodes)
    
    label = u"Offline Nodes"
    fields = silvaforms.Fields(IOfflineNodesSchema)
    ignoreContent = False
    actions = Actions(EditAction(title="Save Offline Nodes"))
    prefix = u"offlinenodes"
    
    