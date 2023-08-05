from distutils.core import setup

version = __import__("auspost").__version__

setup(
    name = 'python-auspost',
    version = version.replace(' ', '-'),
    url = 'http://bitbucket.org/goodtune/python-auspost',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = "Client for Australia Post's Postage Assessment Calculation (PAC) " \
        "and Postcode Search (PCS) service",
    install_requires = ['anyjson', 'httplib2'],
    packages = ['auspost'],
)
