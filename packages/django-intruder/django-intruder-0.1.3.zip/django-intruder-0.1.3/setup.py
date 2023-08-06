#from distutils.core import setup
from setuptools import setup

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# pip install django-intruder
# pip install django-intruder --upgrade --no-deps
# Manual upload to PypI
# http://pypi.python.org/pypi/django-intruder
# Go to 'edit' link
# Update version and save
# Go to 'files' link and upload the file


setup(name='django-intruder',
      url='https://bitbucket.org/paulocheque/django-intruder',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python django intruder feature flip feature switch',
      description='Django Intruder is a simple and unobtrusive application to intercept requests. It is useful to enable and disable features, for continuous deployment purpouses.',
      license='MIT',

      version='0.1.3',
      packages=['intruder', 'intruder/tests', 'example'],
)
