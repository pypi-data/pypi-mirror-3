from distutils.core import setup
from os import path 

description="mako template support for Django >=1.2"

fp = open(path.join(path.dirname(path.realpath(__file__)), 'README.txt'))
long_description = fp.read()

VERSION='0.4'

setup(author="Jacob Smullyan",
      author_email='smulloni@smullyan.org',
      description=description,
      long_description=long_description,
      license="BSD",
      platforms='OS Independent',
      name="djmako",
      url="http://bitbucket.org/smulloni/djmako",
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Web Environment",
                   "Framework :: Django",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Text Processing :: Markup :: HTML',
      ],
      version=VERSION,
      keywords="django mako templating",
      packages=("djmako",),
      package_dir={'': "."},
      )
