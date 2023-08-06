from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      install_requires=[
        'setuptools', # to make "buildout" happy
      # required but apparently difficult to install via "easy_install"
      # "easy_install pyxb" would install "PyXB-full" which would work
      #  but contains huge data we do not need
        #'PyXB-base',
      ] ,
      namespace_packages=['dm', 'dm.xmlsec',
                          ],
      zip_safe=False,
      entry_points = dict(
        ),
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'xmlsec', 'pyxb')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()


setup(name='dm.xmlsec.pyxb',
      version=pread('VERSION.txt').split('\n')[0],
      description="Tiny wrapper around the 'wssplat' bundle of 'pyxb' for XML-Signature and XML-Encryption (likely of limited general interest)",
      long_description=pread('README.txt'),
      classifiers=[
        #'Development Status :: 3 - Alpha',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.6',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.xmlsec.pyxb',
      packages=['dm', 'dm.xmlsec', 'dm.xmlsec.pyxb'],
      license='BSD',
      keywords='pyxb xml security digital signature',
      **setupArgs
      )
