from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      install_requires=['dm.profile'],
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False, # to let the tests work
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'Products', 'ZopeProfiler')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='Products.ZopeProfiler',
      version=pread('version.txt').split('\n')[0],
      description='Zope 2 profiler to learn what Zope spends it time on. For Zope 2.10-2.13',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://www.dieter.handshake.de/pyprojects/zope',
      packages=['Products', 'Products.ZopeProfiler'],
      keywords='Zope 2, profiling, time, analysis, caller, callee',
      license='BSD (see "Products/ZopeProfiler/LICENSE.txt", for details)',
      **setupArgs
      )



