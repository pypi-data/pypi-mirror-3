from distutils.core import setup

setup(
    name='RangeParser',
    version='0.1.0',
    author='Colin Warren',
    author_email='colin@colinwyattwarren.com',
    packages=['rangeparser', 'rangeparser.test'],
    scripts=[],
    url='https://bitbucket.org/colinwarren/rangeparser',
    license='LICENSE.txt',
    description='Parses ranges.',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)