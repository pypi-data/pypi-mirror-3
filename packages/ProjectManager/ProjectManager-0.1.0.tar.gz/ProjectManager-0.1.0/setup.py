from distutils.core import setup

setup(
    name='ProjectManager',
    version='0.1.0',
    author='Trent Hauck',
    author_email='trent@trenthauck.com',
    packages=['projectmanager'],
    scripts=[],
    url='http://pypi.python.org/pypi/ProjectManager/',
    license='LICENSE.txt',
    description='Project management for data analysis projects.',
    #install_requires=[],
    long_description=open('README').read()
)
