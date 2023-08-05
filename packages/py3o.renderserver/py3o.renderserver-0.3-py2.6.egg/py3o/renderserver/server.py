import logging
logging.basicConfig(level=logging.DEBUG)

from pyf.transport.packets import Packet
from pyf.station import FlowServer
from pyf.station.utils import (base64encoder, base64decoder, file_to_packets,
        packets_to_file)

from pyjon.utils import get_secure_filename
from pyjon.utils import create_function

import os
import sys
import time
import optparse
#from py3o.renderers.pyuno import Convertor, formats
from py3o.renderers.juno import Convertor, formats

def render(header, flow, callback, soffice_host, soffice_port):
    input_filename = get_secure_filename()
    output_filename = get_secure_filename()

    packets_to_file(flow, input_filename, callback)
    format = formats[header.target_format.upper()]

    convertor = Convertor(soffice_host, soffice_port)
    convertor.convert(input_filename, output_filename, format)

    return output_filename

def dispatcher(flow, client=None, soffice_host=None, soffice_port=None):
    header = flow.next()

    if header.action == 'render':
        callback = lambda key, value, **kwargs: client.message(
                Packet(dict(type='appinfo', key=key, value=value, **kwargs)))

        if header.target_format.upper() in formats.iterkeys():
            output_filename = render(header, base64decoder(flow), callback,
                    soffice_host, soffice_port
                    )

        else:
            raise ValueError, "Unsupported format %s" % header.target_format

        callback("render_status", "ok", filename=output_filename)
        for data in base64encoder(
                file_to_packets(open(output_filename, 'rb'))):
            client.message(data)

        client.success("Process ended successfully")
        os.unlink(output_filename)

    else:
        raise ValueError, "Unsupported action %s" % header.action

    logging.info("end of flow...")


def cmd_line_server():
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
        "-u", "--ure",
        dest="ure_base",
        help="choose a ure base dir, ex: /usr/lib on ubuntu/libreoffice",
        default=None)

    optparser.add_option(
        "-o", "--office",
        dest="office_base",
        help="choose a office base dir, ex: /usr/lib64/libreoffice on ubuntu64/libreoffice",
        default=None)

    optparser.add_option(
        "-r", "--office-release",
        dest="office_release",
        help="choose a office release number to use, ex: 3.3",
        default=None)

    optparser.add_option(
        "-m", "--maxmem",
        dest="maxmem",
        help="how much memory to give to the JVM if you are using juno driver, default is 150Mb",
        default=150)

    optparser.add_option(
        "-t", "--office-type",
        dest="office_type",
        help="Windows only option! By default we try to find LibreOffice, but if you need to use OpenOffice, set this option to --office-type=openoffice",
        default='libreoffice')


    (options, args) = optparser.parse_args()

    start_server(options)



def start_server(options):
    if os.name in ('nt', 'os2', 'ce'):
        # on windows we expect to find LibreOffice or OpenOffice in the registry
        if options.office_type == 'openoffice':
            base_ooregkey = '''SOFTWARE\\OpenOffice.org\\OpenOffice.org'''

        elif options.office_type == 'libreoffice':
            base_ooregkey = '''SOFTWARE\\Wow6432Node\\LibreOffice\\LibreOffice'''

        else:
            raise ValueError('%s is not a valid office type' % options.office_type)

        import _winreg
        # TODO: make sure that we do not explode in flight when the key is
        # not present...
        # TODO: maybe we could use something else than just LOCAL_MACHINE ?
        base_key = _winreg.HKEY_LOCAL_MACHINE
        try:
            key = _winreg.OpenKey(base_key, base_ooregkey)
            # first entry should be 2.3 or something similar
            version = _winreg.EnumKey(key, 0)
            # set this variable for later use
            office_version = version

            #_winreg.CloseKey(key)
            key = _winreg.OpenKey(base_key, "%s\\%s" % (base_ooregkey, version))

        except WindowsError:
            # some error occured:
            # Open Office is not installed on this machine!
            raise ValueError('OpenOffice is not installed on this Windows host')

        soffice_bin, key_type = _winreg.QueryValueEx(key, 'Path')
        soffice_dir = os.path.dirname(soffice_bin)
        soffice_rootdir = os.path.split(soffice_dir)[0]
        #print soffice_bin, soffice_dir, soffice_rootdir
        # TODO: we must test this on Windows... this is only a placeholder
        # for the moment
        ure_base = soffice_rootdir

        # add to search path for uno import!
        sys.path.insert(0, soffice_dir)
        if options.javalib is None and options.driver == 'juno':
            # we need java for juno support so we try to find it ourselves
            try:
                base_java_key = '''SOFTWARE\\JavaSoft\\Java Runtime Environment'''
                key = _winreg.OpenKey(base_key, base_java_key)
                numversions = _winreg.QueryInfoKey(key)[0]
                last_version = _winreg.EnumKey(key, numversions - 1)
                if numversions > 1:
                    logging.warning('Multiple Java versions found, using the highest: %s' % last_version)

                javakey = _winreg.OpenKey(base_key, "%s\\%s" % (base_java_key, last_version))
                jvm, key_type = _winreg.QueryValueEx(javakey, 'RuntimeLib')
            except WindowsError:
                # some error occured:
                # Java is not (correctly?) installed on this machine!
                raise ValueError('Java is not installed on this Windows host')

        else:
            jvm = options.javalib


    else:
        # Here we are on Linux, nothing can be autodetected so we need explicit
        # values from the command line parser
        jvm = options.javalib
        soffice_rootdir = options.office_base
        ure_base = options.ure_base
        office_version = options.office_release

    if not jvm:
        raise ValueError("You must specify a JVM library (run 'config-py3oservice')")

    jvm_path = os.path.abspath(jvm)

    if not os.path.exists(jvm_path):
        raise ValueError("The specified JVM library does not exist, can not proceed")

    if options.driver == 'juno':
        from py3o.renderers.juno import start_jvm
        start_jvm(jvm, soffice_rootdir, ure_base,
                office_version, int(options.maxmem))

    factory = FlowServer(create_function(dispatcher,
                kwargs=dict(
                        soffice_host=options.soffice_host,
                        soffice_port=options.soffice_port)))

    from twisted.internet import reactor
    reactor.listenTCP(int(options.listen_port), factory)
    reactor.run(installSignalHandlers=0)




