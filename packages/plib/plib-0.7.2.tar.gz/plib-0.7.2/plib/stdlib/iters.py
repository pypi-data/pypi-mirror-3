#!/usr/bin/env python
"""
Module ITERS -- Tools for Iterators and Generators
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module supplements the ``itertools`` standard library
module. It currently provides the following:

function iterfile --

Returns a generator that can be used in place of "for line in file"
in cases (such as when stdin is the file) where Python's line buffering
might mean the program doesn't get the lines one at a time as they come,
but in bunches. See

http://utcc.utoronto.ca/~cks/space/blog/python/FileIteratorProblems

for a discussion of this issue and the author's code for a function that
fixes it. We use a simpler implementation here because testing has shown
that it is functionally equivalent to the author's.

Note that the issue can also arise, as the blog entry notes,
with line-oriented network protocols, which means any time you are
using a "file-like object" derived from a socket.

function first_n -- generates first n items from iterable

    >>> list(first_n(1, xrange(2)))
    [0]
    >>> list(first_n(2, xrange(2)))
    [0, 1]
    >>> list(first_n(2, xrange(3)))
    [0, 1]
    >>> list(first_n(1, []))
    []

function pairwise -- generates items from iterable in pairs

    >>> list(pairwise(xrange(3)))
    [(0, 1), (1, 2)]
    >>> list(pairwise(xrange(2)))
    [(0, 1)]
    >>> list(pairwise(xrange(1)))
    []
    >>> list(pairwise(xrange(0)))
    []

function n_wise -- generates items from iterable in n-tuples; n = 2
is equivalent to pairwise; note that n = 1 converts a list of elements
into a list of 1-tuples; also note that n = 0 raises ValueError

    >>> list(n_wise(3, xrange(4)))
    [(0, 1, 2), (1, 2, 3)]
    >>> list(n_wise(3, xrange(3)))
    [(0, 1, 2)]
    >>> list(n_wise(4, xrange(5)))
    [(0, 1, 2, 3), (1, 2, 3, 4)]
    >>> list(n_wise(4, xrange(4)))
    [(0, 1, 2, 3)]
    >>> list(n_wise(2, xrange(2)))
    [(0, 1)]
    >>> list(n_wise(2, xrange(1)))
    []
    >>> list(n_wise(2, xrange(0)))
    []
    >>> list(n_wise(1, xrange(1)))
    [(0,)]
    >>> list(n_wise(1, xrange(0)))
    []
    >>> list(n_wise(0, xrange(0)))
    Traceback (most recent call last):
    ...
    ValueError: n_wise requires n > 0
    >>> list(n_wise(0, xrange(1)))
    Traceback (most recent call last):
    ...
    ValueError: n_wise requires n > 0

function partitions -- generates all partitions of a sequence or set

    >>> list(partitions(range(3)))
    [([0], [1, 2]), ([1], [0, 2]), ([2], [0, 1])]

function subsequences -- generates all subsequences of a sequence,
from shortest to longest

    >>> list(subsequences(range(2)))
    [[0], [1], [0, 1]]
    >>> list(subsequences(range(3)))
    [[0], [1], [2], [0, 1], [1, 2], [0, 1, 2]]
    >>> list(subsequences(range(1)))
    [[0]]
    >>> list(subsequences(range(0)))
    []

function inverse_subsequences -- generates all subsequences of a sequence,
from longest to shortest

    >>> list(inverse_subsequences(range(3)))
    [[0, 1, 2], [0, 1], [1, 2], [0], [1], [2]]
    >>> list(inverse_subsequences(range(2)))
    [[0, 1], [0], [1]]
    >>> list(inverse_subsequences(range(1)))
    [[0]]
    >>> list(inverse_subsequences(range(0)))
    []

function cyclic_permutations -- generates cyclic permutations of iterable

    >>> list(cyclic_permutations(xrange(3)))
    [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
    >>> list(cyclic_permutations(xrange(2)))
    [(0, 1), (1, 0)]
    >>> list(cyclic_permutations(xrange(1)))
    [(0,)]
    >>> list(cyclic_permutations(xrange(0)))
    []

function unique_permutations -- generates cyclically unique permutations
of iterable with given length r; if r is greater than the length of
iterable, the generator is empty; if r = 0, one empty permutation is
generated (since there is only one 0-length permutation)

    >>> list(unique_permutations(xrange(2), 2))
    [(0, 1)]
    >>> list(unique_permutations(xrange(2), 3))
    []
    >>> list(unique_permutations(xrange(3), 2))
    [(0, 1), (0, 2), (1, 2)]
    >>> list(unique_permutations(xrange(3), 3))
    [(0, 1, 2), (0, 2, 1)]
    >>> list(unique_permutations(xrange(3), 4))
    []
    >>> list(unique_permutations(xrange(3), 1))
    [(0,), (1,), (2,)]
    >>> list(unique_permutations(xrange(2), 1))
    [(0,), (1,)]
    >>> list(unique_permutations(xrange(1), 1))
    [(0,)]
    >>> list(unique_permutations(xrange(1), 2))
    []
    >>> list(unique_permutations(xrange(0), 1))
    []
    >>> list(unique_permutations(xrange(0), 0))
    [()]
    >>> list(unique_permutations(xrange(1), 0))
    [()]
    >>> list(unique_permutations(xrange(2), 0))
    [()]
    >>> list(unique_permutations(xrange(3), 0))
    [()]

function unique_permutations_with_replacement -- generates cyclically
unique permutations of iterable where repeated elements are allowed

    >>> list(unique_permutations_with_replacement(xrange(2), 2))
    [(0, 0), (0, 1), (1, 1)]
    >>> list(unique_permutations_with_replacement(xrange(2), 3))
    [(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1)]
    >>> list(unique_permutations_with_replacement(xrange(2), 1))
    [(0,), (1,)]
    >>> list(unique_permutations_with_replacement(xrange(1), 1))
    [(0,)]
    >>> list(unique_permutations_with_replacement(xrange(1), 2))
    [(0, 0)]
    >>> list(unique_permutations_with_replacement(xrange(1), 0))
    [()]

function partition -- splits a sequence into multiple sequences at
given index (index must be > 0, otherwise ValueError is raised); if
the ``complete`` argument is ``False``, only partition once

    >>> partition(range(4), 2)
    ([0, 1], [2, 3])
    >>> partition(range(4), 3)
    ([0, 1, 2], [3])
    >>> partition(range(4), 4)
    ([0, 1, 2, 3],)
    >>> partition(range(4), 5)
    ([0, 1, 2, 3],)
    >>> partition(range(6), 2)
    ([0, 1], [2, 3], [4, 5])
    >>> partition(range(6), 3)
    ([0, 1, 2], [3, 4, 5])
    >>> partition(range(6), 4)
    ([0, 1, 2, 3], [4, 5])
    >>> partition(range(6), 5)
    ([0, 1, 2, 3, 4], [5])
    >>> partition(range(6), 6)
    ([0, 1, 2, 3, 4, 5],)
    >>> partition(range(6), 7)
    ([0, 1, 2, 3, 4, 5],)
    >>> partition(range(4), 1)
    ([0], [1], [2], [3])
    >>> partition(range(1), 1)
    ([0],)
    >>> partition(range(1), 2)
    ([0],)
    >>> partition(range(0), 1)
    ([],)
    >>> partition(range(0), 2)
    ([],)
    >>> partition(range(1), 0)
    Traceback (most recent call last):
    ...
    ValueError: can't partition sequence at index 0
    >>> partition(range(0), 0)
    Traceback (most recent call last):
    ...
    ValueError: can't partition sequence at index 0
    >>> partition(range(3), 1, complete=False)
    ([0], [1, 2])
    >>> partition(range(2), 1, complete=False)
    ([0], [1])
    >>> partition(range(5), 2, complete=False)
    ([0, 1], [2, 3, 4])
    >>> partition(range(4), 2, complete=False)
    ([0, 1], [2, 3])

function unzip -- inverse of the zip builtin, splits sequence of tuples
into multiple sequences

    >>> unzip(zip(xrange(3), xrange(3)))
    ([0, 1, 2], [0, 1, 2])
    >>> unzip(zip(xrange(3), xrange(3), xrange(3)))
    ([0, 1, 2], [0, 1, 2], [0, 1, 2])
    >>> unzip(zip(xrange(1), xrange(1)))
    ([0], [0])
    >>> unzip(zip(xrange(0), xrange(0)))
    []
    >>> unzip(xrange(1))
    Traceback (most recent call last):
     ...
    TypeError: object of type 'int' has no len()

function exrange -- version of xrange builtin that works with longs

    >>> list(exrange(2147483647, 2147483649))
    [2147483647, 2147483648L]
    >>> list(exrange(2147483647, 2147483651, 2))
    [2147483647, 2147483649L]
    >>> list(exrange(2147483647, 2147483649, 0))
    Traceback (most recent call last):
     ...
    ValueError: exrange() arg 3 must not be zero

function inverse_index -- index of item counting from end of sequence

    >>> inverse_index(range(3), 0)
    2
    >>> inverse_index(range(3), 1)
    1
    >>> inverse_index(range(3), 2)
    0
    >>> inverse_index(range(3), 3)
    Traceback (most recent call last):
     ...
    ValueError: list.index(x): x not in list

function is_subsequence -- tests if one sequence is subsequence of another

    >>> is_subsequence(range(2), range(3))
    True
    >>> is_subsequence(range(2), range(1, 3))
    False
    >>> is_subsequence(range(1, 2), range(1, 3))
    True
    >>> is_subsequence(range(1), range(2))
    True
    >>> is_subsequence(range(1), range(1, 2))
    False
    >>> is_subsequence(range(0), range(1))
    True
    >>> is_subsequence(range(0), range(0))
    True
    >>> is_subsequence(range(3), range(2))
    False
    >>> is_subsequence(range(1), range(0))
    False

function count_matches -- returns mapping of unique elements in sequence
to number of times they appear

    >>> count_matches(range(1))
    {0: 1}
    >>> count_matches(range(2))
    {0: 1, 1: 1}
    >>> count_matches(range(2) * 2)
    {0: 2, 1: 2}
    >>> count_matches(range(2) * 2 + [2])
    {0: 2, 1: 2, 2: 1}
    >>> count_matches(range(0))
    {}
    >>> count_matches('abracadabra')
    {'a': 5, 'c': 1, 'r': 2, 'b': 2, 'd': 1}

function sorted_unzip -- returns two sequences from mapping, of keys and
values, in corresponding order, sorted by key or value

    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)))
    ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)), by_value=True)
    ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)), reverse=True)
    ([4, 3, 2, 1, 0], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)), by_value=True, reverse=True)
    ([4, 3, 2, 1, 0], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)))
    ([0, 1, 2, 3, 4], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)), by_value=True)
    ([4, 3, 2, 1, 0], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)), reverse=True)
    ([4, 3, 2, 1, 0], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)), by_value=True, reverse=True)
    ([0, 1, 2, 3, 4], ['e', 'd', 'c', 'b', 'a'])
"""

