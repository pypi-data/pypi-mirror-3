from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      install_requires=[
        "setuptools", # make "builtout" happy
        'dm.reuse',
      ],
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=True,
      entry_points = {
        'console_scripts' : [
           'dmzdoc = dm.zdoc:cli',
           ]
      },
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zdoc')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zdoc',
      version=pread('VERSION.txt').split('\n')[0].rstrip(),
      description='pydoc based documentation for Zope',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Zope2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      packages=['dm', 'dm.zdoc',],
      keywords='pydoc documentation Zope',
      license='BSD (see "dm/zdoc/LICENSE.txt", for details)',
      **setupArgs
      )
