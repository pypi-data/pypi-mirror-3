#!/usr/bin/env python

import sys
import glob
from distutils.core import setup

# A solution from https://bbs.archlinux.org/viewtopic.php?id=98017
# to located the package data files after installation
import re
from os.path import *
from distutils.core import Command
from distutils.command.build_py import build_py

class package_ini(Command):
    """
        Locate 'package.ini' in all installed packages and patch it as requested
        by wildcard references to install process.
    """
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def visit(self, dirname, names):
        packages = self.distribution.get_command_obj(build_py.__name__).packages
        if basename(dirname) in packages:
            if 'package.ini' in names:
                self.patch(join(dirname, 'package.ini'))

    def patch(self, ini_file):
        print 'patching file' + ini_file
        with open(ini_file,'r') as infile:
            file_data = infile.readlines()
        with open(ini_file,'w') as outfile:
            for line in file_data:
                _line = self.patch_line(line)
                if _line:
                    line = _line
                outfile.write(line)

    def patch_line(self, line):
        """
            Patch an installed package.ini with setup's variables
        """
        match = re.match('(?P<identifier>\w+)\s*=.*##SETUP_PATCH\\((?P<command>.*)\.(?P<variable>.*)\\)', line)
        if not match:
            return line 
        print 'Replacing:'+line 
        line = match.group('identifier')
        line += ' = '
        data = '(self).distribution.get_command_obj(\''+\
                match.group('command')+'\')'+'.'+\
                match.group('variable')
        data = eval(data)
        data = data.replace('\\', '\\\\')
        line += '\''+data+'\'\n'
        print 'With:' + line
        return line

    """
        Patch package.ini files in distribution package with variables from setup
    """
    def run(self):
        walk(
            self.distribution.get_command_obj(install.__name__).install_lib,
            package_ini.visit,
            self
        )
        pass

from distutils.command.install import install as _install
class install(_install):
    sub_commands = _install.sub_commands + [
           (package_ini.__name__, None)
        ]

from distutils.command.build import build as _build
from distutils.command.install_data import install_data as _install_data
from distutils.command.install_lib import install_lib as _install_lib
from distutils.command.install import install as _install
setup(cmdclass={_build.__name__: _build,
              _install_data.__name__: _install_data,
              _install_lib.__name__: _install_lib,
              install.__name__: install,
              package_ini.__name__: package_ini 
             },
      name="PyNEURON",
      version="7.2.536.3", # NEURON 7.2 revision 536
      packages=["neuron", "neuron.tests", "neuron.neuroml"],
      package_dir={"neuron": "python/neuron"},
      package_data={"neuron": ["package.ini"]},
      data_files=[("neuronhome/bin", ["Win32/hoc.pyd", "Win32/nrniv.dll"]),
                  ("neuronhome/lib/hoc", glob.glob("home/hoc/*.hoc")),
                  ("neuronhome/lib/hoc/celbild", glob.glob("home/hoc/celbild/*.hoc")),
                  ("neuronhome/lib/hoc/chanbild", glob.glob("home/hoc/chanbild/*.hoc")),
                  ("neuronhome/lib/hoc/import3d", glob.glob("home/hoc/import3d/*.hoc")),
                  ("neuronhome/lib/hoc/lincir", glob.glob("home/hoc/lincir/*.hoc")),
                  ("neuronhome/lib/hoc/mulfit", glob.glob("home/hoc/mulfit/*.hoc")),
                  ("neuronhome/lib/hoc/mview", glob.glob("home/hoc/mview/*.hoc")),
                  ("neuronhome/lib/hoc/netbild", glob.glob("home/hoc/netbild/*.hoc")),
                  ],
      #TODO: additional data files, from NEURONHOME
      #TODO: we need to set the NEURONHOME environment variable
      author="Uri Cohen",
      author_email="uri.cohen@alice.nc.huji.ac.il",
      url="https://bitbucket.org/uric/pyneuron/",
      description="A Python package version of NEURON, for empirically-based simulations of neurons and networks of neurons",
      long_description="""A Python package version of NEURON,
Yale's project "for empirically-based simulations of neurons and networks of neurons"
See http://www.neuron.yale.edu/neuron/""",
      download_url="https://bitbucket.org/uric/pyneuron/downloads/PyNEURON_7.2.zip", # TODO
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Environment :: Win32 (MS Windows)",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License (GPL)", # Like NEURON,
          "Operating System :: Microsoft :: Windows",
          #"Operating System :: POSIX",
          #"Operating System :: MacOS",
          #"Operating System :: OS Independent",
          "Programming Language :: C",
          "Programming Language :: Python :: 2",
          "Topic :: Scientific/Engineering",
          ]
      )
