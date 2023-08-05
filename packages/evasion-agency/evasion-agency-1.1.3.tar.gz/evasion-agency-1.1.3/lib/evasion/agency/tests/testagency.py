"""
"""
import unittest


from evasion import agency
from evasion.agency import config


class TestDevice(object):
    """Used to check the agent manager is calling the correct methods.
    """
    def __init__(self):
        self.setUpCalled = False
        self.tearDownCalled = False
        self.startCalled = False
        self.stopCalled = False
        self.queryCalled = False

    def setUp(self, config):
        self.setUpCalled = True
    
    def tearDown(self):
        self.tearDownCalled = True

    def start(self):
        self.startCalled = True
        
    def stop(self):
        self.stopCalled = True

    def query(self):
        self.queryCalled = True


class AgencyTC(unittest.TestCase):

    def setUp(self):
        # unittesting reset:
        agency.node._reset()

        # unittesting reset:
        agency.manager.shutdown()

        
    def testAgentConfigFilter(self):
        """Test the extraction of devices from a config file which may contain other things.
        """
        test_config = """

        [My section]
        this = 'should be ignored'
        yes = True
        
        [and this too]
        notanagent = 1
        
        [testswipe]
        # first card swipe
        disable = 'no'
        cat = 'swipe'
        alias = 1
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [magtekusbhid]
        # second card swipe
        disable = 'no'
        cat = 'swipe'
        alias = 2
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [tsp700]
        # first printer: load but don't use it.
        disabled = 'yes'
        cat = 'printer'
        alias = 1
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        """
        td1 = TestDevice()
        
        # These should run without problems.
        agents = agency.manager.load(test_config)
        self.assertEquals(len(agents), 3)

        agent1 = agency.manager.agent('swipe/1')
        self.assertEquals(agent1.node, '/agent/swipe/testswipe/1')
        agent1.agent.setParent(td1)

        agent1 = agency.manager.agent('/agent/swipe/1', absolute=True)
        self.assertEquals(agent1.node, '/agent/swipe/testswipe/1')
        agent1.agent.setParent(td1)
        
        # unittesting reset:
        agency.node._reset()

        # unittesting reset:
        agency.manager.shutdown()

        test_config = ""
        agents = agency.manager.load(test_config)
        self.assertEquals(len(agents), 0)

        # unittesting reset:
        agency.node._reset()

        # unittesting reset:
        agency.manager.shutdown()

        test_config = """
        [messenger]
        host = '127.0.0.1'
        """
        agents = agency.manager.load(test_config)
        self.assertEquals(len(agents), 0)

        
    def testmanager(self):
        """Test the Manager class.
        """
        self.assertEquals(agency.manager.agents, 0)

        # Make sure you can't call the following without calling load:
        self.assertRaises(agency.ManagerError, agency.manager.tearDown)
        self.assertRaises(agency.ManagerError, agency.manager.setUp)
        self.assertRaises(agency.ManagerError, agency.manager.start)
        self.assertRaises(agency.ManagerError, agency.manager.stop)

        # shutdown should be ok though:
        agency.manager.shutdown()

        
        td1 = TestDevice()
        td2 = TestDevice()
        td3 = TestDevice()
        
        test_config = """
        
        [testswipe]
        # first card swipe
        disable = 'no'
        cat = 'swipe'
        alias = 1
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [magtekusbhid]
        # second card swipe
        disable = 'no'
        cat = 'swipe'
        alias = 2
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [tsp700]
        # first printer: load but don't use it.
        disabled = 'yes'
        cat = 'printer'
        alias = 1
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        """

        agents = agency.manager.load(test_config)
        self.assertEquals(len(agents), 3)
        
        agent1 = agency.manager.agent('swipe/1')
        self.assertEquals(agent1.node, '/agent/swipe/testswipe/1')
        agent1.agent.setParent(td1)

        agent1 = agency.manager.agent('/agent/swipe/1', absolute=True)
        self.assertEquals(agent1.node, '/agent/swipe/testswipe/1')
        agent1.agent.setParent(td1)

        agent2 = agency.manager.agent('swipe/2')
        self.assertEquals(agent2.node, '/agent/swipe/magtekusbhid/2')
        agent2.agent.setParent(td2)

        agent3 = agency.manager.agent('printer/1')
        self.assertEquals(agent3.node, '/agent/printer/tsp700/1')
        agent3.agent.setParent(td3)

        # Call all the methods and check that the individual
        # agent methods have also been called:
        agency.manager.setUp()
        self.assertEquals(td1.setUpCalled, True)
        self.assertEquals(td2.setUpCalled, True)
        self.assertEquals(td3.setUpCalled, False)

        agency.manager.start()
        self.assertEquals(td1.startCalled, True)
        self.assertEquals(td2.startCalled, True)
        self.assertEquals(td3.startCalled, False)

        agency.manager.stop()
        self.assertEquals(td1.stopCalled, True)
        self.assertEquals(td2.stopCalled, True)
        self.assertEquals(td3.stopCalled, False)

        agency.manager.tearDown()
        self.assertEquals(td1.tearDownCalled, True)
        self.assertEquals(td2.tearDownCalled, True)
        self.assertEquals(td3.tearDownCalled, False)


    def testagencyNodes(self):
        """Test the agent node id generation.
        """
        
        # check that all the agent nodes have no entries:
        for cat in agency.AGENT_CATEGORIES:
            count = agency.node.get(cat)
            self.assertEquals(count, 0)

        self.assertRaises(ValueError, agency.node.add, 'unknown agent class', 'testing' ,'1')

        # test generation of new ids
        node_id, alias_id = agency.node.add('swipe', 'testing', '12')
        self.assertEquals(node_id, '/agent/swipe/testing/1')
        self.assertEquals(alias_id, '/agent/swipe/12')

        node_id, alias_id = agency.node.add('swipe', 'testing', '23')
        self.assertEquals(node_id, '/agent/swipe/testing/2')
        self.assertEquals(alias_id, '/agent/swipe/23')

    
    def testConfigContainer(self):
        """Verify the behaviour of the test container.
        """
        c = config.Container()
        
        # Check it catches that I haven't provided the required fields:
        self.assertRaises(config.ConfigError, c.check)
        
        c.node = '/agent/swipe/testing/1'
        c.alias = '/agent/swipe/1'
        c.cat = 'swipe'
        c.agent = 'agency.agents.testing.swipe'
        c.name = 'testingswipe'
        
        # This should not now raise ConfigError.
        c.check()
    
    
    def testConfiguration(self):
        """Test the configuration catches the required fields.
        """
        test_config = """
        
        [testswipe]
        alias = 1
        cat = 'swipe'
        agent = 'evasion.agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        """
        def check(node, alias):
            pass
         
        agents = agency.config.load(test_config, check)
        agent1 = agents[0]
        
        self.assertEquals(agent1.alias, '/agent/swipe/1')
        self.assertEquals(agent1.node, '/agent/swipe/testswipe/1')        
        self.assertEquals(agent1.name, 'testswipe')        
                
        self.assertEquals(agent1.interface, '127.0.0.1')        
        self.assertEquals(agent1.port, '8810')        


    def testBadConfigurationCatching(self):
        """Test that bad configurations are caught.
        """
        test_config = """
        [testswipe]
        alias = 1
        cat = 'swipe12'           # unknow cat
        agent = 'agency.agents.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        """

        self.assertRaises(agency.ConfigError, agency.config.load, test_config)


        test_config = """
        [testswipe]
        alias = 1
        cat = 'swipe'           
        agent = 'evasion.agency.agents.testing.doesnotexits'     # unknown agent module
        interface = 127.0.0.1
        port = 8810
        
        """
        self.assertRaises(ImportError, agency.config.load, test_config)

        # test duplicated aliases i.e. the two same cat entries have been
        # given the same alias
        test_config = """
        [testswipe]
        alias = 1                    # first alias: OK
        cat = 'fake'           
        agent = 'evasion.agency.agents.testing.swipe'
        interface = 127.0.0.1
        port = 8810

        [magtek]
        alias = 1                   # Duplicate alias!
        cat = 'swipe'           
        agent = 'evasion.agency.agents.testing.fake'     
        
        """

        self.assertRaises(agency.ConfigError, agency.config.load, test_config)
        
        
        
