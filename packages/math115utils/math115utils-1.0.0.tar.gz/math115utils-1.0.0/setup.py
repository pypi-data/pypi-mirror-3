from distutils.core import setup

setup(
        name='math115utils',
        version='1.0.0',
        author='A115',
        author_email='contact@a115.bg',
        packages=['math115utils', 'math115utils.test'],
        scripts=[],
        url='http://pypi.python.org/pypi/math115utils/',
        license='LICENSE.txt',
        description='Collection of clean, well-tested, well-documented Python utilities for mathematical manipulations. ',
        long_description=open('README.txt').read(),
        )
