from distutils.core import setup

setup(name='recordtype',
      version='0.1',
      url='http://www.trueblade.com/recordtype',
      author='Eric V. Smith',
      author_email='eric@trueblade.com',
      description='Similar to namedtuple, but instances are mutable.',
      long_description=open('README.txt').read() + open('CHANGES.txt').read(),
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   ],
      license='LICENSE.txt',
      py_modules=['recordtype'],
      )
