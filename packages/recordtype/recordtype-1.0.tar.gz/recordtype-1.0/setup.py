from distutils.core import setup, Command

# run our tests
class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'recordtype.py'])
        raise SystemExit(errno)


setup(name='recordtype',
      version='1.0',
      url='http://www.trueblade.com/recordtype',
      author='Eric V. Smith',
      author_email='eric@trueblade.com',
      description='Similar to namedtuple, but instances are mutable.',
      long_description=open('README.txt').read() + open('CHANGES.txt').read(),
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   ],
      license='LICENSE.txt',
      py_modules=['recordtype'],

      cmdclass = {'test': PyTest},
      )
