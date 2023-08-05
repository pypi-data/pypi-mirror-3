from googleplus import get_version
try:
    from distutils.core import setup
    from distutils.core import find_packages
except ImportError:
    from setuptools import setup
    from setuptools import find_packages

NAME="django-googleplus"
DESCRIPTION=""" A plugable registration backend for googleplus. Closely modeled after django-registration"""
AUTHOR="Jonas Geiregat"
EMAIL="jonas@geiregat.org"
URL="https://github.com/jonasgeiregat/django-googleplus"


setup(name=NAME,
      version=get_version(),
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      url=URL,
      packages=find_packages())
