try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='icloud',
    version='0.1',
    license='BSD',
    author='Matin Tamizi',
    author_email='mtamizi@gmail.com',
    packages=['icloud'],
)
