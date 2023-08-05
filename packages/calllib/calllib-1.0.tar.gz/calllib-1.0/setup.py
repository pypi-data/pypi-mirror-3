from distutils.core import setup

setup(name='calllib',
      version='1.0',
      url='https://bitbucket.org/ericvsmith/calllib',
      author='Eric V. Smith',
      author_email='eric@trueblade.com',
      description='A library to call Python functions with parameters declared at runtime.',
      long_description=open('README.txt').read() + '\n' + open('CHANGES.txt').read(),
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   ],
      license='Apache License Version 2.0',
      py_modules=['calllib']
      )
