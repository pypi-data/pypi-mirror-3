"""
Contains classes to help other classes mimic the behavior of strings.
"""


class StringLike(object):
    """
    Class to mimic the behavior of a regular string. Classes that inherit (or mixin) this class
    must implement the `__str__` magic method. Whatever that method returns is used by the various
    string-like methods.
    """

    def __getattr__(self, attr):
        """
        Forwards any other methods to the resulting string's class. This allows support for string
        methods like `upper()`, `lower()`, sub-indexing, etc.
        """
        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)
        raise AttributeError(attr)

    def __len__(self):
        """
        Mimics the behavior of `len(a)` on strings for this class.
        """
        return len(str(self))

    def __getitem__(self, key):
        """
        Mimics the behavior of `a[n]` on strings for this class.
        """
        return str(self)[key]

    def __iter__(self):
        """
        Mimics the behavior of `iter(a)` on strings for this class.
        """
        return iter(str(self))

    def __contains__(self, item):
        """
        Mimics the behavior of `a in b` on strings for this class.
        """
        return item in str(self)

    def __add__(self, other):
        """
        Mimics the behavior of `a + b` on strings for this class.
        """
        return str(self) + other

    def __radd__(self, other):
        """
        Mimics the behavior of `b + a` on strings for this class.
        """
        return other + str(self)
