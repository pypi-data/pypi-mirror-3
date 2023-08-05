from distutils.core import setup

setup(
    name='RangeParser',
    version='0.1.2',
    author='Colin Warren',
    author_email='colin@colinwyattwarren.com',
    packages=['rangeparser', 'rangeparser.test'],
    scripts=[],
    url='https://bitbucket.org/colinwarren/rangeparser',
    license='2-clause BSD',
    description='Parses ranges.',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)