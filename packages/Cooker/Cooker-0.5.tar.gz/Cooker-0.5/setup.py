import os
from distutils.core import setup

base_dir = os.path.expanduser('~/.cooker')
templates_dir = base_dir + '/templates'

setup(name='Cooker',
    version='0.5',
    description='Python CodeChef Utilities',
    long_description=open('README.txt').read(),
    author='Nayan Shah',
    author_email='nayan@nayanshah.com',
    url='http://pypi.python.org/pypi/Cooker/',
    license='LICENSE.txt',
    packages=['cooker', 'cooker.tests'],
    data_files=[('/etc/cooker/templates', ['templates/template.c',
            'templates/template.cpp', 'templates/template.java']),
                ('/etc/cooker', ['templates/config.cfg'])],
    scripts=['scripts/cook'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Environment :: Web Environment',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: Python Software Foundation License',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Utilities',
        ],
     )
