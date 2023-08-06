#!/usr/bin/env python
#-*- coding: utf-8 -*-

from distutils.core import setup, Extension
import sys, os

## patch distutils for added setup keywords for Python versions < 2.2.3...
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

## enable 'build_sphinx' command if Sphinx is installed...
cmdclass = {}
try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    import warnings
    warnings.formatwarning = lambda *a: ' ** WARNING: %s\n' % a[0]
    msg = "no Sphinx install found, 'build_sphinx' command disabled."
    warnings.warn(msg, RuntimeWarning)

def choose_pam_sm(*roots, **kws):
    import os
    names = kws.get('names', ['login', 'authorization', 'su'])
    prefixes = kws.get('prefixes', ['auth', 'login', 'su'])
    roots = roots or ['/etc/pam.d']
    sm = None
    for root in roots:
        try:
            services = os.listdir(root)
        except OSError:
            continue
        for name in names:
            if name in services:
                sm = name
                break
        if sm != None: break
        else:
            for service in services:
                for prefix in prefixes:
                    if service.startswith(prefix):
                        sm = service
                    if sm != None: break
            if sm != None: break
    
    return '"%s"' % sm
    

pyapi2 = Extension(name='draxoft.auth.pam',
                   sources=['src/draxoft/auth/pam.c'],
                   libraries=['pam'],
                   define_macros=[('DEFAULT_SERVICE', choose_pam_sm())],
                   extra_compile_args=['-std=c99', '-pedantic', '-Wall',
                                       '-Wextra',
                                       '-Wno-unknown-pragmas',
                                       '-Wno-unused-parameter',
                                       '-Wno-unused-variable'])

setup(name='draxoft.auth.pam',
      version='0.1.2',
      author='Ryan Volpe',
      author_email='ryan@draxoft.com',
      description="Provides a Python-style interface to PAM's C API.",
      url='http://packages.python.org/draxoft.auth.pam/',
      download_url='',
      package_dir={'': 'src'},
      cmdclass=cmdclass,
      packages=['draxoft', 'draxoft.auth'],
      ext_modules=[pyapi2],
      license='LGPLv2',
      platforms=['POSIX', 'Linux', 'MacOS X'],
      classifiers=['Programming Language :: Python',
                   'Development Status :: 3 - Alpha',
                   'Operating System :: POSIX',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Unix',
                   'Topic :: Security',
                   'Topic :: System',
                   'Topic :: System :: Operating System',
                   'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)'],
      long_description=''''''
     )
