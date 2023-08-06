from Products.Silva.testing import SilvaLayer
import transaction


class HealthLayer(SilvaLayer):
    
    def _install_application(self, app):
        """ install the silva event extension """
        super(HealthLayer, self)._install_application(app)
        app.root.service_extensions.install('bethel.clustermgmt')
        self.hr = self.addObject(app.root,
                                 'HealthReporter',
                                 'hr',
                                 product='bethel.clustermgmt')
        
    #add a news publication
    def addObject(self, container, type_name, id, product='Silva', **kw):
        getattr(container.manage_addProduct[product],
                'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        transaction.savepoint()
        return getattr(container, id)
        