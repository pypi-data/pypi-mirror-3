import os
import sys
from setuptools import setup, find_packages


DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
CONTRIBS = os.path.join(DOCS, 'CONTRIBUTORS.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.1.0'
long_description = open(README).read() + '\n\n' + \
                   open(CONTRIBS).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'unittest2',
    'Cheetah',
    'PasteScript',
    'templer.core'],

setup(name='templer.ztfy',
      version=version,
      description="ZTFY templates for templer",
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Zope3",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Code Generators",
       ],
      keywords='ztfy web zope command-line skeleton project',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://www.ztfy.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['templer'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      install_requires=[
          'setuptools',
          'templer.core'
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points="""
        [paste.paster_create_template]
        ztfy_package = templer.ztfy:ZTFYPackage
        """,
      )
