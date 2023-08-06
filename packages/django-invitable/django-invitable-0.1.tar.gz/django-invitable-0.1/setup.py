try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-invitable',
    version='0.1',
    description='Reusable invitations app for Django',
    author='Teodor Pripoae',
    author_email='toni@netbaiji.com',
    url='https://github.com/teodor-pripoae/django-invitable',
    install_requires=['django'],
    packages=['invitable'])
