import re
from distutils.core import setup

def pep386(v):
    regex = re.compile(r' (?:([ab])\w+) (\d+)$')
    if regex.search(v):
        base = regex.sub('', v)
        minor = ''.join(regex.search(v).groups())
        return base + minor
    return v

version = __import__("paydirt").__version__

setup(
    name = 'paydirt',
    version = pep386(version),
    url = 'http://bitbucket.org/goodtune/paydirt',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = 'Client for the Ctel "Payments Direct" credit card gateway.',
    install_requires = ['suds'],
    packages = ['paydirt'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'Topic :: Software Development :: Libraries',
   ],
)
