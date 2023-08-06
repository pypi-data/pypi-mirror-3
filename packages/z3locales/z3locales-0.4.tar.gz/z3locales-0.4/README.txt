=========
z3locales
=========

The code is distributed under terms of the Zope Public License version 2.1.
See also LICENSE.txt.

Z3locales is a library which translates dates in Zope 2 to the current
user language using Zope 3 technology.

Those functions are available in the module ``localdatetime``:

``get_formatted_now(request)``
    Return the current date formatted and translated in the current
    user language. The target user language is determined via the
    provided request.

``get_formatted_date(date, size="full", request=_marker, locale=_marker, display_time=True)``
    Take a date (should be a tuple ``(year, month, day[, hour[,
    minute[, second]]])`` or a Python datetime object), format it and
    translate it in the target user language (determined via locale or the
    given request). The modifier size and display_time can be used to
    change the output.

``get_month_names(request=_marker, locale=_marker, calendar='gregorian')``
    Return a list of month names translated in the target language
    (determined via locale or the given request).

``get_month_abbreviations(request=_marker, locale=_marker, calendar='gregorian')``
    Return a list of month abbreviations (usually the first three
    letters) translated in the target user language (determined via
    locale or the given request).

``get_locale_info(request)``
    Return the locale representing the target user language using the
    provided request. This locale can be used after by other functions
    of this package.


Compatibility API exists with previous versions.
