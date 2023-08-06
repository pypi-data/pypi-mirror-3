from distutils.core import setup

setup(
    name='PADS',
    version='0.0.20120509',
    author='David Eppstein',
    maintainer='Tim Pederick',
    author_email='pederick@gmail.com',
    packages=['pads'],
    url='http://pypi.python.org/pypi/PADS/',
    description='Python Algorithms and Data Structures',
    classifiers=['Intended Audience :: Developers',
                 'License :: Public Domain',
                 'Programming Language :: Python',
                 'Topic :: Software Development'],
    long_description=open('README.txt').read(),
)

