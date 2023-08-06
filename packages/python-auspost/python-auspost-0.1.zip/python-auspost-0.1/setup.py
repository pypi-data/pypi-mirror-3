import re
from distutils.core import setup

def pep386(v):
    regex = re.compile(r' (?:([ab])\w+) (\d+)$')
    if regex.search(v):
        base = regex.sub('', v)
        minor = ''.join(regex.search(v).groups())
        return base + minor
    return v

version = __import__("auspost").__version__

setup(
    name = 'python-auspost',
    version = pep386(version),
    url = 'http://bitbucket.org/goodtune/python-auspost',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = "Client for Australia Post's Postage Assessment Calculation (PAC) " \
        "and Postcode Search (PCS) service",
    install_requires = ['anyjson', 'httplib2'],
    packages = ['auspost'],
)
