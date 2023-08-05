#!/usr/bin/env python
from distutils.core import setup
      
setup(
    name = "RefBuild",
    version = "0.1.3",
    package_dir={'refbuild': 'src'},
    packages = ['refbuild'],
    scripts= ['src/buildref'],
    author = "Thomas S. McTavish",
    author_email = "Tom.McTavish@gmail.com",
    description = "A tool to prepare source reference from docstrings.",
      long_description = """A tool to construct reStructuredText files from docstrings in Python source files and link to Sphinx autodoc functionality to build API/source reference documentation.""",
    license = "MIT License",
    keywords = "API reference source documentation generation",
    url = "http://bitbucket.org/tommctavish/refbuild",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Documentation'],
    requires = ['Sphinx (>=1.0)']
)

