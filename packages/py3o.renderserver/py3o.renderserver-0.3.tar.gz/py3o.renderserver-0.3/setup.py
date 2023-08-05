from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='py3o.renderserver',
      version=version,
      description="An easy solution to transform libreoffice/openoffice documents to supported formats",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='LibreOffice OpenOffice PDF',
      author='Florent Aide',
      author_email='florent.aide@gmail.com',
      url='http://bitbucket.org/faide/py3o.renderserver',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['py3o'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'pyf.station >= 2.0.1',
          'pyjon.utils',
          'py3o.renderers.juno >= 0.3',
          ],
      entry_points=dict(
          # -*- Entry points: -*-
          console_scripts=[
              'start-py3o-renderserver = py3o.renderserver.server:cmd_line_server',
              'config-ooservice = ooservice.ooservice:config',
              'setup-ooservice = ooservice.ooservice:setup',
              'config-py3oservice = py3o.renderserver.service:config',
              'setup-py3oservice = py3o.renderserver.service:setup',
              ],
          ),
      test_suite = 'nose.collector',
      )
