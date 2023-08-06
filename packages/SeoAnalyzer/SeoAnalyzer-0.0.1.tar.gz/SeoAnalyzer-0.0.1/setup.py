import sys
from setuptools import setup, find_packages

version = '0.0.1'

if not '2.5' <= sys.version < '3.0':
    raise ImportError('Python version not supported')

tests_require = ['nose']

setup(name="SeoAnalyzer",
      version=version,
      install_requires=['lxml >= 2.2.8', 'zope.schema >= 3.7.0'],
      
      description="SEO Analysis Package",
      long_description="""\
Series of modules useful for looking at SEO effectiveness of a webpage

It has a `mercurial repository
<https://ixmatus@bitbucket.org/whoosh/seo-analyzer>`_ that
you can install from with ``easy_install paypy``

""",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Brian Bigelow",
      author_email="brianb@whooshtraffic.com",
      url="http://bitbucket.org/whoosh/seo-analyzer",
      license="PSF",
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require
      )
