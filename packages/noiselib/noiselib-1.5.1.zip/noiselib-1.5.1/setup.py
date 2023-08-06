from distutils.core import setup, Extension

setup(name = 'noiselib',
      version = '1.5.1',
      description = 'noise for Python',
      long_description =
"""
noiselib provides noise generators and manipulators.  noiselib is modeled after
libnoise, the C++ coherent noise library.  noise generators are wrapped in
'modules' that manipulate, modify, filter, and combine noise generators.  Each
module expects and returns noise; thus modules can be stacked to create complex
noise output.
""",
      author = 'Chandler Armstrong',
      author_email = 'omni.armstrong@gmail.com',
      url = 'http://code.google.com/p/noiselib/',
      download_url = 'http://code.google.com/p/noiselib/downloads/list',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Topic :: Multimedia :: Graphics',
          'License :: OSI Approved :: GNU General Public License (GPL)'],
      packages = ['noiselib', 'noiselib.modules'],
      provides = ['noiselib'],
      ext_modules = [ Extension( 'noiselib._simplex', ['noiselib/_simplex.c'] ) ]
      )
