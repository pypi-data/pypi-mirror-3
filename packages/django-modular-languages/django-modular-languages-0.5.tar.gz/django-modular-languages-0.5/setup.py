import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-modular-languages",
    version = "0.5",
    author = "Oscar Carballal Prego",
    author_email = "oscar.carballal@cidadania.coop",
    description = ("Simple script to manage multiple language catalogs in a django project."),
    license = "GPLv3",
    keywords = "script manage language i18n catalog django project",
    url = "http://github.com/oscarcp/django-modular-languages",
    packages=['.'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Intended Audience :: Developers",
   ],
)
