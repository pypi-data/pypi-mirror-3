#!/usr/bin/env python
"""
Module OPTIONS -- Option Parser Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a utility function for option parsers, to
reduce the amount of work needed to make use of the optparse
library module. Instead of having to manually instantiate an
option parser, add options to it, then call its parsing method,
the parse_options function wraps it all into one package; you
give it a list of option parameters and arguments and it
returns the parsed (options, args) tuple. This also allows
adding extra functionality:

- Argument checking: a list of arguments can be passed
  to the ``parse_options`` function, to allow display of
  expected arguments in the help, and to check that the correct
  number of arguments are present in the command line (or, if
  the ``argparse`` module is present, in Python 2.7 and later,
  additional argument checking functionality can be used);

- Option dictionary: the options object (the first element of
  the 2-tuple returned by ``parse_options``) supports an
  immutable mapping interface, using the destination variable
  names passed in the option list as keys. This makes it
  easier to use the options to update other data structures
  in the program (see the gui-display.py example program for
  an illustration of this usage), as well as accessing the
  options directly as attributes of the options object.

- Argument sequence: the arguments object (the second element
  of the 2-tuple returned by ``parse_options``) supports a
  sequence interface; an argument's index in the sequence is
  equal to its index in the list of arguments passed to the
  ``parse_options`` function. This allows easy iteration over
  arguments, as well as accessing them by name directly as
  attributes of the arguments object.
"""

try:
    import argparse
    using_argparse = True
except ImportError:
    import optparse
    using_argparse = False

import os
import new
from itertools import imap, izip

from plib.stdlib import AttrDelegate, AttrDict, AttrList


def _canonicalize_arg(arg):
    if isinstance(arg, basestring):
        return (arg.lower(), {'metavar': arg.upper()})
    return arg


def _canonicalize_args(arglist):
    if isinstance(arglist, basestring):
        import warnings
        warnings.warn("A single string as an argument definition is deprecated; use a one-element list instead.",
            DeprecationWarning)
        arglist = [arglist]
    return [_canonicalize_arg(arg) for arg in arglist]


def _optnames(optlist):
    return [optitem[2]['dest'] for optitem in optlist]


def _argnames(arglist):
    return [argitem[0] for argitem in arglist]


if using_argparse:
    # New API for Python 2.7 and later
    
    def _get_parser(optlist, arglist, description, epilog):
        parser = argparse.ArgumentParser(
            description=description, epilog=epilog)
        for shortopt, longopt, kwargs in optlist:
            parser.add_argument(shortopt, longopt, **kwargs)
        for argname, kwargs in arglist:
            parser.add_argument(argname, **kwargs)
        return parser
    
    
    def _make_ns(names, items):
        ns = argparse.Namespace()
        for name in names:
            setattr(ns, name, getattr(items, name))
        return ns
    
    
    def _invoke_parser(parser, optlist, arglist):
        result = parser.parse_args()
        opts = _make_ns(_optnames(optlist), result)
        args = _make_ns(_argnames(arglist), result)
        return opts, args


else:
    # Old API -- note that we need to test for the "epilog" parameter
    # so we can monkeypatch it in for older versions where it wasn't present
    
    from itertools import izip
    
    if ('epilog' in optparse.OptionParser.__init__.im_func.func_code.co_varnames):
        _parser_factory = optparse.OptionParser
    
    else:
        
        def _parser_factory(usage, description=None, epilog=None):
            # This is an evil hack, but it only kicks in for versions too old
            # to have the epilog parameter built in, so the potential damage
            # is hopefully limited... ;-)
            _parser = optparse.OptionParser(usage, description=description)
            _parser.epilog = epilog
            _parser._old_format_help = _parser.format_help
            def format_help(self, formatter=None):
                result = self._old_format_help(formatter)
                if formatter is None:
                    formatter = self.formatter
                if self.epilog:
                    result = "".join([
                        result,
                        os.linesep,
                        formatter.format_description(self.epilog)])
                return result
            _parser.format_help = new.instancemethod(format_help,
                _parser, _parser.__class__)
            return _parser
    
    
    # Usage format string -- optparse will replace the %prog
    usage = "usage: %prog [options]"
    
    
    def _get_parser(optlist, arglist, description, epilog):
        global usage
        if arglist:
            argstring = " ".join(imap(str,
                (argitem[1]['metavar'] for argitem in arglist)))
            usage = " ".join([usage, argstring])
        
        parser = _parser_factory(usage,
            description=description, epilog=epilog)
        for shortopt, longopt, kwargs in optlist:
            parser.add_option(shortopt, longopt, **kwargs)
        return parser
    
    
    class Namespace(object):
        # Dummy class to hold args as named attributes
        pass
    
    
    def _invoke_parser(parser, optlist, arglist):
        opts, oldargs = parser.parse_args()
        required_arglist = [arg for arg in arglist
            if isinstance(arg, tuple) and not ("default" in arg[1])]
        optional_arglist = [arg for arg in arglist
            if isinstance(arg, tuple) and ("default" in arg[1])]
        l1 = len(oldargs)
        l2 = len(required_arglist)
        l3 = len(arglist)
        if (l1 < l2):
            parser.error(
                "Invalid arguments: %i received, at least %i expected." % (l1, l2))
        if (l1 > l3):
            parser.error(
                "Invalid arguments: %i received, at most %i expected." % (l1, l3))
        args = Namespace()
        for name, oldarg in izip(_argnames(required_arglist), oldargs[:l2]):
            setattr(args, name, oldarg)
        for name, oldarg in izip(_argnames(optional_arglist), oldargs[l2:]):
            setattr(args, name, oldarg)
        for name, kwargs in optional_arglist:
            if not hasattr(args, name):
                setattr(args, name, kwargs['default'])
        return opts, args


def parse_options(optlist, arglist=[],
                  description=None, epilog=None):
    """Convenience function for option and argument parsing.
    
    Adds each option in optlist and each argument in arglist to the parser
    and then return the parsing results.
    
    Parameters:
    
        - ``optlist``: a sequence of 3-tuples: short name, long name,
          dict of keyword arguments.
        
        - ``arglist``: either a sequence of strings which are interpreted
          as argument names, or a sequence of 2-tuples: argument name,
          dict of keyword arguments. The latter form is the "canonical"
          form into which the former will be converted; in that case, each
          2-tuple is then simply the arg name and a dict with a single
          key, 'metavar', mapped to the arg name as its value (note,
          though, that arg names are always lowercased and metavar names
          are always uppercased in this mode).
    
    Note that on Python 2.6 and earlier, when the ``argparse`` standard
    library module is not present, the only checking done on arguments
    is to verify that the correct number of arguments is present.
    """
    
    arglist = _canonicalize_args(arglist)
    parser = _get_parser(optlist, arglist, description, epilog)
    opts, args = _invoke_parser(parser, optlist, arglist)
    opts = AttrDict(_optnames(optlist), opts)
    args = AttrList(_argnames(arglist), args)
    return opts, args
