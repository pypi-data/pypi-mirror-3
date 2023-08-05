#from distribute_setup import use_setuptools
#use_setuptools()

from setuptools import setup


setup(
    name='restful_client',
    version='0.1',
    author='Benjamin Scherrey',
    author_email='scherrey@proteus-tech.com',
    packages=['restful_client'],
    url='',
    license='See LICENSE.txt',
    description='An asynchronous RESTful client library.',
    long_description=open('README.txt').read(),
    install_requires = [  'futures==2.1.2',
                          'unittest2==0.5.1',
                          'mock==0.7.2'
                       ]
)
