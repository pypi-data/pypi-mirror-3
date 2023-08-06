from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='bethel.clustermgmt',
      version=version,
      description="Zope Cluster Management facilities",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: System :: Monitoring"
        ],
      keywords='python zope infrae varnish fabric',
      author='Andy Altepeter',
      author_email='aaltepet@bethel.edu',
      url='http://pypi.python.org/pypi/bethel.clustermgmt',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['bethel'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=[
        'setuptools_hg',
        ],
      install_requires=[
          'setuptools',
          'infrae.rest',
          'zeam.form.base',
          'zeam.form.silva',
          'five.grok',
          'zExceptions',
          'silva.core.conf',
          'silva.core.services',
          'Products.Silva'
      ],
      )