import sys
from itertools import *
from operator import lt, gt

from plib.stdlib.imp import dotted_from_import

# Add alternate implementations of newer itertools functions
# for older versions of Python

imp_names = (
    'combinations',
    'combinations_with_replacement',
    'permutations',
    'permutations_with_replacement',
    'product'
)

thismod = sys.modules[__name__]
for fname in imp_names:
    if not hasattr(thismod, fname):
        f = dotted_from_import('plib.stdlib._iters', fname)
        setattr(thismod, fname, f)
del f, thismod, dotted_from_import


# File iterator utility

def iterfile(f):
    """Return a generator that yields lines from a file.
    
    This works like "for line in file" does, but avoids potential
    problems with buffering. Use as::
    
        for line in iterfile(file):
    """
    return iter(f.readline, '')


# Iterable functions

def first_n(n, iterable):
    # More intuitive spelling for this usage of islice
    return islice(iterable, n)


def pairwise(iterable):
    # s -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def n_wise(n, iterable):
    # Return items from iterable in groups of n
    if n <= 0:
        raise ValueError, "n_wise requires n > 0"
    iters = []
    a = iterable
    for _ in xrange(n - 1):
        a, b = tee(a)
        iters.append(a)
        next(b, None)
        a = b  # this makes sure append(a) below gets the right iterable
    iters.append(a)  # this takes care of the n = 1 case as well
    return izip(*iters)


