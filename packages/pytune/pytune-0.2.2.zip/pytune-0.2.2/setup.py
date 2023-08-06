import versiontools_support

from setuptools import setup, find_packages
import sys, os

#from pytune import __version__

setup(name='pytune',
		version=':versiontools:pytune:VERSION',
#	version = __version__,
      description="A tool for Python program performence tuning.",
      long_description="""\
VisualPyTune is a python program performance tuning tool, based on wxPython. It can show you a callgraph(doing), stats report, callees, callers, and caky charts. finaly, you can remove inessential information very easy.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='profile, performence',
      author='laiyonghao',
      author_email='mail@laiyonghao.com',
      url='http://code.google.com/p/visualpytune/',
      license='apache license 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      setup_requires = [
      	'versiontools >= 1.8',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      pytune = pytune.vpt:main
      """,
      )
