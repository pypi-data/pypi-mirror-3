#!/usr/bin/env python

from distutils.core import setup

import sys
import ctypes
import os.path

# Determine if we're in 32 or 64 bits
if ctypes.sizeof(ctypes.c_void_p) == 4:
    folder = 'Win32'
else:
    folder = 'Win64'

# Set the parameters for the setup script
params = {

    # Setup instructions
    'provides'          : ['BeaEnginePython'],
    'py_modules'        : ['BeaEnginePython'],
    'data_files'        : [
                            (sys.exec_prefix,
                                [os.path.join(folder, 'BeaEngine.dll')]),
                        ],

    # Metadata
    'name'              : 'BeaEnginePython',
    'version'           : '3.1.0',
    'description'       : 'BeaEngine disassembler bindings for Python',
    'url'               : 'http://beatrix2004.free.fr/BeaEngine/index1.php',
    'download_url'      : 'http://beatrix2004.free.fr/BeaEngine/download1.php',
    'platforms'         : ['win32', 'win64'],
    'classifiers'       : [
                        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                        'Development Status :: 5 - Production/Stable',
                        'Programming Language :: Python :: 2.5',
                        'Programming Language :: Python :: 2.6',
                        'Programming Language :: Python :: 2.7',
                        'Topic :: Software Development :: Libraries',
                        ],
    }

# Execute the setup script
setup(**params)
