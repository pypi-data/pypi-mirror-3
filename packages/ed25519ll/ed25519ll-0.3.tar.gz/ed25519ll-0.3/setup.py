import os
import sys
import glob
# import ed25519ll

from setuptools import setup, find_packages
from distutils.core import Extension
from distutils.util import get_platform

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

plat_name = get_platform().replace('-', '_')

setup(name='ed25519ll',
      version='0.3',
      description='A low-level cffi wrapper for Ed25519 digital signatures.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://bitbucket.org/dholth/ed25519ll/',
      keywords='ed25519',
      license='MIT',
      packages=['ed25519ll'],
      include_package_data=True,
      zip_safe=False,
      setup_requires = ['cffi'],
      install_requires = ['cffi'],
      tests_require = ['nose'],
      test_suite = 'nose.collector',
      ext_modules=[
                   # ed25519ll._ed25519.ffi.verifier.get_extension(),
                   Extension('ed25519ll._ed25519_%s' % plat_name,
                             sources=glob.glob('ed25519-supercop-ref10/*.c'),
                             include_dirs = ['ed25519-supercop-ref10',],
                             export_symbols=["crypto_sign",
                                             "crypto_sign_open",
                                             "crypto_sign_keypair"],),
                   ],
      )

