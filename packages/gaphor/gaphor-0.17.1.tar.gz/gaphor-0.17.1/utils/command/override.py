"""
This file contains code for loading up an override file.  The override file
provides implementations of functions where the code generator could not
do its job correctly.

This is a simple rip-off of the override script used in PyGTK.
"""


import sys, string

class Overrides:

    def __init__(self, filename=None):
        self.overrides = {}
        if filename:
            self.read_overrides(filename)


    def read_overrides(self, filename):
        """Read a file and return a dictionary of overriden properties
        and their implementation.

        An override file ahs the form:
        override <property>
        <implementation>
        %%
        """
        fp = open(filename, 'r')
        # read all the components of the file ...
        # bufs contains a list of (lines, startline) pairs.
        bufs = []
        startline = 1
        lines = []
        line = fp.readline()
        linenum = 1
        while line:
            if line == '%%\n' or line == '%%':
                if lines:
                    bufs.append((list(lines), startline))
                startline = linenum + 1
                lines = []
            else:
                lines.append(line)
            line = fp.readline()
            linenum = linenum + 1
        if lines:
            bufs.append((list(lines), startline))

        if not bufs:
            return

        # Parse the parts of the file
        for lines, startline in bufs:
            line = lines[0]
            rest = lines[1:]
            words = string.split(line)

            # TODO: Create a mech to define dependencies
            if words[0] == 'override':
                func = words[1]
                deps = ()
                if len(words) > 3 and words[2] == 'derives':
                    deps = tuple(words[3:])
                self.overrides[func] = (deps, string.join(rest, ''), '%d: %s' % (startline, line))
            elif words[0] == 'comment':
                pass # ignore comments
            else:
                print "Unknown word: '%s', line %d" (words[0], startline)
                raise SystemExit

    def has_override(self, key):
        return bool(self.overrides.get(key))

    def derives(self, key):
        return self.overrides.get(key, ((), None))[0]

    def write_override(self, fp, key):
        """Write override data for 'key' to a file refered to by 'fp'."""
        deps, data, line = self.overrides.get(key, ((), None, None))
        if not data:
            return False

        fp.write('# ')
        fp.write(line)
        fp.write(data)
        return True

# vim:sw=4:et:ai
