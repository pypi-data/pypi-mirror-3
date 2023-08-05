from distutils.core import setup

setup(
    name='mcint',
    author='Tristan Snowsill',
    description='''
    A simple tool to perform numerical integration using Monte Carlo techniques.
    ''',
    author_email='tristan.snowsill@googlemail.com',
    version='0.1dev1',
    py_modules=['mcint'],
    url='http://pypi.python.org/pypi/Monte Carlo integrator/',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
)
