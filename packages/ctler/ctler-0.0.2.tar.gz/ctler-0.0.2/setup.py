RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.0.2'

setup(
        name='ctler',
        version=version,
        description="GrADS CTL reader.",
        long_description="""\
This is an initial module for reading CTL files from GrADS. Right now
the module targets output from CPTEC's atmospheric model only.
""",
        classifiers=filter(None, classifiers.split("\n")),
        keywords='grads ctl data array math',
        author='Roberto De Almeida',
        author_email='roberto@dealmeida.net',
        url='http://bitbucket.org/robertodealmeida/ctler/',
        download_url = "http://cheeseshop.python.org/packages/source/p/ctler/ctler-%s.tar.gz" % version,
        license='MIT',
        py_modules=['ctler'],
        include_package_data=True,
        zip_safe=True,
        test_suite = 'nose.collector',
        install_requires=[
            'numpy',
        ],
        extras_require={
            'test': ['nose'],
        },
)
