import os
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import blazeform
version = blazeform.VERSION

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

setup(
    name = "BlazeForm",
    version = version,
    description = "A library for generating and validating HTML forms",
    long_description=README + '\n\n' + CHANGELOG,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/BlazeForm',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP'
      ],
    license='BSD',
    packages=['blazeform'],
    install_requires = [
        "FormEncode>=1.2.2",
        "BlazeUtils>=0.3.0",
        "WebHelpers>=1.0"
    ],
    test_suite='nose.collector',
    # tests will issue warning if run without pydns, but only one test uses it
    tests_require=['nose', 'pydns'],
    zip_safe=False
)
