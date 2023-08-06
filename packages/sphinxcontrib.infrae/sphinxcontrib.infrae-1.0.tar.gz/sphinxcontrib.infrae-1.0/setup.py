from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='sphinxcontrib.infrae',
      version=version,
      description="Add-ons to sphinx to document Zope event and interfaces (and buildout configuration).",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='sphinx color buildout zope interface',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['sphinxcontrib'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Pygments',
        'Sphinx >= 1.0',
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.schema',
        ],
      )
