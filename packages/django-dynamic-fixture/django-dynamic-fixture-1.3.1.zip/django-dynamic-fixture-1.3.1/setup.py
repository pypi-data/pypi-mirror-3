#from distutils.core import setup
from setuptools import setup

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# http://pypi.python.org/pypi/django-dynamic-fixture
# pip install django-dynamic-fixture
# pip install django-dynamic-fixture --upgrade --no-deps

setup(name='django-dynamic-fixture',
      url='http://code.google.com/p/django-dynamic-fixture',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python django testing fixture',
      description='A full library to create dynamic model instances for testing purposes.',
      license='MIT',

      version='1.3.1',
      packages=['django_dynamic_fixture', 'django_dynamic_fixture/tests', ],
)
