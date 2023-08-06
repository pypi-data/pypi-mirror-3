#from distutils.core import setup
from setuptools import setup

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# pip install django-dynamic-fixture
# pip install django-dynamic-fixture --upgrade --no-deps
# Manual upload to PypI
# http://pypi.python.org/pypi/django-dynamic-fixture
# Go to 'edit' link
# Update version and save
# Go to 'files' link and upload the file


setup(name='django-dynamic-fixture',
      url='https://bitbucket.org/paulocheque/django-dynamic-fixture',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python django testing fixture',
      description='A full library to create dynamic model instances for testing purposes.',
      license='MIT',

      version='1.4.3',
      entry_points={ 'nose.plugins': ['queries = queries:Queries', ] },
      packages=['django_dynamic_fixture', 'django_dynamic_fixture/tests', 'queries', 'queries/management/commands'],
)
