#from distutils.core import setup
from setuptools import setup

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# pip install python-html-objects
# pip install python-html-objects --upgrade --no-deps
# Manual upload to PypI
# http://pypi.python.org/pypi/python-html-objects
# Go to 'edit' link
# Update version and save
# Go to 'files' link and upload the file


setup(name='python-html-objects',
      url='https://bitbucket.org/paulocheque/python-html-objects',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python html objects',
      description='Python library that contains objects that represents HTML tags.',
      license='MIT',

      version='0.1.0',
      packages=['html_objects', 'html_objects.tests',],
)
