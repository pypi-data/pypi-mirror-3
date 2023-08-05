==========================
ISO 8601 utility functions
==========================

This package collects together functions supporting the data formats described
in ISO 8601.

For the parsing functions, both the "verbose" and "short" forms of ISO 8601
times are accepted.  The verbose form includes hyphens in the date and colons
in the time, and the short form omits both.  For each function, we'll start
with verbose examples, and will then repeat all of the examples in short form.
The verbose form is generally preferred in practice since it is substantially
more readable for humans.


Parsing date values
-------------------

There's a simple function that parses a date:

    >>> from zc.iso8601.parse import date

This function only accepts a date; no time information may be included:

    >>> date(u"2006-12-02T23:40:42")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 date: u'2006-12-02T23:40:42'

    >>> date(u"2006-12-02T23:40:42Z")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 date: u'2006-12-02T23:40:42Z'

    >>> date(u"2006-12-02T23:40:42+00:00")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 date: u'2006-12-02T23:40:42+00:00'

    >>> date(u"2006-12-02T23:40:42-00:00")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 date: u'2006-12-02T23:40:42-00:00'

    >>> date(u"2006-12-02T23:40:42-01:00")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 date: u'2006-12-02T23:40:42-01:00'

A date without time information is parsed as expected:

    >>> date(u"2011-10-10")
    datetime.date(2011, 10, 10)
    >>> date(u"20111010")
    datetime.date(2011, 10, 10)

    >>> date(u"0001-01-01")
    datetime.date(1, 1, 1)
    >>> date(u"00010101")
    datetime.date(1, 1, 1)

    >>> date(u"9999-12-31")
    datetime.date(9999, 12, 31)
    >>> date(u"99991231")
    datetime.date(9999, 12, 31)

Surrounding whitespace is ignored:

    >>> date(u"\t\n\r 2011-10-10 \r\n\t")
    datetime.date(2011, 10, 10)
    >>> date(u"\t\n\r 20111010 \r\n\t")
    datetime.date(2011, 10, 10)

Embedded whitespace is not:

    >>> date("2011 10 10")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 date: '2011 10 10'


Parsing date/time values
------------------------

There is a function that parses text and returns date/time values:

    >>> from zc.iso8601.parse import datetime

This function does not support or accept values that include time zone
information:

    >>> datetime(u"2006-12-02T23:40:42Z")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006-12-02T23:40:42Z'

    >>> datetime(u"2006-12-02T23:40:42+00:00")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006-12-02T23:40:42+00:00'

    >>> datetime(u"2006-12-02T23:40:42-00:00")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006-12-02T23:40:42-00:00'

    >>> datetime(u"2006-12-02T23:40:42-01:00")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006-12-02T23:40:42-01:00'

For times that don't include zone offsets, the results are as expected:

    >>> datetime(u"2006-12-02T23:40:42")
    datetime.datetime(2006, 12, 2, 23, 40, 42)

The seconds field, as shown above, is optional.  If omitted, the seconds field
of the time will be zero:

    >>> datetime(u"2006-12-02T23:40")
    datetime.datetime(2006, 12, 2, 23, 40)

When the seconds are specified, fractional seconds are supported:

    >>> datetime(u"2008-05-12T14:30:32.000")
    datetime.datetime(2008, 5, 12, 14, 30, 32)

    >>> datetime(u"2008-05-12T14:30:32.5")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 500000)

    >>> datetime(u"2008-05-12T14:30:32.01")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000)

    >>> datetime(u"2008-05-12T14:30:32.000001")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 1)

Fractional seconds smaller than 1 microsecond are simply thrown away:

    >>> datetime(u"2008-05-12T14:30:32.00000099999")
    datetime.datetime(2008, 5, 12, 14, 30, 32)

If a space is used instead of the "T" separator, the input is still
interpreted properly:

    >>> datetime(u"2006-12-02 23:40:42")
    datetime.datetime(2006, 12, 2, 23, 40, 42)

    >>> datetime(u"2008-05-12 14:30:32.01")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000)

Surrounding whitespace is ignored, and multiple whitespace characters between
the date and time fields is collapsed and treated as if the extra whitespace
characters were not present:

    >>> datetime(u"""
    ...   2006-12-02
    ...   \t\r\f
    ...   23:40:42
    ... """)
    datetime.datetime(2006, 12, 2, 23, 40, 42)

    >>> datetime(u"""
    ...   2008-05-12
    ...   \t\r\f
    ...   14:30:32.01
    ... """)
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000)

Other whitespace is considered an error:

    >>> datetime(u"  2006 -12-02  23:40:42  ")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006 -12-02 23:40:42'

Now, let's look at how the same examples do in the short form:

    >>> datetime(u"20061202T234042Z")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'20061202T234042Z'

    >>> datetime(u"20061202T234042+0000")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'20061202T234042+0000'

    >>> datetime(u"20061202T234042-0000")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'20061202T234042-0000'

    >>> datetime(u"20061202T234042-0100")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'20061202T234042-0100'

    >>> datetime(u"20061202T234042")
    datetime.datetime(2006, 12, 2, 23, 40, 42)

    >>> datetime(u"20061202T2340")
    datetime.datetime(2006, 12, 2, 23, 40)

    >>> datetime(u"20080512T143032.000")
    datetime.datetime(2008, 5, 12, 14, 30, 32)

    >>> datetime(u"20080512T143032.5")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 500000)

    >>> datetime(u"20080512T143032.01")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000)

    >>> datetime(u"20080512T143032.000001")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 1)

    >>> datetime(u"20080512T143032.00000099999")
    datetime.datetime(2008, 5, 12, 14, 30, 32)

    >>> datetime(u"20061202 234042")
    datetime.datetime(2006, 12, 2, 23, 40, 42)

    >>> datetime(u"20080512 143032.01")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000)

    >>> datetime(u"""
    ...   20061202
    ...   \t\r\f
    ...   234042
    ... """)
    datetime.datetime(2006, 12, 2, 23, 40, 42)

    >>> datetime(u"""
    ...   20080512
    ...   \t\r\f
    ...   143032.01
    ... """)
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000)

    >>> datetime(u"  2006 1202  234042  ")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006 1202 234042'


