from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = \
  [
    Extension(
    'streaming',       # name of extension
    ['streaming.pyx'], # filename of our Pyrex/Cython source
    language='c++',    # this causes Pyrex/Cython to create C++ source
    ),
    Extension(
    'fileutils',       # name of extension
    ['fileutils.pyx'], # filename of our Pyrex/Cython source
    language='c++',    # this causes Pyrex/Cython to create C++ source
    ),
  ]
)