__all__ = ('VersionInfo')

import collections
import datetime
import re


class VersionInfo(object):
    __slots__ = ('data',)

    sexpr_labels = re.compile(r"\w+(?!\w)")
    sexpr_strings = re.compile(r"'((?:[^']+|'')*)'")
    date_fmt = re.compile(r"(\d{1,2}) (\w+) (\d{4})$")
    time_fmt = re.compile(r"(\d{1,2}):(\d{2})(?::(\d{2})(?:(.\d+))?)? ?([a|p]m)?$")
    months = ("January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December")

    @classmethod
    def parse(cls, contents):
        pos = 0 
        current = []
        stack = collections.deque()
        
        # iterative parser for sexpr-like constructs
        while pos < len(contents):
            c = contents[pos]
            
            if c.isspace():
                # skip spaces
                pos += 1
                continue
            
            if contents[pos] == "(":
                # start a new expression
                pos += 1
                stack.append(current)
                current = []
                continue
            
            if contents[pos] == ")":
                # finish the current expression
                pos += 1
                old, current = current, stack.pop()
                current.append(tuple(old))
                continue
            
            if contents[pos].isalpha():
                # a label
                m = cls.sexpr_labels.match(contents[pos:])
                current.append(m.group(0))
                pos += m.end(0)
                continue
            
            if contents[pos] == "'":
                # a string
                m = cls.sexpr_strings.match(contents[pos:])
                current.append(m.group(1).replace("''", "'"))
                pos += m.end(0)
                continue
        
        return VersionInfo(current[0])
    
    def __init__(self, data):
        self.data = dict(zip(data[0::2], data[1::2]))
    
    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.name)
    
    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        return getattr(super(VersionInfo, self), key)
    
    # lazy creation of ancestor instances
    def ancestors(self):
        return [VersionInfo(p) for p in self.data["ancestors"]]
    
    def timestamp(self):
        day, month, year = self.date_fmt.match(self.date).groups()
        hour, minute, second, fraction, ampm = self.time_fmt.match(self.time).groups()
        
        return datetime.datetime(
            int(year),
            self.months.index(month) + 1,
            int(day),
            (int(hour) + (12 if ampm == "pm" else 0)) % 24,
            int(minute),
            int(second or 0),
            int(float(fraction or 0.0) * 1e6))
