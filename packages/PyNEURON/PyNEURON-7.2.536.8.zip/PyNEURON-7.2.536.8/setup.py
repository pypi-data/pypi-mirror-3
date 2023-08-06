#!/usr/bin/env python

import sys
import os
import glob
import platform
from distutils.core import setup

if os.name != 'nt':
    sys.exit("Only Windows OS is currently supported by PyNEURON")

arch=platform.architecture()[0]
if arch == '32bit':
    binaries = ["Win32/hoc.pyd", "Win32/nrniv.dll"]
elif arch == '64bit':
    binaries = ["Win64/hoc.pyd", "Win64/nrniv.dll", "Win64/pthreadGC2.dll", "Win64/IEShims.dll"]
else:
    sys.exit("Unsupported architecture: " + arch)
    
setup(name="PyNEURON",
      version="7.2.536.8", # NEURON 7.2 revision 536
      packages=["neuron", "neuron.tests", "neuron.neuroml"],
      package_dir={"neuron": "python/neuron"},
      data_files=[("neuronhome/bin", binaries),
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
