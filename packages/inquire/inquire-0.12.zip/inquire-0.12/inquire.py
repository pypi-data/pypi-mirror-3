"""
LINQ-style query implementation for Python.

"We don't need no expression trees 'round these parts!"
"""

__author__ = "Tony Young <rofflwaffls@gmail.com>"
__version__ = "0.12"

import operator
from itertools import chain, count, dropwhile, islice, izip, takewhile, tee

def _as_is(x):
    """
    Return argument as-is.

    >>> _as_is(1)
    1

    @return: The argument.
    """
    return x

def _as_is_packed(*x):
    """
    Return all arguments packed in a tuple.

    >>> _as_is_packed(1, 2, 3)
    (1, 2, 3)

    @return: The arguments, packed in a tuple.
    """
    return x

def _as_true(*x):
    """
    Return True, regardless of input.

    >>> _as_true(False)
    True

    @return: C{True}.
    """
    return True

class Query(object):
    """
    The basic query object of inquire.

    >>> list(Query([1, 2, 3]))
    [1, 2, 3]
    """

    ############################################################################
    # Filtering
    ############################################################################
    def where(self, predicate):
        """
        Filter a container using a predicate.

        >>> list(Query(["apple", "almond", "banana"]).where(lambda x: x.startswith("a")))
        ['apple', 'almond']

        @param predicate: Function specifying a condition for a value.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(item for item in self if predicate(item))

    ############################################################################
    # Projection
    ############################################################################
    def select(self, selector):
        """
        Select an element from a container using a selector.

        >>> list(Query(["apple", "almond", "banana"]).select(len))
        [5, 6, 6]

        @param selector: Function to use when selecting results.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(selector(item) for item in self)

    def _select_many(self, selector):
        """
        Internal L{select_many} implementation.
        """
        for elem in self:
            for subelem in elem:
                yield selector(subelem)

    def select_many(self, selector):
        """
        Select nested elements from a container.

        >>> "".join(list(Query(["apple", "almond", "banana"]).select_many(lambda x: x)))
        'applealmondbanana'

        @param selector: Function to use when selecting results.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._select_many(selector))

    ############################################################################
    # Ordering
    ############################################################################
    def _order_by(self, key_selector):
        """
        Internal L{order_by} implementation.
        """
        for elem in sorted(self, key=key_selector):
            yield elem

    def order_by(self, key_selector=_as_is):
        """
        Order an iterable by key selector.

        >>> list(Query([5, 1, 2, 4, 8, 3]).order_by())
        [1, 2, 3, 4, 5, 8]

        >>> list(Query(["monster", "dog", "cat", "apple"]).order_by(len))
        ['dog', 'cat', 'apple', 'monster']

        @param key_selector: Function to use to select the key.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._order_by(key_selector))

    def _reverse(self):
        """
        Internal L{reverse} implementation.
        """
        for elem in reversed(list(self)):
            yield elem

    def reverse(self):
        """
        Reverse an iterable.

        >>> list(Query([1, 2, 3, 4, 5]).reverse())
        [5, 4, 3, 2, 1]

        @return: The reversed iterable.
        @note: Supports deferred execution.
        """
        return Query(self._reverse())

    ############################################################################
    # Aggregation
    ############################################################################
    def aggregate(self, aggregator, initial=0):
        """
        Build a return value by iterating over an iterable (right fold).

        >>> Query([1, 2, 3, 4, 5, 6]).aggregate(operator.add)
        21

        >>> Query([1, 2, 3, 4, 5, 6]).aggregate(lambda acc, x: acc + str(x), "")
        '123456'

        @param aggregator: The function to use to combine the iterable.
        @return: Reduced iterable.
        """
        return reduce(aggregator, self, initial)

    def average(self):
        """
        Return the numerical average of the iterable.

        >>> Query([1, 2, 3, 4, 5]).average()
        3.0

        @return: The average.
        """
        total = 0

        for i, v in enumerate(self):
            total += v
        return total / float(i + 1)

    def sum(self):
        """
        Synonym for C{Query.aggregate(operator.add)}.

        >>> Query([1, 2, 3, 4, 5]).sum()
        15

        @return: The sum of the iterable.
        """
        return reduce(operator.add, self)

    def count(self):
        """
        Return the number of elements in an iterable.

        >>> Query([1, 2, 3, 4]).count()
        4

        @return: The number of elements in the iterable.
        """
        iterator = iter(self)
        for i in count():
            try:
                iterator.next()
            except StopIteration:
                return i

    def max(self, selector=_as_is):
        """
        Get the maximum of all elements in the iterable.

        >>> Query([1, 2, 3]).max()
        3

        @param selector: Function to use when selecting a value.
        @return: The maximum element.
        """
        return max(self, key=selector)

    def min(self, selector=_as_is):
        """
        Get the minimum of all elements in the iterable.

        >>> Query([1, 2, 3]).min()
        1

        @param selector: Function to use when selecting a value.
        @return: The minimum element.
        """
        return min(self, key=selector)

    ############################################################################
    # Set
    ############################################################################
    def _union(self, other, comparer=operator.eq):
        """
        Internal L{union} implementation.
        """
        present = set([])

        for elem in chain(self, other):
            skip = False
            for item in present:
                if comparer(elem, item):
                    skip = True
                    break
            if skip: continue
            present.add(elem)
            yield elem

    def union(self, other):
        """
        Get the distinct elements of two iterables.

        >>> list(Query([1, 2, 3]).union([3, 4, 5]))
        [1, 2, 3, 4, 5]

        @param other: Iterable to perform a union with.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._union(other))

    def _difference(self, other, comparer):
        """
        Internal L{difference} implementation.
        """
        for elem in self:
            skipping = False
            for item in other:
                if comparer(elem, item):
                    skipping = True
                    break
            if skipping: continue
            yield elem

    def difference(self, other, comparer=operator.eq):
        """
        Get the set difference of two iterables using the specified equality
        comparer.

        >>> list(Query([1, 2, 3]).difference([2, 3, 4]))
        [1]

        >>> list(Query([1, 2, 3]).difference([1, 2, 3]))
        []

        @param other: The other iterable.
        @param comparer: Function used to compare the equality of two elements.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._difference(other, comparer))

    def _distinct(self, comparer):
        """
        Internal L{distinct} implementation.
        """
        present = set([])

        for elem in self:
            skip = False
            for item in present:
                if comparer(elem, item):
                    skip = True
                    break
            if skip: continue
            present.add(elem)
            yield elem

    def distinct(self, comparer=operator.eq):
        """
        Get only the distinct elements of the iterable.

        >>> list(Query([1, 1, 2, 3, 3]).distinct())
        [1, 2, 3]

        @param comparer: Function to use when comparing two elements.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._distinct(comparer))

    def _intersect(self, other, comparer):
        """
        Internal L{intersect} implementation.
        """
        for elem in self:
            using = False
            for item in other:
                if comparer(elem, item):
                    using = True
                    break
            if using: yield elem

    def intersect(self, other, comparer=operator.eq):
        """
        Get the set intersection of two iterables using the specified equality
        comparer.

        >>> list(Query([1, 2, 3]).intersect([2, 3, 4]))
        [2, 3]

        >>> list(Query([1, 2, 3]).intersect([4, 5, 6]))
        []

        @param other: The other iterable.
        @param comparer: Function used to compare the equality of two elements.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._intersect(other, comparer))

    ############################################################################
    # Convolution
    ############################################################################
    def zip(self, other, zipper=_as_is_packed):
        """
        Join two iterables together by combining one element with another.

        >>> list(Query([1, 2, 3]).zip([4, 5, 6], operator.add))
        [5, 7, 9]

        @param other: Iterable to zip with.
        @param zipper: Function to use when combining elements,
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(zipper(*elem) for elem in izip(self, other))

    ############################################################################
    # Concatenation
    ############################################################################
    def concat(self, other):
        """
        Join two iterables together, one after the other.

        >>> list(Query([1, 2]).concat([3, 4]))
        [1, 2, 3, 4]

        @param other: Iterable to concatenate.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(chain(self, other))

    ############################################################################
    # Qualification
    ############################################################################
    def any(self, predicate=_as_is):
        """
        Check if any element in the iterable meets a condition.

        >>> Query([ True, False, False ]).any()
        True

        >>> Query([ False, False ]).any()
        False

        @param predicate: Function specifying a condition for a value.
        @return: C{True} or C{False}.
        """
        return any(predicate(elem) for elem in self)

    def all(self, predicate=_as_is):
        """
        Check if all elements in the iterable meets a condition.

        >>> Query([ True, False, False ]).all()
        False

        >>> Query([ True, True ]).all()
        True

        @param predicate: Function specifying a condition for a value.
        @return: C{True} or C{False}.
        """
        return all(predicate(elem) for elem in self)

    def contains(self, item, comparer=operator.eq):
        """
        Check if an item exists in an iterable.

        >>> Query([1, 2, 3]).contains(2, lambda x, y: x == y + 1)
        True

        >>> Query([1, 2, 3]).contains(4)
        False

        @param item: Item to check for.
        @param comparer: Function to use for comparing equality.
        @return: C{True} or C{False}.
        """
        for elem in self:
            if comparer(elem, item):
                return True
        return False

    ############################################################################
    # Equality
    ############################################################################
    def sequence_equal(self, other, comparer=operator.eq):
        """
        Check if two iterables are equal to each other.

        >>> Query([1, 2, 3, 4, 5]).sequence_equal([1, 2, 3, 4, 5], operator.eq)
        True

        >>> Query([1, 2, 3, 4]).sequence_equal([1, 2, 3, 4, 5], operator.eq)
        False

        >>> Query([1, 2, 3, 4, 5]).sequence_equal([1, 2, 3, 4], operator.eq)
        False

        >>> Query([True, False, None]).sequence_equal([True, False, None], operator.is_)
        True

        @param other: Iterable to check equality with.
        @param comparer: Function to use for comparing equality.
        @return: C{True} or C{False}.
        """
        self_iter = iter(self)
        other_iter = iter(other)

        while True:
            try:
                self_value = self_iter.next()
            except StopIteration:
                try:
                    other_value = other_iter.next()
                except StopIteration:
                    return True
                else:
                    return False
            else:
                try:
                    other_value = other_iter.next()
                except StopIteration:
                    return False
                else:
                    if not comparer(self_value, other_value): return False

    ############################################################################
    # Partitioning
    ############################################################################
    def take_while(self, predicate=_as_is):
        """
        Take elements from the iterable while a condition is met.

        >>> list(Query([1, 2, 3, 4, 5]).take_while(lambda x: x < 4))
        [1, 2, 3]

        @param predicate: Function specifying a condition to meet.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(takewhile(predicate, self))

    def skip_while(self, predicate=_as_is):
        """
        Skip elements in the iterable while a condition is met.

        >>> list(Query([1, 2, 3, 4, 5]).skip_while(lambda x: x < 4))
        [4, 5]

        @param predicate: Function specifying a condition to meet.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(dropwhile(predicate, self))

    def take(self, num):
        """
        Take the first few elements of an iterable.

        >>> list(Query([1, 2, 3, 4]).take(2))
        [1, 2]

        @param num: Number of elements to take.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(islice(self, None, num))

    def skip(self, num):
        """
        Skip the first few elements of an iterable.

        >>> list(Query([1, 2, 3, 4]).skip(2))
        [3, 4]

        @param num: Number of elements to skip.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(islice(self, num, None))

    ############################################################################
    # Elements
    ############################################################################
    def not_empty_or(self, value=None):
        """
        Return the iterable if it contains items, otherwise return C{value}.

        >>> list(Query([1]).not_empty_or(None))
        [1]

        >>> Query([]).not_empty_or(2)
        2

        @param value: Value to return if the iterable is empty.
        @return: The iterable or C{value}.
        """
        for elem in self:
            return self
        return value

    def single(self, predicate=_as_is):
        """
        Return the only element in an iterable that matches the predicate,
        otherwise raise an exception if not.

        >>> Query([1, 2]).single(lambda x: x == 1)
        1

        >>> Query([1, 2]).single()
        Traceback (most recent call last):
        ...
        ValueError: more than one element matches predicate

        >>> Query([]).single()
        Traceback (most recent call last):
        ...
        ValueError: no elements match predicate

        @param predicate: Function specifying a condition for a value.
        @return: The item.
        """
        has_result = False

        for elem in self:
            if predicate(elem):
                if not has_result:
                    result = elem
                    has_result = True
                else:
                    raise ValueError("more than one element matches predicate")

        if not has_result:
            raise ValueError("no elements match predicate")

        return result

    def single_or(self, predicate=_as_is, value=None):
        """
        Return the only element in an iterable that matches the predicate,
        otherwise return C{value}.

        >>> Query([1, 2]).single_or(lambda x: x == 1, value=3)
        1

        >>> Query([1, 2]).single_or(value=3)
        3

        >>> Query([]).single_or(value=3)
        3

        @param predicate: Function specifying a condition for a value.
        @param value: Value to return if nothing matches the predicate.
        @return: The item or C{value}.
        """
        has_result = False

        for elem in self:
            if predicate(elem):
                if not has_result:
                    result = elem
                    has_result = True
                else:
                    return value

        if not has_result:
            return value

        return result

    def element_at(self, index):
        """
        Get the element at a specific index of the iterable.

        >>> Query([1, 2, 3]).element_at(1)
        2

        >>> Query([1, 2, 3]).element_at(4)
        Traceback (most recent call last):
        ...
        IndexError: index out of range

        @param index: The index.
        @return: The value at the index.
        """
        iterator = iter(self)
        try:
            for i in xrange(index):
                iterator.next()
            return iterator.next()
        except StopIteration:
            raise IndexError("index out of range")

    def element_at_or(self, index, value=None):
        """
        Get the element at a specific index of the iterable or return C{value}
        if the index is not in the iterable.

        >>> Query([1, 2, 3]).element_at_or(1, 4)
        2

        >>> Query([1, 2, 3]).element_at_or(4, 4)
        4

        @param index: The index.
        @param value: Value to return if specified index does not exist.
        @return: The value at the index or C{value}.
        """
        iterator = iter(self)
        try:
            for i in xrange(index):
                iterator.next()
            return iterator.next()
        except StopIteration:
            return value

    def first(self, predicate=_as_is):
        """
        Get the first element that matches the predicate.

        >>> Query(["cat", "dog", "moose"]).first(lambda x: len(x) == 3)
        'cat'

        >>> Query(["cat", "dog", "moose"]).first(lambda x: len(x) == 4)
        Traceback (most recent call last):
        ...
        ValueError: no elements match the predicate

        @param predicate: Function specifying a condition for a value.
        @return: The item.
        """
        for elem in self:
            if predicate(elem):
                return elem
        raise ValueError("no elements match the predicate")

    def first_or(self, predicate=_as_is, value=None):
        """
        Get the first element that matches the predicate or return C{value} if
        none are found.

        >>> Query(["cat", "dog", "moose"]).first_or(lambda x: len(x) == 3, "deer")
        'cat'

        >>> Query(["cat", "dog", "moose"]).first_or(lambda x: len(x) == 4, "deer")
        'deer'

        @param predicate: Function specifying a condition for a value.
        @param value: Value to return if nothing matches the predicate.
        @return: The item or C{value}.
        """
        for elem in self:
            if predicate(elem):
                return elem
        return value

    def last(self, predicate=_as_is):
        """
        Get the last element that matches the predicate.

        >>> Query(["cat", "dog", "moose"]).last(lambda x: len(x) == 3)
        'dog'

        >>> Query(["cat", "dog", "moose"]).last(lambda x: len(x) == 4)
        Traceback (most recent call last):
        ...
        ValueError: no elements match the predicate

        @param predicate: Function specifying a condition for a value.
        @return: The item.
        """
        matches = []

        for elem in self:
            if predicate(elem):
                matches.append(elem)

        if matches:
            return matches[-1]
        raise ValueError("no elements match the predicate")

    def last_or(self, predicate=_as_is, value=None):
        """
        Get the last element that matches the predicate or return C{value} if
        none are found.

        >>> Query(["cat", "dog", "moose"]).last_or(lambda x: len(x) == 3, "deer")
        'dog'

        >>> Query(["cat", "dog", "moose"]).last_or(lambda x: len(x) == 4, "deer")
        'deer'

        @param predicate: Function specifying a condition for a value.
        @param value: Value to return if nothing matches the predicate.
        @return: The item or C{value}.
        """
        matches = []

        for elem in self:
            if predicate(elem):
                matches.append(elem)

        if matches:
            return matches[-1]
        return value

    ############################################################################
    # Join
    ############################################################################
    def _inner_join(
        self,
        inner,
        outer_key_selector,
        inner_key_selector,
        result_selector,
        comparer
    ):
        """
        Internal L{join} implementation.
        """
        inners = {}

        for elem in inner:
            inners[inner_key_selector(elem)] = elem

        for elem in self:
            outer_key = outer_key_selector(elem)
            for inner_key in inners:
                if comparer(inner_key, outer_key):
                    yield result_selector(elem, inners[inner_key])

    def inner_join(
        self,
        inner,
        outer_key_selector,
        inner_key_selector,
        result_selector=_as_is_packed,
        comparer=operator.eq
    ):
        """
        Perform an inner join between two iterables.

        >>> list(Query([(1, "cake"), (2, "cat")]).inner_join(
        ...     [(1, "delicious"), (2, "meow")],
        ...     operator.itemgetter(0),
        ...     operator.itemgetter(0),
        ...     lambda x, y: (x[1], y[1])
        ... ))
        [('cake', 'delicious'), ('cat', 'meow')]

        >>> list(Query([(1, "cake"), (2, "cat")]).inner_join(
        ...     [(3, "yuck"), (4, "woof")],
        ...     operator.itemgetter(0),
        ...     operator.itemgetter(0),
        ...     lambda x, y: (x[1], y[1])
        ... ))
        []

        @param inner: The inner iterable to join with.
        @param outer_key_selector: Function used to select the key from this
                                   iterable.
        @param inner_key_selector: Function used to select the key from the
                                   inner iterable.
        @param result_selector: Function used to select the result.
        @param comparer: Function used to compare equality of keys.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._inner_join(
            inner,
            outer_key_selector,
            inner_key_selector,
            result_selector,
            comparer
        ))

    ############################################################################
    # Grouping
    ############################################################################
    def _group_by(self, key_selector, element_selector, comparer):
        """
        Internal L{group_by} implementation.
        """
        groups = {}
        for elem in self:
            appended = False
            key = key_selector(elem)
            for group_key in groups:
                if comparer(key, group_key):
                    groups[key].append(element_selector(elem))
                    appended = True
                    break
            if not appended:
                groups[key] = [ element_selector(elem) ]

        for group in groups.iteritems():
            yield group

    def group_by(
        self,
        key_selector,
        element_selector=_as_is,
        comparer=operator.eq
    ):
        """
        Group an iterable by key.

        >>> dict(Query(["cat", "dog", "elmo"]).group_by(len))
        {3: ['cat', 'dog'], 4: ['elmo']}

        @param key_selector: Function used to select the key.
        @param element_selector: Function used to select the element.
        @param comparer: Function used to compare the equality of two keys.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._group_by(key_selector, element_selector, comparer))

    ############################################################################
    # Overrides
    ############################################################################
    def __new__(cls, iterable):
        """
        Create a new Query object, only if the provided iterable is not already
        wrapped with Query.

        >>> list(Query([1, 2, 3]))
        [1, 2, 3]

        >>> q = Query([1, 2, 3])
        >>> q2 = Query(q)
        >>> q is q2
        True

        @param iterable: Iterable to wrap.
        @return: L{Query}-wrapped iterable.
        """
        if isinstance(iterable, cls):
            return iterable

        query = super(Query, cls).__new__(cls)
        query.iterable = iterable
        return query

    def __iter__(self):
        """
        Iterator wrapper.

        >>> for i in Query([1, 2, 3]):
        ...     print i
        1
        2
        3

        @return: Iterator for the iterable.
        """
        return iter(self.iterable)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
