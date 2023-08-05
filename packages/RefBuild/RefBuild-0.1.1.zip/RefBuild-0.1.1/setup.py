#!/usr/bin/env python
from distutils.core import setup
      
setup(
    name = "RefBuild",
    version = "0.1.1",
    package_dir={'refbuild': 'src'},
    packages = ['refbuild'],
    scripts= ['src/buildref'],
    author = "Thomas S. McTavish",
    author_email = "Tom.McTavish@gmail.com",
    description = "A tool to automatically build reference documentation from sources.",
      long_description = """A tool to construct reStructuredText files from docstrings
          in Python source files for automatically building reference documentation
          from the source.""",
    license = "MIT License",
    keywords = "API reference source documentation generation",
    url = "http://bitbucket.org/tommctavish/refbuilder",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Environment :: Web Environment',
                   'License :: Other/Proprietary License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
    requires = ['Sphinx (>=1.0)']
)