Parsing date/time values with time zone information
---------------------------------------------------

There is a function that parses text and returns date/time values with time
zone offsets:

    >>> from zc.iso8601.parse import datetimetz

Times in UTC may be encoded using either the "Z" notation or "+00:00" (or
"-00:00").  Let try a few examples:

    >>> datetimetz(u"2006-12-02T23:40:42Z")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40:42+00:00")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40:42-00:00")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

The time zone information must be given explicitly, however; it cannot be
omitted:

    >>> datetimetz(u"2006-12-02T23:40:42")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006-12-02T23:40:42'

Other time zones are converted to UTC:

    >>> datetimetz(u"2006-12-02T23:40:42-01:00")
    datetime.datetime(2006, 12, 3, 0, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40:42-04:00")
    datetime.datetime(2006, 12, 3, 3, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40:42-05:00")
    datetime.datetime(2006, 12, 3, 4, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40:42+01:00")
    datetime.datetime(2006, 12, 2, 22, 40, 42, tzinfo=<UTC>)

We'll even make up a few that have non-zero values for the minutes portion of
the offset.  While these are made-up time zones, there are real time zones
that aren't exactly some interger number of hours offset from UTC:

    >>> datetimetz(u"2006-12-02T23:40:42-05:25")
    datetime.datetime(2006, 12, 3, 5, 5, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40:42+01:25")
    datetime.datetime(2006, 12, 2, 22, 15, 42, tzinfo=<UTC>)

The seconds field, as shown above, is optional.  If omitted, the seconds field
of the time will be zero:

    >>> datetimetz(u"2006-12-02T23:40Z")
    datetime.datetime(2006, 12, 2, 23, 40, tzinfo=<UTC>)

    >>> datetimetz(u"2006-12-02T23:40-05:00")
    datetime.datetime(2006, 12, 3, 4, 40, tzinfo=<UTC>)

When the seconds are specified, fractional seconds are supported:

    >>> datetimetz(u"2008-05-12T14:30:32.000Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, tzinfo=<UTC>)

    >>> datetimetz(u"2008-05-12T14:30:32.5Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 500000, tzinfo=<UTC>)

    >>> datetimetz(u"2008-05-12T14:30:32.01Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000, tzinfo=<UTC>)

    >>> datetimetz(u"2008-05-12T14:30:32.000001+00:00")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 1, tzinfo=<UTC>)

Fractional seconds smaller than 1 microsecond are simply thrown away:

    >>> datetimetz(u"2008-05-12T14:30:32.00000099999+00:00")
    datetime.datetime(2008, 5, 12, 14, 30, 32, tzinfo=<UTC>)

If a space is used instead of the "T" separator, the input is still
interpreted properly:

    >>> datetimetz(u"2006-12-02 23:40:42Z")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"2008-05-12 14:30:32.01Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000, tzinfo=<UTC>)

Surrounding whitespace is ignored, and multiple whitespace characters between
the date and time fields is collapsed and treated as if the extra whitespace
characters were not present:

    >>> datetimetz(u"""
    ...   2006-12-02
    ...   \t\r\f
    ...   23:40:42Z
    ... """)
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"""
    ...   2008-05-12
    ...   \t\r\f
    ...   14:30:32.01Z
    ... """)
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000, tzinfo=<UTC>)

Other whitespace is considered an error:

    >>> datetimetz(u"  2006 -12-02  23:40:42Z  ")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'2006 -12-02 23:40:42Z'

Now, let's look at how the same examples do in the short form.  Note that time
zone offsets given in numeric form continue to include the minus sign; that
carries necessary information, while the hyphens in the date are purely for
human consumption:

    >>> datetimetz(u"20061202T234042Z")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042+0000")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042-0000")
    datetime.datetime(2006, 12, 2, 23, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042")
    Traceback (most recent call last):
    ValueError: could not parse ISO 8601 datetime: u'20061202T234042'

    >>> datetimetz(u"20061202T234042-0100")
    datetime.datetime(2006, 12, 3, 0, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042-0400")
    datetime.datetime(2006, 12, 3, 3, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042-0500")
    datetime.datetime(2006, 12, 3, 4, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042+0100")
    datetime.datetime(2006, 12, 2, 22, 40, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042-0525")
    datetime.datetime(2006, 12, 3, 5, 5, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T234042+0125")
    datetime.datetime(2006, 12, 2, 22, 15, 42, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T2340Z")
    datetime.datetime(2006, 12, 2, 23, 40, tzinfo=<UTC>)

    >>> datetimetz(u"20061202T2340-0500")
    datetime.datetime(2006, 12, 3, 4, 40, tzinfo=<UTC>)

    >>> datetimetz(u"20080512T143032.000Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, tzinfo=<UTC>)

    >>> datetimetz(u"20080512T143032.5Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 500000, tzinfo=<UTC>)

    >>> datetimetz(u"20080512T143032.01Z")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 10000, tzinfo=<UTC>)

    >>> datetimetz(u"20080512T143032.000001+0000")
    datetime.datetime(2008, 5, 12, 14, 30, 32, 1, tzinfo=<UTC>)

    >>> datetimetz(u"20080512T143032.00000099999+00:00")
    datetime.datetime(2008, 5, 12, 14, 30, 32, tzinfo=<UTC>)
