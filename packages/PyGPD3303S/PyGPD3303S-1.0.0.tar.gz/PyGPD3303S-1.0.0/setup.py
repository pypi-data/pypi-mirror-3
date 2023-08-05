from distutils.core import setup
import gpd3303s

setup(name='PyGPD3303S',
      version='1.0.0',
      description='Python Interface for DC power supply GPD-3303S',
      author='Akira Okumura',
      author_email='oxon@mac.com',
      license='BSD License',
      platforms=['MacOS :: MacOS X', 'POSIX', 'Windows'],
      url='https://sourceforge.net/p/pygpd3303s/',
      py_modules=['gpd3303s'],
      install_requires=['serial'],
      classifiers=['Topic :: Terminals :: Serial',
                   'Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   ],
      long_description=gpd3303s.__doc__
      )