def partitions(s):
    # Generate all pairs of non-empty subsets that partition s
    itemcount = len(s)
    for n in xrange(1, (itemcount / 2) + 1):
        for indexes in combinations(xrange(itemcount), n):
            p = [s[i] for i in indexes]
            o = [s[j] for j in xrange(itemcount) if j not in indexes]
            yield p, o


def _subseq(sequence, step=0):
    length = len(sequence)
    indexes = (0, length)
    start = indexes[step] + 1 + step
    stop = indexes[1 + step] + 1 + step
    step = step or 1
    for current in xrange(start, stop, step):
        for i in xrange(length - current + 1):
            yield sequence[i:i + current]


def subsequences(sequence):
    # Generate all subsequences of sequence, starting with
    # the shortest and ending with the sequence itself
    return _subseq(sequence)


def inverse_subsequences(sequence):
    # Generate all subsequences of sequence, starting with
    # the longest (which is just the sequence itself)
    return _subseq(sequence, -1)


def cyclic_permutations(iterable):
    # Generate just the cyclic permutations of iterable
    # (all permutations are the same length as iterable)
    # cyclic_permutations('123') -> '123', '231', '312'
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    r = len(pool)
    s = pool + pool
    for i in xrange(r):
        p = s[i:i + r]
        if p not in seen:
            seen[p] = p
            yield p


