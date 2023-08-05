#    list115utils -- A115's Python List Utilities
#    Copyright (C) 2011  A115 Ltd.
#
#    This library is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this library.  If not, see <http://www.gnu.org/licenses/>.
#


from functools import partial
from itertools import chain, repeat
from operator import or_

#
# We start with the identity function. It returns 
# whatever we have passed it.  
#
ego = lambda x:x

#
# The p_true predicate returns True no matter 
# what it has been passed.  (tautology)
#
p_true = lambda x: True

#
# The p_false predicate returns False no matter 
# what it has been passed.  (contradiction)
#
p_false = lambda x: False

#
# Next we define the function composition primitive.  
# Given two functions f1 and f2, 
# compose(f1, f2) returns a new function f3 such that 
# for every x, f3(x) = f1(f2(x))
#
def compose(func, curried): 
    return lambda *args, **kwargs: \
        func(curried(*args, **kwargs))

#
# The remove_if function takes a filter function f 
# and a list l and returns a new list containing all the 
# elements of l for which the filter predicate f isn't satisfied.  
#
remove_if = lambda f, l: filter(lambda x: not(f(x)), l)

#
# The foldr ("fold right") function takes a function f, an 
# initial value and a list.  It prepends the initial value in 
# front of the list.  It then replaces the first two elements 
# of the list (a and b) with the value of f(a,b).  This step 
# is repeated until the entire list is evaluated.  
#
foldr = lambda f,i,s: reduce(f, s, i)

#
# xfoldr is a foldr factory.  Given a function f 
# and an initial value i, it returns a foldr function 
# which applies the function f to the initial value i 
# and the list passed to it.  E.g.:
# xfoldr(add, 0) returns a function equivalent to 
# python's 'sum' 
#
xfoldr = lambda f,i: lambda s: reduce(f, s, i)

# 
# map0_n applies the function f to all natural numbers 
# from 0 to n-1 and returns a list of the results. 
#
map0_n = lambda f,n: map(f, range(n))

#
# map1_n applies the function f to all natural numbers 
# from 1 to n and returns a list of the results.  
#
map1_n = lambda f,n: map(f, range(1,n+1))

#
# The empty_list iterator creates a list of N empty 
# lists.  E.g.: 
# list(empty_lists(3)) == [[],[],[]]
#
empty_lists = partial(repeat, [])

#
# The listor_ function takes a list and returns the 
# result of folding it left with the OR operator.  
#
listor_ = partial(reduce, or_)

#
# Use flatten to turn a list of lists (1-level nesting)
# into a flat list. 
# E.g. flatten([[1], [2, 3], [4, 5]]) == [1, 2, 3, 4, 5]
# But: flatten([[1], [2, [3, 4]]]) == [1, 2, [3, 4]]
#
flatten = compose(list, partial(apply, chain))

#
# Use flatten_deep to turn a list of mixed items, including 
# multi-level nested lists (deep) into a flat list. 
# E.g. flatten_deep([1, [2, 3], [4, 5]]) == [1, 2, 3, 4, 5]
# and: flatten_deep([1, [2, [3, 4]]]) == [1, 2, 3, 4]
#
def flatten_deep(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten_deep(el))
        else:
            result.append(el)
    return result

#
# The which function takes a predicate p and a list l 
# and returns the index of the first element in l which 
# matches the predicate. If no such element is found 
# in l, returns -1.  
#
def which(p,l):
    try:
        return filter(partial(lambda g,t: g(t[1]), p), 
                enumerate(l))[0][0]
    except IndexError:
        return -1

#
# subdict takes a dictionary d and a list l and returns 
# a new dictionary composed of the items in d which have 
# keys in l
#
subdict = lambda d,l: \
    {k: v for k, v in d.iteritems() if k in l}

#
# tuplify takes a list l and splits it into tuples of 
# size n
#
def tuplify(l, n=2):
	"""
	Takes a list and splits it into tuples of size n.
	""" 
	return [tuple(l[i:i+n:]) for i in range(0, len(l), n)]

#
# collides takes two lists and determines whether or not 
# they have at least one common element. 
#
collides = lambda fl,sl: any(item in sl for item in fl)

#
# Set named attributes on an object i from a dictionary d 
# only if they are in the list l
#
set_attrs_from_dict = lambda i,d,l: \
    [setattr(i, k, v) for k,v in d.iteritems() if k in l]
