try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-rails-model',
    version='0.1',
    description='Rails like models: hooks, first, last selectors, etc',
    author='Teodor Pripoae',
    author_email='toni@netbaiji.com',
    url='https://github.com/teodor-pripoae/django-rails-model',
    install_requires=['django'],
    packages=['rails_model'])
