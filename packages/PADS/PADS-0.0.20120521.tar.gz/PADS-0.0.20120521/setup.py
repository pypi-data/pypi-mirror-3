from distutils.core import setup

setup(
    name='PADS',
    version='0.0.20120521',
    author='David Eppstein',
    author_email='eppstein@ics.uci.edu',
    maintainer='Tim Pederick',
    maintainer_email='pederick@gmail.com',
    packages=['pads'],
    url='http://pypi.python.org/pypi/PADS/',
    description='Python Algorithms and Data Structures',
    classifiers=['Intended Audience :: Developers',
                 'License :: Public Domain',
                 'Programming Language :: Python',
                 'Topic :: Software Development'],
    long_description=open('README.txt').read(),
)

