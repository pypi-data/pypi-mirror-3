'''
python-algebraic
================
:Author: Ryan J. O'Neil <ryanjoneil@gmail.com>
:Version: 0.3.1-beta
:Website: https://github.com/rzoz/python-algebraic

This library allows use of symbolic algebra against Python objects for
describing decision variables, constraints, and objective function.  Its goal
is to provide a unified modeling interface for access to optimization solvers
in Python.

License
-------
This software is released under the Simplified BSD License.
'''

from algebraic.variable import variable

__version__ = '0.3.1'
__all__ = 'variable',
