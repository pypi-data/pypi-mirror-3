#!/usr/bin/python

# Commentary: parse_file will parse a table file and return a list of
# lists of strings for you do do whatever you want with. See Line
# class documentation for more info.

# For future versions:
#   make separators escapable
#   add comment support
#   support for optional columns


import re
from itertools import takewhile, dropwhile

class Line(object):
    """Just a line aware of it's header, it is able to merge
    """

    def __init__(self, string, parser):
        """Try to use head to parse string into cells of a row and
        then put them into _row which you can retrieve form
        to_list. If head is None then we read solely based on the
        string provided. You can provide your own separator and the
        number (the line number is only used for debug messages)"""
        self._line = parser.linum
        self._head = None
        self._separator = parser.separator
        self._string = self._strip_edge_separators(string)
        self._row = self._string.split(self._separator)
        if parser.head is None:
            self._head = ['']
        else:
           self._head = parser.head.to_list()


        if not self._separator in string:
            self._row = ['']*len(self._head)
            return


        if len(self._row) > len(self._head) and self._head != ['']:
            self._sanitize()
        if len(self._row) < len(self._head):
            raise Exception("Too few cells on line %d (expected %d, got %d)" % (self._line, len(self._head), len(self._row)))

        # Spaces are important for spacing :P
        self._row = map(self.clean_spaces, self._row)

    def _strip_edge_separators(self, string):
        """If after any leadingor trailing spaces there are separators
        remove both spaces and separators"""
        if string.rstrip()[-1] == self._separator:
            string = string.rstrip()[:-1]

        if string.strip()[0] == self._separator:
            string = string.strip()[1:]

        return string

    def _sanitize(self):
        """Try given the separator-based split self._rows to merge to
        get the same number of cells as head based on the cell size"""


        row_i = head_i = 0
        while row_i < len(self._row) - 1:
            if len(self._row) <= len(self._head):
                break

            # While merging cells helps preserve the cell size
            while len(self._row[row_i]) < len(self._head[head_i]) and abs(len(self._row[row_i]) + len(self._row[row_i+1]) - len(self._head[head_i])) < abs(len(self._row[row_i]) - len(self._head[head_i])):
                self._row[row_i] += self._separator + self._row[row_i+1]
                del self._row[row_i+1]

            row_i+=1
            head_i+=1

    def clean_spaces(self, s):
        """Remove spaces from string in the front and back"""
        return s.strip().rstrip()

    def merge(self, line_list, join_char = "\n"):
        """Merge the list of lines with this line. Join cells with provided character."""
        for l in line_list:
            if len(l) != len(self._row):
                raise Exception("Unmatched number fo cells while merging lines.")

            def smart_concat(x, y):
                if not x:
                    return y
                if not y:
                    return x
                return x+join_char+y

            self._row = map(smart_concat, self._row, l._row)

    def empty_line(self):
        """All cells are empty. most probably a separator or an empty
        line or later maybe a comment"""
        for i in self._row:
            if i != "":
                return False
        return True

    def standalone(self):
        """A standalone row is a row that is not the continuation of
        it's above and that is if it's first field is empty. Note that
        that includes lines that are completely empty and invalid
        lines (that are converted to completely empty."""
        return bool(self._row[0])

    def __len__(self):
        return len(self._row)

    def __repr__(self):
        return str(self._row)

    def to_list(self):
        """After a row is created and merged the above functions are
        of no use yet we may need to access slices etc. For now the
        solution is to turn it into a list. Later, we mayn need to be
        able to recosntruct the table, so I will implement the rest
        then."""
        return self._row

    def __nonzero__(self):
        for i in self._row:
            if i != '':
                return True
        return False

class Parser(object):

    def __init__(self, filename, sep = '|'):
        """Returns a list of lists with the cells of a table separated by
        separator. The header line is separated from the rest with an
        empty_line. Lines that are not standalone are merged with the
        previous line.  See Line class for more info on parameters."""
        self.separator = sep
        self.linum = 1
        self.head = None

        f = open(filename, 'r')
        itf = iter(f.readlines())

        # Parse header
        while not self.head:
            self.linum+=1
            try:
                self.head = None
                tmp = itf.next()
                self.head = Line(tmp, self)
            except StopIteration:
                raise Exception("No table found in file '%s'" % filename)

        # Parse rows
        rrows = []
        for s in itf:
            self.linum += 1
            rrows.append(Line(s, self))

        # Merge until the separator, note that this consumes the separator aswell
        cursor = iter(rrows)
        self.head.merge([i for i in takewhile(lambda (x): bool(x), cursor)])
        self.lines = []
        for i in cursor:
            self.consume_line(i)

        if len(self.lines) == 0:
            print "W: Found just one line  of table"
            return

        if not self.lines[0]:
            del self.lines[0]

        assert self.lines[0].standalone()

    def consume_line(self, line):
        """If the line is a continuation then merge it with the last
        encountered line. If not merge it with the last one ok."""
        if not line.standalone() and len(self.lines):
            self.lines[-1].merge([line])
        else:
            self.lines.append(line)

    @property
    def rows(self):
        """List of rows."""
        return [Row(self.head.to_list(), i.to_list()) for i in self.lines]


class Row(dict):
    """Use this class to obtain a dict of the row with the column names as keys"""
    def __init__(self, headers, cells):
        self._headers = map(self._strip_numbers, headers)
        for i,c in zip(self._headers, cells):
            self[i] = c

    def _strip_numbers(self, cell):
        return re.sub("\d", "", cell)


def parse_file(filename):
    """For backwards compatibility basically"""
    return Parser(filename).rows

if __name__ == "__main__":
    from sys import argv, exit
    USAGE = """parser.py <filename> <row> <column>
Outputs the text of the cell you queried for."""


    if len(argv) == 1 or argv[1] == "help":
        print USAGE
        exit()

    rows = parse_file(argv[1], '|')

    print rows
