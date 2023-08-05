from distutils.core import setup

version = __import__("paydirt").__version__

setup(
    name = 'paydirt',
    version = version.replace(' ', '-'),
    url = 'http://bitbucket.org/goodtune/paydirt',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = 'Client for the Ctel "Payments Direct" credit card gateway.',
    install_requires = ['suds'],
    packages = ['paydirt'],
)
