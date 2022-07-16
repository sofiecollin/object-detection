from distutils.core import setup
from Cython.Build import cythonize

setup(name='Hello world app',
      ext_modules=cythonize("gaussian_mix.pyx"))

import gaussian_mix