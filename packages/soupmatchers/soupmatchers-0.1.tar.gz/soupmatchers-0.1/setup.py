from setuptools import setup
from textwrap import dedent


setup(
    name='soupmatchers',
    version='0.1',
    description='Matchers for checking parts of a HTML parse tree',
    url='http://launchpad.net/soupmatchers',
    license='Eclipse Public License',
    packages=['soupmatchers',],
    long_description=dedent('''
        This module allows your testing to be more robust against textual
        changes by working against the parse tree provided by BeautifulSoup.
        It provides a powerful language for matching parts of the HTML, giving
        you endless possibilities for testing. It does this while fitting in
        to your TestCase hierarchy because it makes use of testtools
        Matchers.'''),
    setup_requires=['setuptools'],
    install_requires=['testtools>0.9.3', 'BeautifulSoup'],
    )
