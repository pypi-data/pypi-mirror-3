from setuptools import setup, find_packages

setup(name='django-cms-facetsearch',
      version='0.9.2',
      description='Searching using language facets for django-cms pages and plugins.',
      author='Oyvind Saltvik',
      author_email='oyvind.saltvik@gmail.com',
      url='http://github.com/fivethreeo/django-cms-facetsearch/',
      packages = find_packages(),
      include_package_data=True,
      zip_safe = False
)
