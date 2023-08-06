from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
setup(
    name='pyurfa',
    version='0.0.1',
    description='Python api for UTM5 Billing',
    author='Ilia Gavrilin',
    author_email='gavrilin.ilia@gmail.com',
    url='http://bitbucket.org/chubi/pyurfa',
    keywords = "netup utm5 api",
    install_requires=[''],
    license='BSD',
    packages=['pyurfa'],
    long_description=read('README'),
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
)
