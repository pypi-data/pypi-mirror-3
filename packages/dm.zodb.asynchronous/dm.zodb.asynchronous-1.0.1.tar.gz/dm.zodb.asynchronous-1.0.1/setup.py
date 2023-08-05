from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      install_requires=[
        "decorator",
        "dm.transaction.aborthook",
      ] ,
      namespace_packages=['dm', 'dm.zodb'],
      zip_safe=False,
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zodb', 'asynchronous')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zodb.asynchronous',
      version=pread('VERSION.txt').split('\n')[0],
      description="Utilities to implement asynchronous operations accessing the ZODB",
      long_description=pread('README.txt'),
      classifiers=[
        #'Development Status :: 3 - Alpha',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Framework :: ZODB',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.zodb.asynchronous',
      packages=['dm', 'dm.zodb', 'dm.zodb.asynchronous'],
      keywords='ZODB thread asynchronous utilities',
      license='BSD',
      **setupArgs
      )
