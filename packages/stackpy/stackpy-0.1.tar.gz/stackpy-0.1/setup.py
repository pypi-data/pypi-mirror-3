# In order to support Python 3.x, we use 'build_py_2to3' if we are running on Py3k
try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

from distutils.core import setup

setup(name='stackpy',
      version='0.1',
      description='Python bindings for the Stack Exchange API.',
      author='Nathan Osman',
      author_email='admin@quickmediasolutions.com',
      url='https://launchpad.net/stackpy',
      license='MIT',
      packages=['stackpy'],
      cmdclass = {'build_py': build_py,})