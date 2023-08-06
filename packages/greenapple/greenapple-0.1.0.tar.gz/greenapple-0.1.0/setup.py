from distutils.core import setup

setup(
    name='greenapple',
    version='0.1.0',
    author='Acellam Guy',
    author_email='abiccel@yahoo.com',
    packages=['greenapple','greenapple.model'],    
    url='http://pypi.python.org/pypi/greenapple/',
    license='LICENSE.txt',
    description='Useful DB Layer Package for MySQL,PSQL & Oracle.',
    long_description=open('README.txt').read(),
    #install_requires=[
    #    "Django >= 1.1.1",
    #    "caldav == 0.1.4",
    #],
)
