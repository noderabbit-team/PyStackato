from setuptools import setup
import stackato

requirements = ['setuptools', 'requests>=0.11.2']

version = '0.10.4.1dev'

setup(
    name='PyStackato',
    version=version,
    description=stackato.__doc__.strip(),
    author=stackato.__author__,
    license=stackato.__license__,
    packages=['stackato'],
    install_requires=requirements
)








