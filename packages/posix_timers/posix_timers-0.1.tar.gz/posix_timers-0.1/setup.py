from distutils.core import setup, Extension

setup(name='posix_timers',
    description='Provides access to posix timers (clock_gettime etc.) from Python.',
    version='0.1',
    author="Torsten Landschoff",
    author_email="t.landschoff@gmx.net",
    url="http://bitbucket.org/bluehorn/posix_timers",
    ext_modules=[ Extension('posix_timers', ['src/posix_timers.c'], libraries=["rt"]) ],
    license='MIT License',
)
