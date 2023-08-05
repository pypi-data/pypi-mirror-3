Python Format Functions
=======================

The van.timefmt module is a support module for date/time specific operations.

    >>> from datetime import date, datetime
    >>> mydate = date(1975, 12, 17)
    >>> mydatetime = datetime(1975, 12, 17, 5, 24, 36)

It provides a "timefmt" function which can take either a date or datetime object:

    >>> from van.timeformat import ltimefmt, timefmt

Fixed formatting
----------------

Fixed formats are locale independant. They are useful in 2 situations:

* Computer parsable dates
* Projects with no localization requirement

default formatting
++++++++++++++++++

If no format argument is specified, dates and datetimes are formatted using .isoformat(" "):

    >>> print timefmt(mydatetime)
    1975-12-17T05:24:36

    >>> print timefmt(mydate)
    1975-12-17

The 'iso' format also triggers this:
    
    >>> print timefmt(mydatetime, format='iso')
    1975-12-17T05:24:36

If None is used as an input date, timefmt will return None:
    
    >>> timefmt(None) is None
    True

rfc2822
+++++++

The date in compliance with the RFC 2822 Internet email standard.

    >>> print timefmt(mydate, 'rfc2822')
    Wed, 17 Dec 1975 00:00:00 +0000

    >>> print timefmt(mydatetime, 'rfc2822')
    Wed, 17 Dec 1975 05:24:36 +0000


Extending formats
+++++++++++++++++

If we want to extend the list of formats available, we can use the
"time_format" zcml command defined in this module's meta.zcml.

An example of use is in configure.zcml where the rfc2822 format is defined.

Note: it's probably a good idea to use namespaces for registrations. The
van.timeformat module promises to not use "." in any of it's default
registrations.

Unicode
+++++++

The return type is a unicode string:

    >>> timefmt(mydatetime)
    u'1975-12-17T05:24:36'

And we can have unicode in the formats:

    >>> timefmt(mydatetime, format='unicode_test')
    u'1975-17-12 Extended Arabic-Indic Digit Seven: \u06f7:'

Locale dependant translations
-----------------------------

    >>> from zope.i18n.locales import locales
    >>> german = locales.getLocale('de', 'de')
    >>> us = locales.getLocale('en', 'us')
    >>> britain = locales.getLocale('en', 'gb')

Returns unicode:

    >>> ltimefmt(mydate, us)
    u'Dec 17, 1975'

Defaults correctly chosen for date and datetime:

    >>> print ltimefmt(mydate, us)
    Dec 17, 1975
    >>> print ltimefmt(mydatetime, us)
    Dec 17, 1975 5:24:36 AM

But we can force format one as the other:

    >>> print ltimefmt(mydate, us, category="dateTime")
    Dec 17, 1975 12:00:00 AM
    >>> print ltimefmt(mydatetime, us, category="date")
    Dec 17, 1975

Localized:

    >>> print ltimefmt(mydate, britain, category="date", length="long")
    17 December 1975
    >>> print ltimefmt(mydate, german, category="date", length="long")
    17. Dezember 1975

If None is used as an input date, ltimefmt will return None:
    
    >>> ltimefmt(None, us) is None
    True

Localized formatting examples
+++++++++++++++++++++++++++++

Short times:

    >>> print ltimefmt(mydate, us, category="time", length="short")
    12:00 AM

Short dates:

    >>> print ltimefmt(mydate, us, category="date", length="short")
    12/17/75

Medium Dates:

    >>> print ltimefmt(mydate, us, category="date", length="medium")
    Dec 17, 1975

Long Dates:

    >>> print ltimefmt(mydate, us, category="date", length="long")
    December 17, 1975

Short Datetimes:

    >>> print ltimefmt(mydatetime, us, category="dateTime", length="short")
    12/17/75 5:24 AM

Medium Datetimes:

    >>> print ltimefmt(mydatetime, us, category="dateTime", length="medium")
    Dec 17, 1975 5:24:36 AM

Long Datetimes:

    >>> print ltimefmt(mydatetime, us, category="dateTime", length="long")
    December 17, 1975 5:24:36 AM +000

