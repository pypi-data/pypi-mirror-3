from setuptools import setup, find_packages
import os
import sys

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

extra = {}
requirements = [ 'distribute', 'docutils', 'httplib2' ],
tests_require = ['nose', 'Mock', 'coverage', 'unittest2']

# In case we use python3
if sys.version_info >= (3,):
    extra['use_2to3'] = True

if sys.version_info <= (2,6):
    requirements.append('simplejson')

setup(
    name = "libthirty",
    version = "0.3",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False, # Don't create egg files, Django cannot find templates in egg files.
    install_requires = requirements,

    tests_require=tests_require,
    setup_requires='nose',
    test_suite = "nose.collector",
    extras_require={'test': tests_require},

    author = "Christo Buschek",
    author_email = "crito@30loops.net",
    url = "https://github.com/30loops/libthirty",
    description = "libthirty provides a python api to access the 30loops platform.",
    long_description = read('README.rst'),
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    **extra
)
