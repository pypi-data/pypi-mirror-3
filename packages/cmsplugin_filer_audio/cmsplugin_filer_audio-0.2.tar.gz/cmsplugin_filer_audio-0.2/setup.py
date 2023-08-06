from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='cmsplugin_filer_audio',
      version=version,
      description="MP3 player for Django CMS with flowplayer",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        ],
      keywords='',
      author='GISA Elkartea',
      author_email='kontaktua@gisa-elkartea.org',
      url='http://lagunak.gisa-elkartea.org/projects/cmsplugin_filer_audio',
      license='GPL3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'distribute',
          'z3c.setuptools_mercurial',
          # -*- Extra requirements: -*-
          'django-cms',
          'django-filer',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
