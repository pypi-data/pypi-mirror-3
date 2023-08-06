import json

from zExceptions import BadRequest

from HealthTestCase import HealthTestCase

class HealthFunctionalTestCase(HealthTestCase):
    
    def setUp(self):
        super(HealthFunctionalTestCase, self).setUp()
        self.browser = self.layer.get_browser()
        self.browser.options.handle_errors = False
        self.hr_url = self.layer.hr.absolute_url()
        self.root = self.layer.get_application()
        
    def test_add(self):
        #verify the zmi add form is functional
        b = self.browser
        b.login('manager')
        code = b.open('/root/manage_addProduct/bethel.clustermgmt/manage_addHealthReporterForm')
        self.assertEquals(code, 200)
        f = b.get_form(name="addform")
        f.get_control("name").value="healthreporter"
        code = f.submit(name="submit_add")
        self.assertEquals(code, 200)
        self.assertTrue(getattr(self.root, 'healthreporter', None) is not None)

        code = b.open('/root/manage_addProduct/bethel.clustermgmt/manage_addHealthReporterForm')
        self.assertEquals(code, 200)
        f = b.get_form(name="addform")
        f.get_control("name").value="healthreporter1"
        code = f.submit(name="submit_edit")
        self.assertEquals(code, 200)
        self.assertEquals(b.url,
                          '/root/healthreporter1/managenodes')
    
    def test_managemain(self):
        #make sure that accessing manage_main redirects to the real
        # management screen
        b = self.browser
        b.login('manager')
        code = b.open(self.hr_url + '/manage_main')
        self.assertEquals(b.url,
                          '/root/hr/managenodes')

    def test_zmi_form_nodelist(self):
        b = self.browser
        root = self.layer.get_application()
        
        #try to access main mgmt form, should fail
        b.login('dummy')
        code = b.open(self.hr_url + '/managenodes')
        self.assertEquals(code, 401)
        
        b.login('manager')
        
        #it's possible to save the nodes as manager
        b.open(self.hr_url + '/managenodes')
        f = b.get_form(name='nodelist')
        f.get_control("nodelist.field.nodes_in_cluster").value="zope1\r\nzope2"
        code = f.submit(name="nodelist.action.save-nodes")
        self.assertEquals(root.hr.nodes_in_cluster,
                          set(['zope1', 'zope2']))
        
        #saving duplicates results in dedupping (since it's a set)
        b.open(self.hr_url + '/managenodes')
        f = b.get_form(name='nodelist')
        f.get_control("nodelist.field.nodes_in_cluster").value="zope1\r\nzope2\r\nzope1"
        code = f.submit(name="nodelist.action.save-nodes")
        self.assertEquals(root.hr.nodes_in_cluster,
                          set(['zope1', 'zope2']))
    
    def test_zmi_form_offline(self):
        #use the zmi form to take nodes offline / out of service
        b = self.browser
        root = self.layer.get_application()
        
        b.login('manager')
        
        #initial set of nodes, with one offline
        root.hr.nodes_in_cluster = set(['zope1','zope2'])
        root.hr.offline_nodes = ['zope1']
        
        #verify form controls are accurate
        b.open(self.hr_url + '/managenodes')
        f = b.get_form(name='offlinenodes')
        nodes = f.get_control('offlinenodes.field.offline_nodes')
        self.assertEquals(root.hr.offline_nodes,
                          nodes.value)
        
        #switch offline to other node
        nodes.value = ['zope2']
        code = f.submit(name="offlinenodes.action.save-offline-nodes")
        self.assertEquals(root.hr.offline_nodes,
                          set(['zope2']))

        #now put all into service (offline is an empty set)
        f = b.get_form(name='offlinenodes')
        nodes = f.get_control('offlinenodes.field.offline_nodes')
        nodes.value = []
        code = f.submit(name="offlinenodes.action.save-offline-nodes")
        self.assertEquals(root.hr.offline_nodes,
                          set([]))
    
    def test_rest_status(self):
        #test ++rest++nodestatus
        
        b = self.browser
        root = self.layer.get_application()
        
        #XXX this should change to a different user having just the 'XXX'
        #    permission (what perm is that?)
        b.login('manager')
        
        #initial set of nodes, with one offline
        root.hr.nodes_in_cluster = set(['zope1','zope2'])
        root.hr.offline_nodes = set(['zope1'])
        
        code = b.open(self.hr_url + '/++rest++nodestatus')
        self.assertEquals(code, 200)
        self.assertEquals(b.contents,
                          '{"zope1": {"status": "offline"}, "zope2": {"status": "online"}}')
        
        root.hr.offline_nodes = set([])
        code = b.open(self.hr_url + '/++rest++nodestatus')
        self.assertEquals(code, 200)
        self.assertEquals(b.contents,
                          '{"zope1": {"status": "online"}, "zope2": {"status": "online"}}')
        
    def test_rest_setstatus(self):
        #test ++rest++setstatus, or setting the offline/online status of nodes

        b = self.browser
        root = self.layer.get_application()
        change = {'zope1':{'status':'offline'}}
        
        #not even chiefeditors can access this
        b.login('chiefeditor')
        code = b.open(self.hr_url + '/++rest++setstatus',
                      method='POST',
                      form={"change":json.dumps(change)})
        self.assertEquals(code, 401)
        
        
        #XXX this should change to a different user having just the 'XXX'
        #    permission (what perm is that?)
        b.login('manager')
        
        #initial set of nodes, with one offline
        root.hr.nodes_in_cluster = set(['zope1','zope2'])
        
        #stupid infrae.testbrowser and infrae.rest don't support passing in
        # jquery as simply jquery in the POST payload.  Need to piggyback it
        # as the value to a GET or POST param
        code = b.open(self.hr_url + '/++rest++setstatus',
                      method='POST',
                      form={"change":json.dumps(change)})
        
        self.assertEquals(root.hr.offline_nodes,
                          set(['zope1']))
        
        change['zope1']['status'] = 'online'
        code = b.open(self.hr_url + '/++rest++setstatus',
                      method='POST',
                      form={"change":json.dumps(change)})
        
        self.assertEquals(root.hr.offline_nodes,
                          set([]))


    def test_call(self):
        #test default view, raising errors, etc
        b = self.browser
        root = self.layer.get_application()
        root.hr.nodes_in_cluster = set(['zope1','zope2'])
        root.hr.offline_nodes = set(['zope1'])
        
        self.assertRaises(BadRequest, b.open, self.hr_url,
                          query={'node': 'zope1'})
        
        code = b.open(self.hr_url,
                      query={'node': 'zope2'})
        self.assertEquals(code, 200)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HealthFunctionalTestCase))
    return suite