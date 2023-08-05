from setuptools import setup, find_packages
import sys, os

version = '1.2'

setup(name='ConfigObject',
      version=version,
      description="""ConfigObject is a wrapper to the python ConfigParser to
      allow to access sections/options with attribute names.""",
      long_description="""\
""",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
      ],
      keywords='configuration config',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org/docs/ConfigObject/index.html',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
