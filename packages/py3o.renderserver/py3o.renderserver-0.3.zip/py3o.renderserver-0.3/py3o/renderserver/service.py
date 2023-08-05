# File name: service.py
#
# The service module defines a single class (Py3oWindowsService) that contains
# the functionality for running a py3o.renderserver as a Windows Service.
# 
# To use this class, users must do the following:
# 1. Download and install the win32all package
#    (http://starship.python.net/crew/mhammond/win32/)
#
# 2. Open a command prompt and navigate to the directory where this file
#    is located.  Use one of the following commands to
#    install/start/stop/remove the service:
#    > service.py install
#    > service.py start
#    > service.py stop
#    > service.py remove
#    Additionally, typing "service.py" will present the user with all of the
#    available options for controlling an installed service
#
#    to configure the service use the commands provided by the service.py --help
#    this command is handled by our own program and not by the windows service framework
#
# Once installed, the service will be accessible through the Services
# management console just like any other Windows Service.  All service 
# startup exceptions encountered by the Py3oWindowsService class will be 
# viewable in the Windows event viewer (this is useful for debugging
# service startup errors); all application specific output or exceptions that
# are not captured by the standard TG logging mechanism should 
# appear in the stdout/stderr logs.
#
# This module has been tested on Windows Server 2000, 2003, and Windows
# XP Professional.

from ConfigParser import SafeConfigParser
import optparse
import logging
import sys
import os
from os.path import *

import win32serviceutil
import win32service
import win32event
import win32process
import win32api
from win32com.client import constants
import _winreg


import pkg_resources
from pkg_resources import iter_entry_points
from pkg_resources import working_set, Environment

# the org name used to store your conf in the registry
organization = "py3o"
product_name = "py3o-renderserver"

def get_config():
    """find the config file path in the registry
    """
    class Config(object):
        pass

    config = Config()

    try:
        reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\%s\\%s' % (organization, product_name))

        config.soffice_host = _winreg.QueryValueEx(reg_key, 'soffice_host')[0]
        config.soffice_port = _winreg.QueryValueEx(reg_key, 'soffice_port')[0]
        config.listen_port = _winreg.QueryValueEx(reg_key, 'listen_port')[0]
        config.javalib = _winreg.QueryValueEx(reg_key, 'javalib')[0]
        config.driver = _winreg.QueryValueEx(reg_key, 'driver')[0]
        config.maxmem = _winreg.QueryValueEx(reg_key, 'maxmem')[0]
        #config.libdir = _winreg.QueryValueEx(reg_key, 'libdir')[0]

    except WindowsError, e:
        logging.exception(str(e))

    return config


def scan_directory(directory):
    distributions, errors = working_set.find_plugins(
            Environment([directory])
    )

    map(working_set.add, distributions)

    if len(errors) > 0:
        raise ValueError("Couldn't load %s" % errors)

class NullOutput(object):
    """a file-like object that behaves like a black hole.
    Does not consume memory and gives nothing back. Ever.
    """
    def noop(self, *args, **kw):
        pass

    write = writelines = close = seek = flush = truncate = noop

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration

    def isatty(self):
        return False

    def tell(self):
        return 0

    def read(self, *args, **kw):
        return ''

    readline = read

    def readlines(self, *args, **kw):
        return list()



def set_config(options):
    """set the config file path in the registry
    """
    reg_key = _winreg.CreateKey(_winreg.HKEY_LOCAL_MACHINE,
            'SOFTWARE\\%s\\%s' % (organization, product_name))

    reg_val = _winreg.SetValueEx(
            reg_key, 'soffice_host', None, _winreg.REG_SZ, options.soffice_host)
    reg_val = _winreg.SetValueEx(
            reg_key, 'soffice_port', None, _winreg.REG_SZ, options.soffice_port)
    reg_val = _winreg.SetValueEx(
            reg_key, 'listen_port', None, _winreg.REG_SZ, options.listen_port)
    reg_val = _winreg.SetValueEx(
            reg_key, 'javalib', None, _winreg.REG_SZ, options.javalib)
    reg_val = _winreg.SetValueEx(
            reg_key, 'driver', None, _winreg.REG_SZ, options.driver)
    reg_val = _winreg.SetValueEx(
            reg_key, 'maxmem', None, _winreg.REG_SZ, options.maxmem)

    # reg_val = _winreg.SetValueEx(
    #         reg_key, 'libdir', None, _winreg.REG_SZ, options.libdir)

