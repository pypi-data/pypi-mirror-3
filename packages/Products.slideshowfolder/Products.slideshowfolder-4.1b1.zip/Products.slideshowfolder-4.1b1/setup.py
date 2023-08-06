from setuptools import setup, find_packages
import os

version = '4.1b1'

setup(name='Products.slideshowfolder',
      version=version,
      description="Slideshow Folder provides a simple, elegant animated slideshow for Plone.",
      long_description=open(os.path.join('Products', 'slideshowfolder', 'README.txt')).read() + "\n" +
                       open(os.path.join('Products', 'slideshowfolder', 'CHANGES.txt')).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone slideshow album mootools javascript',
      author='Johnpaul Burbank, Jon Baldivieso, David Glick, et al',
      author_email='davidglick@onenw.org',
      url='http://plone.org/products/slideshowfolder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
