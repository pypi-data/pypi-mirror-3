
from distutils.core import setup

setup(name='Cooker',
    version='0.2',
    description='Python CodeChef Utilities',
    long_description=open('README.txt').read(),
    author='Nayan Shah',
    author_email='nayan@nayanshah.com',
    url='http://pypi.python.org/pypi/Cooker/',
    license='LICENSE.txt',
    packages=['cooker', 'cooker.tests'],
    data_files=[('/etc/cooker/templates', ['templates/template.cpp', 'templates/template.c']),
                ('/bin', ['bin/cook'])],
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
