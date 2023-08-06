import os
from distutils.core import setup

files = map(lambda name: 'templates/' + name, os.listdir('templates'))

setup(name='Cooker',
    version='1.0',
    description='Python CodeChef Utilities',
    long_description=open('README.txt').read(),
    author='Nayan Shah',
    author_email='nayan@nayanshah.com',
    url='http://pypi.python.org/pypi/Cooker/',
    license='LICENSE.txt',
    packages=['cooker'],
    data_files=[('/etc/cooker/templates', files),
                ('/etc/cooker', ['config/config.cfg'])],
    scripts=['scripts/cook'],
    classifiers=[
      'Development Status :: 4 - Beta',
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
