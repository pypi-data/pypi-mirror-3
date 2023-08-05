##############################################################################
#
# Copyright (c) 2006-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""\
Utility functions for parsing ISO 8601 values.

"""
__docformat__ = "reStructuredText"

# We have to use import-as since we mask the module name.
import datetime as _datetime
import pytz
import re


# "Verbose" ISO 8601, with hyphens and colons:
_date_re1 = """\
    (?P<year>\d\d\d\d)
    -(?P<month>\d\d)
    -(?P<day>\d\d)
    """

# "Compact" ISO 8601, without hyphens and colons:
_date_re2 = """\
    (?P<year>\d\d\d\d)
    (?P<month>\d\d)
    (?P<day>\d\d)
    """

_date_rx1 = re.compile(_date_re1 + "$", re.VERBOSE)
_date_rx2 = re.compile(_date_re2 + "$", re.VERBOSE)
_date_rxs = [_date_rx1, _date_rx2]

_tz_re = "(?:Z|(?P<tzdir>[-+])(?P<tzhour>\d\d):(?P<tzmin>\d\d))$"

# "Verbose" ISO 8601, with hyphens and colons:
_datetime_re1 = _date_re1 + """\
    [T\ ]
    (?P<hour>\d\d)
    :(?P<minute>\d\d)
    (?::(?P<second>\d\d(?:\.\d+)?))?
    """

_datetimetz_re1 = _datetime_re1 + _tz_re
_datetime_re1 += "$"

# "Compact" ISO 8601, without hyphens and colons:
_datetime_re2 = _date_re2 + """\
    [T\ ]
    (?P<hour>\d\d)
    (?P<minute>\d\d)
    (?P<second>\d\d(?:\.\d+)?)?
    """

_datetimetz_re2 = _datetime_re2 + _tz_re.replace("):(", "):?(")
_datetime_re2 += "$"

_datetime_rx1 = re.compile(_datetime_re1, re.VERBOSE)
_datetime_rx2 = re.compile(_datetime_re2, re.VERBOSE)
_datetime_rxs = [_datetime_rx1, _datetime_rx2]

_datetimetz_rx1 = re.compile(_datetimetz_re1, re.VERBOSE)
_datetimetz_rx2 = re.compile(_datetimetz_re2, re.VERBOSE)
_datetimetz_rxs = [_datetimetz_rx1, _datetimetz_rx2]


def date(string):
    """Parse an ISO 8601 date without time information.

    Returns a Python date object.

    """
    m = _find_match(string, _date_rxs, "date")
    year, month, day = map(int, m.group("year", "month", "day"))
    return _datetime.date(year, month, day)
    


def datetime(string):
    """Parse an ISO 8601 date without timezone information.

    Returns a Python datetime object.

    """
    m = _find_match(string, _datetime_rxs)
    parts = _get_datetime_parts(m)
    return _datetime.datetime(*parts)


def datetimetz(string):
    """Parse an ISO 8601 date including timezone information.

    Returns a Python datetime object.

    """
    m = _find_match(string, _datetimetz_rxs)
    parts = _get_datetime_parts(m)
    year, month, day, hour, minute, second, microsecond = parts

    if m.group("tzhour"):
        tzhour, tzmin = map(int, m.group("tzhour", "tzmin"))
        offset = (tzhour * 60) + tzmin
        if m.group("tzdir") == "-":
            offset *= -1
        if offset:
            tzinfo = pytz.FixedOffset(offset)
            dt = _datetime.datetime(
                year, month, day, hour, minute, second, microsecond,
                tzinfo=tzinfo)
            return dt.astimezone(pytz.UTC)

    return _datetime.datetime(
        year, month, day, hour, minute, second, microsecond,
        tzinfo=pytz.UTC)


def _find_match(string, rxs, what="datetime"):
    string = " ".join(string.split())
    for rx in rxs:
        m = rx.match(string)
        if m is not None:
            return m
    raise ValueError("could not parse ISO 8601 %s: %r" % (what, string))


def _get_datetime_parts(m):
    year, month, day, hour, minute = map(
        int, m.group("year", "month", "day", "hour", "minute"))
    second = 0
    microsecond = 0
    s = m.group("second")
    if s:
        try:
            second = int(s)
        except ValueError:
            seconds = float(s)
            second = int(seconds)
            # We figure out microseconds this way to avoid floating-point
            # issues.  Anything smaller than one microsecond is simply thrown
            # away.
            fractional = s.split(".")[1]
            while len(fractional) < 6:
                fractional += "0"
            fractional = fractional[:6]
            microsecond = int(fractional)
    return year, month, day, hour, minute, second, microsecond
