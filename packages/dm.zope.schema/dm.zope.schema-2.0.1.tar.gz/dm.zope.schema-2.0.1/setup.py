from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      install_requires=['zope.schema', "dm.reuse",] ,
      namespace_packages=['dm', 'dm.zope'],
      zip_safe=False,
      test_suite='dm.zope.schema.tests.testsuite',
      test_requires=['zope.schema'],
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zope', 'schema')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zope.schema',
      version=pread('VERSION.txt').split('\n')[0],
      description="'zope.schema' extensions",
      long_description=pread('README.txt'),
      classifiers=[
#        'Development Status :: 3 - Alpha',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.zope.schema',
      packages=['dm', 'dm.zope', 'dm.zope.schema'],
      keywords='application development zope schema',
      license='ZPL',
      **setupArgs
      )
