"""
:mod:`agency.scripts.manager` -- This supervises then agents under its control.
=================================================================================

.. module:: 'agency.scripts.manager'
   :platform: Unix, MacOSX, Windows
   :synopsis: This supervises then agents under its control.
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>

This is where the main function to run the agency lives. This will generally be run and managed by 
the director.

.. autofunction:: agency.scripts.manager.appmain(isExit)
.. autofunction:: agency.scripts.manager.setup(logconfig, deviceconfig, managerconfig)
.. autofunction:: agency.scripts.manager.exit()
.. autofunction:: agency.scripts.manager.run(app=appmain)
.. autofunction:: agency.scripts.manager.create_config(cfg_data)
.. autofunction:: agency.scripts.manager.main()
   

"""
import os
import sys
import time
import pprint
import os.path
import logging
import logging.config
from configobj import ConfigObj
from optparse import OptionParser
from pydispatch import dispatcher


def get_log():
    return logging.getLogger("agency.manager")


def appmain(isExit):
    """The application main loop.

    isExit:
        This is a function that will return true
        when its time to exit.
        
    """
    def event_watch(signal, sender, **data):
        """Show the event we've received so far."""
        get_log().debug("Event watch - signal:%s, sender:%s" % (signal, sender))

    # pickup all events from anybody:
    dispatcher.connect(
        event_watch,
        signal = dispatcher.Any,
        sender = dispatcher.Any,
    )

    print "Appmain running."
    while not isExit():
        time.sleep(0.5)
    print "Appmain exit."


def setup(logconfig, managerconfig):
    """Setup the various pieces of information based on the given details.

    logconfig:
        path and file to the log configuration. If it doesn't exit
        a default stdout configuration will be used.

    managerconfig (required):
        The device configuration to load, setup and start running.

        The configuration for stomp, locale, etc setup.
    
    """
    # Set up python logging if a config file is given:
    if os.path.isfile(logconfig):
        logging.config.fileConfig(logconfig)
        
    else:
        # No log configuration file given or it has been overidden
        # by the user, just print out to console instead:
        log = logging.getLogger()
        hdlr = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
        log.setLevel(logging.DEBUG)
        logging.getLogger("agency")

    # Check the requried config files exits:
    check_exits = [
        managerconfig,
    ]    
    for f in check_exits:
        if not os.path.isfile(f):
            raise SystemError("The file '%s' was not found!" % f)

    # Set up manager details from its config. Stomp, etc...
    import configobj
    dm_cfg = configobj.ConfigObj(infile=managerconfig)
        
    # Set up the messenger protocols where using:            
    import messenger

    stomp_cfg = dict(
        host = dm_cfg['Messenger'].get("host"),
        port = dm_cfg['Messenger'].get("port"),
        username = dm_cfg['Messenger'].get("username"),
        password = dm_cfg['Messenger'].get("password"), 
        channel = dm_cfg['Messenger'].get("channel"), 
    )
    stomp_cfg['port'] = int(stomp_cfg['port'])
    messenger.stompprotocol.setup(stomp_cfg)

    # Load the device/hardware configuration file, set it up
    # and start the devices running ready for use:
    import agency
    from agency import manager

    manager.load(dm_cfg)
    manager.setUp()
    manager.start()


def exit():
    """Called by the service to stop the device manager and exit.
    """
    import messenger
    messenger.quit()
    time.sleep(1)
        

def run(app=appmain):
    """Called to run a set up manager running twisted in the main loop
    and the app in its own thread.
    """
    import messenger
    import agency
 
    # Messaging system needs to run as the main loop the program will run 
    # inside appmain(), which is run in a different thread.
    try:
        messenger.run(app)
        
    except KeyboardInterrupt, e:
        agency.shutdown()
        exit()
        
    except:
        agency.shutdown()

#
DEFAULT_CONFIG_NAME = "devices.cfg"
DEFAULT_MANAGER_CONFIG_NAME = "manager.cfg"
DEFAULT_LOGCONFIG_NAME = "manager-log.cfg"

def create_config(cfg_data):
    """Create the default director.ini in the current directory based
    on a the template stored in director.templatecfg
    """
    import agency
    import agency.templatecfg
    from mako.template import Template
    from pkg_resources import resource_string

    print("Creating initial configuration: '%s', '%s' and '%s'." % (DEFAULT_CONFIG_NAME, DEFAULT_MANAGER_CONFIG_NAME, DEFAULT_LOGCONFIG_NAME))

    # Recover the template file we will fill out with the path information:
    dcfg_data = resource_string(agency.templatecfg.__name__, 'devices.cfg.in')
    mcfg_data = resource_string(agency.templatecfg.__name__, 'manager.cfg.in')
    logcfg_data = resource_string(agency.templatecfg.__name__, 'log.cfg.in')

    # Ok, write the result out to disk:
    fd = open(DEFAULT_CONFIG_NAME, 'w')
    fd.write(dcfg_data)
    fd.close()
    
    fd = open(DEFAULT_MANAGER_CONFIG_NAME, 'w')
    fd.write(mcfg_data)
    fd.close()
    
    fd = open(DEFAULT_LOGCONFIG_NAME, 'w')
    fd.write(Template(logcfg_data).render(**cfg_data))
    fd.close()

    print("Success, '%s', '%s' and '%s' created ok." % (DEFAULT_CONFIG_NAME, DEFAULT_MANAGER_CONFIG_NAME, DEFAULT_LOGCONFIG_NAME))

        
def main():
    """Main program for commandline non-service manager.
    """
    parser = OptionParser()
    parser.add_option("--logdir", action="store", dest="logdir", default=".",
                      help="Where log file goes in template log.")
    parser.add_option("--logconfig", action="store", dest="logconfig_filename", default="log.cfg",
                      help="This is the logging config file.")
    parser.add_option("--config", action="store", dest="config_filename", default="devices.cfg",
                      help="This the hardware configuration file.")
    parser.add_option("--create", action="store_true", dest="create_config", default=False,
                      help="Create the default manager.cfg and device.cfg.")
    (options, args) = parser.parse_args()

    if options.create_config:
        create_config(dict(
            log_dir=options.logdir,
            logconfig=options.logconfig_filename,
            config=options.config_filename,
            dmconfig=options.manager_config,
        ))
    else:
        setup(
            logconfig=options.logconfig_filename,
            managerconfig=options.manager_config,
        )
        run(appmain)
    
    
if __name__ == "__main__":
    main()
    
    
    


