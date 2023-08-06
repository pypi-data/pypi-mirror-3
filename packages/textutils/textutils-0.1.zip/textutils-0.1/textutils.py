# vim: ft=python ts=4 sts=4 sw=4 et cc=80 fileencoding=utf-8
# Collection of string and text utilities
#
# To the extent possible under law, the authors have dedicated all
# copyright and related and neighboring rights to this software to
# the public domain worldwide.  This software is distributed without
# any warranty.


""" Small collection of string and text utilities """


import sys


__all__ = [
    'quote',
    'StringType',
    'Table',
    'trim',
]





""" The type from which all strings are derived from. """
if sys.version_info.major >= 3:
    # Py3k; strings are <class 'str'>
    StringType = str
else:
    # Py2.x; strings are <class 'basestring'>
    StringType = basestring


def quote (string, quotes=('"', "'", '`'), escape='\\', always_quote=False):
    r"""
       Quote a string.

       First, each quote in `quotes` is checked, in order, to see if is there
       any one which is not present in the string, in which case that one will
       be used to quote the string.

       If all the specified quotes are used in the string, the least used one
       is selected, and its occurrences inside the string are prefixed with
       `escape`.

       By default, the string is only quoted if it contains whitespace.
       By setting the `always_quote` parameter to True, the string is
       quoted regardless of necessity.

       Examples:
         >>> print(quote('NoQuotesNeeded'))
         NoQuotesNeeded
         >>> print(quote('This string has "double quotes"'))
         'This string has "double quotes"'
         >>> print(quote("This string has 'single quotes'"))
         "This string has 'single quotes'"
         >>> print(quote('This string has \'single\' and "double" quotes'))
         `This string has 'single' and "double" quotes`
         >>> print(quote('"This string\'s" will have an `escaped` apostrophe'))
         '"This string\'s" will have an `escaped` apostrophe'
         >>> print(quote('And `this one`\'s apostrophe will be "$"-escaped',
         ...             escape='$'))
         'And `this one`$'s apostrophe will be "$"-escaped'
         >>> print(quote('ThisWillBeAlwaysQuoted', always_quote=True))
         "ThisWillBeAlwaysQuoted"
         >>> print(quote('This one will have funny quotes', quotes=('!YAH!',)))
         !YAH!This one will have funny quotes!YAH!
    """

    def has_whitespace (s):
        """
           Check if the string does contain any whitespace.

           >>> has_whitespace('The_quick_brown_fox_jumps_over_the_lazy_dog')
           False
           >>> has_whitespace('The quick brown fox jumps over the lazy dog')
           True
           >>> has_whitespace('This…\vis…\rSPARTA!!!')
           True
        """
        # There are two obvious ways to do this:
        #   1. Using a regexp (r'\s+')
        #   2. Checking if the string contains any characters from
        #      string.whitespace
        #
        # No. 1 is likely to be slow on strings where the first whitespace
        # is far from the beginning, and no. 2 is terribly inefficient due
        # to the fact space (U+0020) is the last character in that sequence,
        # what means it would be the last one to be searched.
        #
        # So here we use our own variation of no. 2.
        whitespace = ' \t\n\r\f\v'
        return any(ws in s for ws in whitespace)

    # If the string contains no whitespace, return it unchanged,
    # unless specified otherwise
    if not (always_quote or has_whitespace(string)):
        return string

    try:
        # Try to use a quote which is not present in the string
        quote = next(q for q in quotes if not q in string)
    except StopIteration:
        # Find the least used quote and use it
        quote = min(quotes, key=string.count)
        # Escape the quote in the string
        string = string.replace(quote, escape + quote)
    return quote + string + quote


# PEP 257's trim put into a module
def trim (string, expand_tabs=True, rstrip=True):
    r"""
       Remove indentation and trim empty lines from a string, as specified in
       PEP 257.

       The following text, adapted from PEP 257, describes the main operations
       performed:
       
           A uniform amount of indentation is stripped from the second and
           further lines of the string, equal to the minimum indentation
           of all non-blank lines after the first line.  Any indentation
           in the first line of the string (i.e., up to the first newline)
           is insignificant and removed.  Relative indentation of later
           lines in the string is retained.  Blank lines are removed from
           the beginning and end of the string.

       By default, trailing whitespace is removed from each line, and tabs
       are expanded with str.expandtabs().  These behaviors can be disabled
       with the `expand_tabs` and `rstrip` parameters, respectively.

       To illustrate:
         >>> foo = '''   1st
         ...        This is the second line. 
         ...        \tAnd this one is indented.
         ... '''
         >>> foo
         '   1st\n       This is the second line. \n       \tAnd this one is indented.\n'
         >>> trim(foo)
         '1st\nThis is the second line.\n And this one is indented.'
         >>> trim(foo, expand_tabs=False, rstrip=False)
         '1st\nThis is the second line. \n\tAnd this one is indented.'
    """

    if not isinstance(string, StringType):
        raise TypeError("Expected string, got %r" % type(string))
    if not string.strip():
        return ''

    # Convert tabs to spaces (following the normal Python rules) and split
    # into a list of lines
    lines = (string.expandtabs() if expand_tabs else string).splitlines()

    # Determine minimum indentation (first line doesn't count)
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    # Remove indentation (first line is special)
    trimmed = [lines[0].strip() if rstrip else lines[0].lstrip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip() if rstrip else line[indent:])

    # Strip off trailing and leading blank lines
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Return a single string
    return '\n'.join(trimmed)


