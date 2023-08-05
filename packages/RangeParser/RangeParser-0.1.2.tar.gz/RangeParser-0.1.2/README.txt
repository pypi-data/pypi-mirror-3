===========
RangeParser
===========

RangeParser is a Python package to parse ranges easily.

    from rangeparser import RangeParser

    parser = RangeParser()

    parser.parse('10,20,30')
    # => [10, 20, 30]

    parser.parse('1-10')
    # => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    parser.parse('10,20,30,40-45')
    # => [10, 20, 30, 40, 41, 42, 43, 44, 45]

Hacking
-------

* Make your changes, send a pull request, etc.

* If it's a bug, file an issue, then send a pull request.

* Any new features require testing. All tests must pass for a pull request to be submitted.

* If it's a behavior breaking change, email me first (colin@colinwyattwarren.com).