""" Base module for sparql tests
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import eea.sparql

import BaseHTTPServer
import threading
from eea.sparql.tests.mock_server import Handler

@onsetup
def setup_sparql():
    """Set up the additional products.
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', eea.sparql)
    fiveconfigure.debug_mode = False

    ztc.installPackage('eea.sparql')


setup_sparql()
ptc.setupPloneSite(products=['eea.sparql'])

#port for mock http server
from eea.sparql.tests.mock_server import PORT

class SparqlFunctionalTestCase(ptc.FunctionalTestCase):
    """ Base class for functional integration tests for the Sparql product.
    """
    def setUp(self):
        """ Start the mock http server on port 8888
            Since we make only one request we can use handle_request
        """
        self.server = BaseHTTPServer.HTTPServer(("", PORT), Handler)
        self.server_thread = threading.Thread(target=self.server.handle_request)
        self.server_thread.start()

    def tearDown(self):
        """ Stop the mock http server """
        self.server.server_close()
        self.server_thread.join()

    def afterSetUp(self):
        """ After setup """
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])
