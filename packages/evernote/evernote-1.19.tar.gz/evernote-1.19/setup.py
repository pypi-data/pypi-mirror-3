import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'evernote',
    version = '1.19',
    author = 'Evernote Corporation',
    author_email = 'en-support@evernote.com',
    maintainer = 'Jacob Kaplan-Moss',
    maintainer_email = 'jacob@jacobian.org',
    url = 'http://www.evernote.com/about/developer/api/',
    description = 'Python bindings to the Evernote API.',
    long_description = read('README.txt'),
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries',
    ],
    license = 'BSD',
)