class Py3oWindowsService(win32serviceutil.ServiceFramework):
    """The Py3oWindowsService class contains all the functionality required
    for running a py3o renderserver as a Windows Service. The only
    user edits required for this class are located in the following class
    variables:

    _svc_name_:         The name of the service (used in the Windows registry).
                        DEFAULT: The capitalized name of the current directory.
    _svc_display_name_: The name that will appear in the Windows Service Manager.
                        DEFAULT: The capitalized name of the current directory.

    For information on installing the application, please refer to the
    documentation at the end of this module or navigate to the directory
    where this module is located and type "service.py" from the command
    prompt.
    """
    _svc_name_ = '%s' % (product_name)
    _svc_display_name_ = _svc_name_
    _svc_deps = list()

    def __init__(self, args):
        """set some usefull variables
        """

        # replace normal output channels by fake ones
        # to make sure we don't go over the buffer and inadvertently
        # kill our windows service
        #sys.stdout.close()
        #sys.stderr.close()
        sys.stdout = NullOutput()
        sys.stderr = NullOutput()

        win32serviceutil.ServiceFramework.__init__(self, args)
        #self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        """Called when the Windows Service runs."""

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        try:
            config = get_config()
            from py3o.renderserver.server import start_server
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            start_server(config)

        except Exception, e:
            # something went wrong and we did not start correctly
            self.ReportServiceStatus(win32service.SERVICE_ERROR_CRITICAL)
            import servicemanager
            servicemanager.LogErrorMsg("The service could not start for the folloing reason: %s" % str(e))
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcStop(self):
        """Called when Windows receives a service stop request."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        from twisted.internet import reactor
        reactor.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def config():
    """write the configuration parameters of the py3o-renderserver service in the windows registry
    """
    optparser = optparse.OptionParser()

    optparser.add_option(
        "-a", "--sofficehost",
        dest="soffice_host",
        help="specify the open office hostname/ip address ADDR",
        metavar="ADDR",
        default="127.0.0.1")

    optparser.add_option(
        "-p", "--sofficeport",
        dest="soffice_port",
        help="specify the open office port PORT",
        metavar="PORT",
        default="8997")

    optparser.add_option(
        "-l", "--listenport",
        dest="listen_port",
        help="specify the PORT on which our service will listen",
        metavar="PORT",
        default=8994)

    optparser.add_option(
        "-d", "--driver",
        dest="driver",
        help="choose a driver between juno & pyuno",
        default='juno')

    optparser.add_option(
        "-j", "--java",
        dest="javalib",
        help="choose a jvm.dll/jvm.so to use if you are using the juno driver",
        default=None)

    optparser.add_option(
        "-m", "--maxmem",
        dest="maxmem",
        help="how much memory to give to the JVM if you are using juno driver, default is 150Mb",
        default='150')


    (options, args) = optparser.parse_args()
    set_config(options)


def setup():
    """basic win32 service setup: install or remove or update or start or stop the service
    """

    # The following are the most common command-line arguments that are used
    # with this module:
    #  service.py install (Installs the service with manual startup)
    #  service.py --startup auto install (Installs the service
    #  with auto startup)
    #  service.py start (Starts the service)
    #  service.py stop (Stops the service)
    #  service.py remove (Removes the service)
    #
    # For a full list of arguments, simply type "service.py".

    win32serviceutil.HandleCommandLine(Py3oWindowsService)
    
    
