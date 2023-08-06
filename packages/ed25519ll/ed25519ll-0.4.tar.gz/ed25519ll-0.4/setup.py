import os
import sys
import glob

from setuptools import setup, find_packages
from distutils.core import Extension
from distutils.util import get_platform

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

plat_name = get_platform().replace('-', '_')

setup(name='ed25519ll',
      version='0.4',
      description='A low-level cffi wrapper for Ed25519 digital signatures.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Security :: Cryptography",
        ],
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://bitbucket.org/dholth/ed25519ll/',
      keywords='ed25519',
      license='MIT',
      packages=['ed25519ll'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=['cffi'],
      install_requires=['cffi'],
      tests_require=['nose'],
      test_suite='nose.collector',
      ext_modules=[
               Extension('ed25519ll._ed25519_%s' % plat_name,
                         sources=[
                             'ed25519-supercop-ref10/ge_frombytes.c',
                             'ed25519-supercop-ref10/fe_frombytes.c',
                             'ed25519-supercop-ref10/ge_tobytes.c',
                             'ed25519-supercop-ref10/fe_sq.c',
                             'ed25519-supercop-ref10/ge_scalarmult_base.c',
                             'ed25519-supercop-ref10/sc_reduce.c',
                             'ed25519-supercop-ref10/ge_p2_0.c',
                             'ed25519-supercop-ref10/ge_sub.c',
                             'ed25519-supercop-ref10/fe_sub.c',
                             'ed25519-supercop-ref10/ge_p2_dbl.c',
                             'ed25519-supercop-ref10/ge_double_scalarmult.c',
                             'ed25519-supercop-ref10/fe_0.c',
                             'ed25519-supercop-ref10/ge_p3_to_p2.c',
                             'ed25519-supercop-ref10/ge_precomp_0.c',
                             'ed25519-supercop-ref10/fe_cmov.c',
                             'ed25519-supercop-ref10/sc_muladd.c',
                             'ed25519-supercop-ref10/fe_isnegative.c',
                             'ed25519-supercop-ref10/ge_p3_dbl.c',
                             'ed25519-supercop-ref10/ge_add.c',
                             'ed25519-supercop-ref10/fe_neg.c',
                             'ed25519-supercop-ref10/ge_p3_0.c',
                             'ed25519-supercop-ref10/fe_1.c',
                             'ed25519-supercop-ref10/ge_madd.c',
                             'ed25519-supercop-ref10/fe_tobytes.c',
                             'ed25519-supercop-ref10/sign.c',
                             'ed25519-supercop-ref10/fe_copy.c',
                             'ed25519-supercop-ref10/ge_p1p1_to_p2.c',
                             'ed25519-supercop-ref10/fe_isnonzero.c',
                             'ed25519-supercop-ref10/open.c',
                             'ed25519-supercop-ref10/fe_sq2.c',
                             'ed25519-supercop-ref10/ge_msub.c',
                             'ed25519-supercop-ref10/fe_add.c',
                             'ed25519-supercop-ref10/fe_mul.c',
                             'ed25519-supercop-ref10/fe_pow22523.c',
                             'ed25519-supercop-ref10/fe_invert.c',
                             'ed25519-supercop-ref10/ge_p3_tobytes.c',
                             'ed25519-supercop-ref10/ge_p1p1_to_p3.c',
                             'ed25519-supercop-ref10/ge_p3_to_cached.c',
                             'ed25519-supercop-ref10/sha512-blocks.c',
                             'ed25519-supercop-ref10/sha512-hash.c',
                             'ed25519-supercop-ref10/verify.c',
                             'ed25519-supercop-ref10/keypair.c'],
                         include_dirs=['ed25519-supercop-ref10', ],
                         export_symbols=["crypto_sign",
                                         "crypto_sign_open",
                                         "crypto_sign_keypair"],
                         compile_extra=['-march=native']),
               ],
      )

