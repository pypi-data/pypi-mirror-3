Introduction and Examples
-------------------------

The fuzzyparsers library provides a small collection of functions to sanitize
free form user input.  For the moment its chief value is the flexible date
parser.

The library has two main parsers.  The first is a prefix parser which compares
a string to a list of strings and returns the unique element of the list which
matches the prefix.  An exception is thrown if the match is not unique.

    >>> from fuzzyparsers import fuzzy_match
    >>> fuzzy_match(['aab','bba','abc'],'aa')
    'aab'
    >>> fuzzy_match(['aab','bba','abc'],'a')  # two strings starting with 'a'.
    Traceback (most recent call last):
    ... 
    ValueError: ambiguous match for 'a'

The second parser parses dates in various formats and returns a datetime.date
object.  Accepted formats include::

    jan 12, 2003
    jan 5
    2004-3-5
    +34 -- 34 days in the future (relative to todays date)
    -4 -- 4 days in the past (relative to todays date)

For instance:

    >>> from fuzzyparsers import parse_date
    >>> parse_date('jun 17 2010') # my youngest son's birthday
    datetime.date(2010, 6, 17)

The library allows setting a default date to fill in specified components of a
date (e.g. the year).  By default, a date with-out a year to will give the
current year.

    >>> from fuzzyparsers import DateParser
    >>> import datetime
    >>> DateParser(today=datetime.date(2013, 3, 1)).parse_date('feb 3')
    datetime.date(2013, 2, 3)

TODO
----

We'd like to support the following features:

* Parsing time strings like "10 am" and "2 3 pm"
* A "[0-9]*.[0-9]*" with the first hunk a month and the second hunk a day
  should return the month/day combination which is nearest.  For example,
  "12-3" would return december 3 of this year or last year.

Changelog
---------
* 0.7.2 - added doc-tests and "march 2012" date format; doc-test scripts
* 0.7.1 - install fixes
* 0.7 - overhaul of date parsing api to support relative dates (not necessarily
  relative to the current date)
* 0.6.x - initial public release and series of doc/install corrections

Installation
------------

Fuzzyparsers is written by Joel B. Mohler and distributed under the terms of
the GPL v2 (or later).

Use the following commands to run the extensive doc-tests::

    python -m doctest fuzzyparsers/*.py
    python -m doctest README.txt

To install fuzzyparsers, do the normal python thing (probably as root)::

    python setup.py install

or::

    eazy_install fuzzyparsers
