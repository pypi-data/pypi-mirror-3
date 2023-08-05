#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# setup.py

from distutils.core import setup
from distutils.core import Command
import os, glob, sys
import py2exe

dist_dir = "dist\\py3o.openoffice.service"

include_modules = ['_winreg', "win32com", "win32service",
                    "win32serviceutil",
                    "win32event"]

include_packages = ["encodings",]
options = dict()
	
# Some things we do not need in our build
dll_excludes = list()
excludes = []

def __removedirs(top):
	for root, dirs, files in os.walk(top, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))
	if os.path.exists(top):
		os.rmdir(top)

def __removefiles(top, suffix):
	for root, dirs, files in os.walk(top):
		for name in files:
			if name.endswith(suffix):
				os.remove(os.path.join(root, name))


if "clean" in sys.argv:
    top = os.getcwd()

    __removedirs(os.path.join(top, dist_dir))
    __removedirs(os.path.join(top, 'build'))
    __removefiles(top, 'pyc')

# If run without args, build win32 executables.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        #self.version = "0.5.0"
        self.company_name = ""
        self.copyright = "Florent AIDE 2010"
        self.name = "py3o.ooservice"

class MyCommand(Command):
    depend_files = []

    def need_build(self, file):
        for dep_file in self.depend_files:
            if newer(dep_file, file):
                return True

class NSI(MyCommand):

    user_options = [('version', 'V', "Set version")]

    def initialize_options(self):
        self.version = VERSION

    def finalize_options(self):
        pass

    def need_py2exe(self):
        return True

    def run(self):
        call_args = [MAKENSIS_EXECUTABLE, '/DVersion=%s' % VERSION, NSI_FILE]
        Popen(args=call_args)

# an xml template file for winXP control
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24
#RT_ICON = 3

py3o_openofficeservice = Target(
	description = "Open Office headless as a windows service",
	modules = ['ooservice'],
    create_exe = True,
    create_dll = True,
	icon_resources = [],
	other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="py3o.ooservice"))],
	dest_base = "py3o.ooservice",
    # this is to make sure our service will work
    cmdline_style='pywin32',
    )

py3o_openofficesetup = Target(
	description = "Open Office headless as a windows service",
	script = 'service-setup.py',
    create_exe = True,
    create_dll = True,
	icon_resources = [],
	other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="py3o.ooservice.setup"))],
	dest_base = "py3o.ooservice.setup",
    )

add_data = []

setup(
	options = {"py2exe": {
						"compressed": 1,
						"optimize": 2,
						"packages": include_packages,
						"includes": include_modules,
						"excludes": excludes,
						"dll_excludes": dll_excludes,
						"dist_dir": dist_dir,
						},
			},

	zipfile = "data\\shared.lib",
	console = [py3o_openofficesetup],
	windows = [],
	service = [py3o_openofficeservice],
	data_files = add_data,
    cmdclass = dict(nsi=NSI),
	)