def unique_permutations(iterable, r):
    # Generate all cyclically unique r-length permutations of iterable
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    for c in combinations(pool, r):
        car, cdr = c[:1], c[1:]
        for p in permutations(cdr):
            u = car + p
            if u not in seen:
                for t in cyclic_permutations(u):
                    seen[t] = u
                yield u


def unique_permutations_with_replacement(iterable, r):
    # Generate all cyclically unique r-length permutations of iterable,
    # where elements can be repeated
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    s = len(pool)
    for i in xrange(min(r, s) + 1):
        for c in combinations(pool, i):
            for p in combinations_with_replacement(pool, r - i):
                for u in unique_permutations(c + p, r):
                    if u not in seen:
                        for t in cyclic_permutations(u):
                            seen[t] = u
                        yield u


def partition(seq, at, complete=True):
    # Return two or more sequences, split from seq at given index
    # If complete is True and seq is longer than 2 * at, partition
    # multiple times; otherwise only partition once (i.e., into
    # two sequences)
    if at <= 0:
        raise ValueError, "can't partition sequence at index 0"
    results = []
    while at < len(seq):
        results.append(seq[:at])
        seq = seq[at:]
        if not complete:
            break
    results.append(seq)
    return tuple(results)


def unzip(seq):
    # Unzip seq into multiple sequences; assumes seq contains tuples
    # that are all of the same length. Empty sequences are returned
    # unchanged.
    if not seq:
        return seq
    num = len(seq[0])
    results = []
    for _ in xrange(num):
        results.append([])
    for items in seq:
        for i in xrange(num):
            results[i].append(items[i])
    return tuple(results)


def exrange(start, stop, step=1):
    # xrange that works with Python long ints
    if step == 0:
        raise ValueError, "exrange() arg 3 must not be zero"
    if step < 0:
        cmpfn = gt
    else:
        cmpfn = lt
    i = start
    while cmpfn(i, stop):
        yield i
        i += step


# Test and count functions

def inverse_index(seq, elem):
    # Return inverse index of elem in seq (i.e., first element
    # of seq has highest index, down to 0 for last element)
    return len(seq) - seq.index(elem) - 1


def is_subsequence(s, seq):
    # Test if s is a subsequence of seq
    slen = len(s)
    for i in xrange(len(seq) - slen + 1):
        if s == seq[i:i + slen]:
            return True
    return False


# Mapping <=> sequence functions

def count_matches(seq):
    # Return dict of unique elements in seq vs. number of times they appear
    # Assumes all sequence elements are hashable
    results = {}
    for item in seq:
        results.setdefault(item, []).append(True)
    return dict((k, len(v)) for k, v in results.iteritems())


def sorted_unzip(mapping, by_value=False, reverse=False):
    # Return list of keys and list of values from mapping, both
    # sorted in corresponding order, by values if by_value is
    # True, by keys otherwise; reverse parameter governs the sort
    if by_value:
        unsorted_result = list((v, k) for k, v in mapping.iteritems())
    else:
        unsorted_result = list(mapping.iteritems())
    result = sorted(unsorted_result, reverse=reverse)
    r1, r2 = unzip(result)
    if by_value:
        return r2, r1
    return r1, r2


if __name__ == '__main__':
    import doctest
    doctest.testmod()
