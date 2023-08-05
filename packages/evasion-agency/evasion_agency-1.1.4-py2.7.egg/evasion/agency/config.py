"""
:mod:`evasion.agency.config`
=====================

.. module:: 'evasion.agency.config'
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>

This module provides the Agent parsing, loading and configuration handling.

.. exception:: evasion.agency.config.ConfigError

.. autoclass:: evasion.agency.config.Container
   :members:
   :undoc-members:

.. autofunction:: evasion.agency.config.load(config, check=None)


"""
import logging
import StringIO
import traceback

import configobj



def get_log():
    return logging.getLogger('evasion.agency.config')


class ConfigError(Exception):
    """This is raised for problems with loading and using the configuration.
    """


class Container(object):
    """This represents a configuration sections as recoverd from the
    agent configuration.

    A config section can have the following options::

        [name]
        # The python path to agent to import e.g.
        agent = 'agency.testing.fake'

        # A ategoary from agency.AGENT_CATEGORIES
        cat = 'general'

        # OPTIONAL: a unique number which can be used instead of name
        # to refer to this agent.
        alias = 1

        # OPTIONAL: disable the setup/tearDown/start/stop of the
        # agent. It will still be loaded and created.
        disabled = 'yes' | 'no'

    """
    reserved = ()
    def __init__(self):
        self.agent = None
        self.cat = None
        self.alias = None
        self.node = None
        self.name = None
        self.disabled = "no"
        # alias is no longer required.
        self.reserved = ('agent', 'cat', 'reserved', 'name')
        self.config = None
        self.agent = None

    def check(self):
        """Called to check that all the reserved fields have been provided.

        If one or more aren't provided then ConfigError
        will be raised to indicate so.

        """
        for i in self.reserved:
            if not getattr(self, i, None):
                raise ConfigError("The member '%s' must be provided in the configuration." % i)

    def __str__(self):
        """Print out who were representing and some unique identifier."""
        #print "self:", self.__dict__
        return "<Agent: node %s, alias %s>" % (self.node, self.alias)


    def __repr__(self):
        """This is a string the represents us, can be used as a dict key."""
        return self.__str__()


def load(config, check=None):
    """Called to test and then load the agent configuration.

    config:
        This is a string representing the contents of the
        configuration file.

    check:
        If this is given the callback will be invoked and
        given the node and alias of the config object. The
        callback can then check if its unique. Its up to the
        user to determine what to do if they're not.

    returned:
        This returns a list of config containers loaded with
        the entries recovered from the device's section.

    """
    cfg = configobj.ConfigObj(StringIO.StringIO(config))
    processed = {}
    # Lazy import to prevent cirular imports:
    from evasion.agency import AGENT_CATEGORIES

    def recover(section, key):

        # If the section does not have and 'agent' then
        # it is not considered and ignored.
        if 'agent' not in section:
            #get_log().info("The config section '%s' does not appear to be an agent section. Ignoring." % key)
            return

        value = section[key]
        c = processed.get(section.name, Container())

        if not c.name:
            c.name = section.name

        if not c.config:
            c.config = section

        if key == 'cat' and value not in AGENT_CATEGORIES:
            raise ConfigError("The class '%s' is not known. It might need adding to '%s'." % (key, AGENT_CATEGORIES))

        elif key == 'agent':
            def recover_agent():
                # default: nothing found.
                returned = None

                # Check I can at least import the stated module.
                try:
                    # absolute imports only:
                    imported_agent = __import__(section[key], fromlist=section[key].split('.'), level=0)
                except ImportError, e:
                     raise ImportError("The agent module '%s' was not found! %s" % (section[key], traceback.format_exc()))

                # TODO:
                #
                # This is not very sophisticate an import, my testharness does
                # this better by importing anything that derives from a set class
                # I should do something like this here.
                #
                if hasattr(imported_agent, 'Agent'):
                    returned = getattr(imported_agent, 'Agent')

                else:
                    get_log().error("No 'Agent' class name found in '%s'." % section[key])

                get_log().debug("setting: %s = %s\n" % (key, value))

                raise returned

                return returned

            value = recover_agent()
            if not value:
                raise ConfigError("I was unable to import '%s'." % (section[key]))

        setattr(c, key, value)
        processed[section.name] = c

    # Process all the config sections creating config containers.
    cfg.walk(recover)

    # Verify we've got all the sections I require:
    alias_check = {}
    def update_and_check(c):
        c.check()
        c.node, c.alias = agency.node.add(c.cat, c.name, c.alias)
        if alias_check.get(c.alias, 0):
            bad = c.alias.split('/')[-1]
            raise ConfigError("A duplicate config alias '%s' has been found for configuration '%s'" % (bad, c.name))
        else:
            alias_check[c.alias] = 1

        return c

    returned = [update_and_check(c) for c in processed.values()]

    return returned
