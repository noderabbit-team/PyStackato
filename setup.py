from setuptools import setup
import stackato

requirements = ['setuptools', 'requests>=0.10.1']

setup(
    name='PyStackato',
    version=stackato.__version__,
    description=stackato.__doc__.strip(),
    author=stackato.__author__,
    license=stackato.__license__,
    packages=['stackato'],
    install_requires=requirements
)
