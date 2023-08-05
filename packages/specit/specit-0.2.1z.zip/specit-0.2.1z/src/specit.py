"""specit assists in creating and running executable specifications.

The components and conventions that make up specit are crafted to 
help developers create software specifications with a BDD bias.

Once you have imported the "expect" starter into your spec file,
you may start describing the behaviour of your software
"""
import os
import sys


# core
# ====

class Expect(object):
    """Encapsulates a value (primitive, expression or callable)
    that would later be compared to another value.

    Provides the basic construct for describing an expectation.
    Generally you would not use this class directly, instead it is 
    available through the "expect" alias which allows for a more 
    pythonic syntax.
    
    it initializes with primitives, native types and expressions
    
    >>> e = Expect("Foo")
    >>> e.actual == "Foo"
    True
    
    >>> e = Expect(['a', 'b'])
    >>> e.actual == ['a', 'b']
    True
    
    >>> Expect(4 + 7).actual == 11
    True
    
    >>> Expect(4 == 7).actual == False
    True
    """
    def __init__(self, value):
        self.actual = value
    

# provide a usable alias for the Expect class
expect = Expect
"""Alias for the Expect class that starts an expectation contruct.

So you can do this:

    >>> expect(5 + 10).actual == 45
    True
"""
    
def matcher(func):
    """Registers the decorated function as a matcher for 
    the Expect class aliased by "expect" """
    setattr(expect, func.__name__, func)

def ensure(expr, outcome, message=""):
    """Compares the result of the given boolean expression to the anticipated
    boolean outcome. If there is a match, all is well. If the comparison fails,
    it throws an AssersionError with the given message
    
    it stays quite if the comparison lines up
    
    >>> ensure(5 == 5, True)
    
    it throws an error if the comparison fails
    
    >>> ensure('Foo' == 'foo', True)
    Traceback (most recent call last):
        ...
    AssertionError
    
    it throws an error with the given message if the comparison fails
    
    >>> actual = 'Foo'
    >>> expected = 'foo'
    >>> message = "'%s' does not equal '%s'" % (actual, expected)
    >>> ensure(actual == expected, True, message)
    Traceback (most recent call last):
        ...
    AssertionError: 'Foo' does not equal 'foo'
    """
    if expr != outcome:
        raise AssertionError(message)


# Basic matchers
# ==============

@matcher
def to_equal(self, expected):
    """Compares values based on simple equality "=="
    
    it passes if the values are equal
    
    >>> expect(555).to_equal(555)
    
    it fails if the values are not equal
    
    >>> expect('waiting...').to_equal('done!')
    Traceback (most recent call last):
        ...
    AssertionError: Expected 'waiting...' to equal 'done!'
    """
    msg = "Expected '%s' to equal '%s'" % (self.actual, expected)
    ensure(self.actual == expected, True, msg)

@matcher
def to_be(self, expected):
    """Compares values based on identity "is"
    
    it passes if the values are identical
    
    >>> a1 = a2 = ['foo', 'bar']
    >>> expect(a1).to_be(a2)
    
    it fails if the values are not identical
    
    >>> b1 = ['foo', 'bar']
    >>> expect(a1).to_be(b1)
    Traceback (most recent call last):
        ...
    AssertionError: Expected '['foo', 'bar']' to be '['foo', 'bar']'
    """
    msg = "Expected '%s' to be '%s'" % (self.actual, expected)
    ensure(self.actual is expected, True, msg)
    
@matcher
def to_return(self, expected):
    """Compares the return value of a callable to the expected value
    
    it passes if the callable returns the expected value
    
    >>> def foo():
    ...     return "Foo"
    >>> expect(foo).to_return('Foo')
    
    it fails if the callable does not return the expected value
    
    >>> def bar():
    ...     return "Barf"
    >>> expect(bar).to_return('Bar')
    Traceback (most recent call last):
        ...
    AssertionError: Expected callable to return 'Bar' but got 'Barf'
    """
    actual = self.actual()
    msg = "Expected callable to return '%s' but got '%s'" % (expected, actual)
    ensure(actual == expected, True, msg)


# Main
# ====

def main():
    """A simple wrapper that calls nosetests
    with a regex of keywords to use in discovering specs
    """
    print "\n******************** DEPRECATED *********************"
    print "\n Specit is no longer actively developed."
    print " It has been replaced with 'compare' and 'checkit' "
    print " Please see http://pypi.python.org/pypi/specit/ "
    print "\n*****************************************************\n\n"    
    return os.system('nosetests --with-doctest -i "^(Describe|it|should)" -i "(Spec[s]?)$" -i "(specs?|examples?)(.py)?$" ' + ' '.join(sys.argv[1:]))
    
if __name__ == '__main__':
    main()
