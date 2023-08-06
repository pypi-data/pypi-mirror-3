from distutils.core import setup

setup(
    name="ChordFinder",
    version="0.1",
    author="Anthony Reid",
    author_email="AnthonyReid99@gmail.com",
    packages=['chordfinder'],
    url="http://pypi.python.org/pypi/ChordFinder/",
    license='LICENSE.txt',
    description='A simple GUI chord finder',
    long_description=open('README.txt').read(),
    install_requires=[
	"wx >= 2.6.4"
    ],
)
