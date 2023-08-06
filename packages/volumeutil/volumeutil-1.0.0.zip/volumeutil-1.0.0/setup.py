#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from distutils.core import setup
try:
    from cx_Freeze import setup, Executable
except ImportError:
    Executable = lambda *a, **k: None
import volumeutil


if __name__ == '__main__':
    target = volumeutil
    setup(
        name=target.__name__,
        version=target.__version__,
        description=target.__doc__.splitlines()[0],
        long_description=target.__doc__,
        author=target.__author__,
        author_email=target.__author_email__,
        url=target.__url__,
        classifiers=target.__classifiers__,
        license=target.__license__,
        py_modules=[target.__name__, ],
        executables=[Executable(target.__file__)],
        )


