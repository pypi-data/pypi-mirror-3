"""
.. module:: wr
   :platform: Any
   :synopsis: A Python module for working with weighted randomness.

.. moduleauthor:: Waawal <waawal@boom.ws>


"""
import random
try:
    from collections import Mapping
except ImportError:
    Mapping = dict

def choice(data):
    """The main implementation of weighted random choice.
       (based on inplace algorithm)

    Args:
       data (Mapping or sequence of pairs):  (returnable, weight)

    Returns:
       For Mappings: A key
       For sequences of pairs: [0] of a pair.

    Usecase:

    >>> print wr.choice({"hello": 80, "world": 20})
    hello

    """
    if isinstance(data, Mapping):
        dataitems = data.items()
        totalweights = sum(data.values()) - 1
    else:
        dataitems = data
        totalweights = sum([i[1] for i in data]) - 1
    
    randomindex = random.randint(0, totalweights)
    count = 0
    for returnable, weight in dataitems:
            count += weight
            if count > randomindex:
                    return returnable

