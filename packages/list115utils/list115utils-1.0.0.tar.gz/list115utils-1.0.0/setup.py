from distutils.core import setup

setup(
        name='list115utils',
        version='1.0.0',
        author='A115',
        author_email='contact@a115.bg',
        packages=['list115utils', 'list115utils.test'],
        scripts=[],
        url='http:/pypi.python.org/pypi/list115utils/',
        license='LICENSE.txt',
        description='Collection of clean, well-tested, well-documented Python utilities for manipulating lists and facilitating functional programming',
        long_description=open('README.txt').read(),
        )
