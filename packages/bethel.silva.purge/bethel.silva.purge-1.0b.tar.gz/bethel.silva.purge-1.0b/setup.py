from setuptools import setup, find_packages
import os

version = '1.0b'

setup(name='bethel.silva.purge',
      version=version,
      description="Send HTTP PURGE to caching servers on content publishing events",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='silva varnish cache purge',
      author='Andy Altepeter',
      author_email='aaltepet@bethel.edu',
      url='http://pypi.python.org/pypi/bethel.silva.purge',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['bethel', 'bethel.silva'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=["setuptools_hg"],
      install_requires=[
          'setuptools',
          'five.grok',
          'zope.component',
          'zope.interface',
          'zeam.form.base',
          'zeam.form.ztk',
          'zeam.form.silva',
          'silva.core.conf',
          'silva.core.interfaces',
          'silva.core.services',
          'silva.core.views',
          'plone.cachepurging',
          'plone.registry',
          'zope.annotation'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