class Table (object):
    """
       Helper for creating a tabular representation of data.

       Example:
         >>> table = Table(3, ['ID', 'Revision', 'Difference from pi'])
         >>> table.add_row([8, 'e4f6', -0.15])
         >>> table.add_row([42, 'b7d1ab', 0.4815162342])
         >>> table.add_row([108, '10110101', 0.00047])
         >>> print(table) # doctest:+NORMALIZE_WHITESPACE
         ID     Revision    Difference from pi
         --     --------    ------------------
         8      e4f6        -0.15
         42     b7d1ab      0.4815162342
         108    10110101    0.00047

       It's also possible to sort the data based on a column:
         >>> import math
         >>> # Here we sort based on the final value, i.e. π + the value
         >>> # of the third column
         >>> table.sort(3, key=lambda x: math.pi + float(x))
         >>> print(table) # doctest:+NORMALIZE_WHITESPACE
         ID     Revision    Difference from pi
         --     --------    ------------------
         8      e4f6        -0.15
         108    10110101    0.00047
         42     b7d1ab      0.4815162342
    """

    # Not a hashable or comparable class
    __hash__ = None
    __eq__ = __ne__ = lambda self, other: NotImplemented

    @staticmethod
    def _to_index (obj):
        try:
            index = obj.__index__()
            assert index is not NotImplemented # Why would someone do this?
        except (AttributeError, NotImplementedError):
            raise TypeError("Expected integer, got %r" % type(obj))
        return index

    def __init__ (self, columns, headers=[], header_separator='-'):
        """
           Initialize a table with the given number of columns.  Optionally,
           also add headings for the table; in the case these are present,
           the header separator character is used to separate the heading
           from the table's data.
        """

        # Perform a sanity check on the number of columns
        columns = self._to_index(columns)
        if columns < 2:
            raise ValueError("Expected value greater than 2, got %d" % columns)

        self._cache = None
        self.columns = columns
        self.data = []
        self.has_headers = bool(headers)
        if self.has_headers:
            self.add_row(headers)
            self.add_row(header_separator * len(s) for s in headers)

    def add_row (self, items):
        """ Append a row to a table. """
        items = tuple(items)
        if len(items) != self.columns:
            raise ValueError(
                "invalid number of columns in row: expected {0}, got {1}"
                .format(self.columns, len(items)))
        self.data.append([str(e) for e in items])
        self._cache = None

    def copy (self):
        """
           Create an independent copy of a table.
        """
        new = self.__class__.__new__(self.__class__)
        new._cache = None
        new.columns = self.columns
        new.has_headers = self.has_headers
        new.data = self.data[:]
        return new

    def sort (self, column, key=None, reverse=False):
        """
           Sort the rows of the table according to a specific column.
           The `key` and `reverse` parameters have the same meaning
           as for the `sorted` built-in function.

           It must be noted that the columns' data are always stored
           as strings, so e.g., when sorting by a column of integers,
           one should use `key=int`.
        """

        column = self._to_index(column)
        if not(1 <= column <= self.columns):
            raise ValueError(
                "invalid column {0}; expected integer between 1 and {1}"
                .format(column, self.columns))

        # Wrap the key function to receive the correct parameters
        if key is not None:
            key_func = key
            key = lambda row: key_func(row[column - 1])
        else:
            key = lambda row: row[column - 1]

        sort_args = {'key': key, 'reverse': reverse}
        if not self.has_headers:
            # Simple; just sort in place
            self.data.sort(**sort_args)
        else:
            # Slightly more complicated
            self.data = self.data[:2] + sorted(self.data[2:], **sort_args)
        self._cache = None

    def getvalue (self):
        """ Create a string representation of a table's data. """
        rows = self.data[:]
        for column in range(self.columns):
            # Find the length of the largest string in the column
            largest = max(len(row[column]) for row in rows)
            # Adjust each row to the maximum width found
            for row in rows:
                row[column] += ' ' * (largest - len(row[column]))
        return '\n'.join('\t'.join(row) for row in rows)

    def __str__ (self):
        """
           Create a (possibly cached) string representation of a table's data.
        """
        if self._cache is None:
            self._cache = self.getvalue()
        return self._cache
