from distutils.core import setup, Extension

fsdir_mod = Extension('fsdir', sources = ['src/fsdir.c'])

setup (name = 'fsdir',
       version = '0.7',
       description = 'File System Scan',
       author="Rui Gomes",
       author_email="rui.tech@gmail.com",
       ext_modules=[fsdir_mod])
