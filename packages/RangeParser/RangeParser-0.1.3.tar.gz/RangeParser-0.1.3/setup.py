from distutils.core import setup

setup(
    name='RangeParser',
    version='0.1.3',
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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Text Processing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
  ],
)