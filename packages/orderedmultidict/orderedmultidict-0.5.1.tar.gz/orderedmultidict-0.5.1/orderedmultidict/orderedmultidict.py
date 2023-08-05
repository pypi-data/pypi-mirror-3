#
# omdict: Ordered Multivalue Dictionary.
#
# Arthur Grunseid
# grunseid.com
# grunseid@gmail.com
#
# License: Build Amazing Things (Unlicense)

try:
  from collections import OrderedDict as odict
except ImportError:
  from ordereddict import OrderedDict as odict
from itertools import imap, izip, izip_longest, repeat

_absent = object() # Marker that means no parameter was provided.

class omdict():
  """
  omdict: Ordered Multivalue Dictionary that retains method parity with dict().

  A multivalue dictionary is a dictionary that can store multiple values for the
  same key. An ordered multivalue dictionary is a multivalue dictionary that
  retains the order of insertions and deletions into and from a multivalue
  dictionary.

  Internally, keys and their values are stored in an ordered dictionary,
  self._map. Order for all key:value items is maintained in a list, self._items.

  Standard dict() methods interact with the first value associated with a given
  key. This means that omdict() retains method parity with dict(), and a dict()
  object can be replaced with an omdict() object and all interaction will behave
  identically. Every dict() method retains parity:
  
    get(), setdefault(), pop(), popitem(),
    clear(), copy(), update(), fromkeys(), len()
    __getitem__(), __setitem__(), __delitem__(), __contains__(),
    items(), keys(), values(), iteritems(), iterkeys(), itervalues(),

  Optional parameters have been added to some dict() methods, but because the
  parameters are optional, standard dict() use remains unaffected. An optional
  <key> parameter has been added to these methods:

    items(), values(), iteritems(), itervalues()

  New methods have also been added to omdict(). Methods with 'list' in their
  name interact with lists of values, and methods with 'all' in their name
  interact with all items in the dictionary, including multiple items with the
  same key.
 
  The new methods of omdict() are:

    load(), size(), reverse(),
    getlist(), add(), addlist(), set(), setlist(), setlistdefault(),
    poplist(), popvalue(), popitem(), popitemlist(),
    lists(),  allitems(), allkeys(), allvalues(),
    iterlists(), iterallitems(), iterallkeys(), iterallvalues()

  Explanations and examples of the new methods above can be found in the
  function comments below and online at

    https://github.com/gruns/orderedmultidict

  Additional information and documentation can also be found at the above url.
  """
  def __init__(self, mapping=None):
    # Ordered list of items in (key, value) fashion.
    self._items = []

    # Ordered dictionary of keys and values. Each key's value is an ordered list
    # of its assocaited values, [v1, v2, v3, v4, ...].
    self._map = odict()

    if mapping:
      self.load(mapping)

  def load(self, mapping):
    """
    Clear all existing key:value items and import all key:value items from
    <mapping>. If multiple values exist for the same key in <mapping>, they will
    all be imported.

    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.load([(4,4),(4,44),(5,5)])
      omd.allitems() == [(4,4),(4,44),(5,5)]

    Returns: self.
    """
    self.clear()
    self.updateall(mapping)
    return self
    
  def copy(self):
    return self.__class__(self._items)

  def clear(self):
    self._map.clear()
    del self._items[:]

  def size(self):
    """
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.size() == 5

    Returns: Total number of items, including multiple items with the same key.
    """
    return len(self._items)

  @classmethod
  def fromkeys(cls, iterable, value=None):
    return cls([(key, value) for key in iterable])

  def has_key(self, key):
    return key in self

  def update(self, mapping):
    self._update_updateall(mapping, lambda key, value: self.__setitem__(key, value))

  def updateall(self, mapping):
    """
    Update this dictionary with the items from <mapping>, overwriting existing
    keys.

    Returns: self.
    """
    self._update_updateall(mapping, lambda key, value: self.add(key, value))
    return self

  def _update_updateall(self, mapping, update_lambda):
    iterator = mapping
    if hasattr(mapping, 'iterallitems') and callable(mapping.iterallitems):
      iterator = mapping.iterallitems()
    elif hasattr(mapping, 'iteritems') and callable(mapping.iteritems):
      iterator = mapping.iteritems()
    for key, value in iterator:
      update_lambda(key, value)

  def get(self, key, default=None):
    if key in self:
      return self._map[key][0]
    return default

  def getlist(self, key, default=[]):
    """
    Returns: The list of values for <key> if <key> is in the dictionary, else
    <default>. If <default> is not provided, an empty list is returned.
    """
    if key in self:
      return self._map[key]
    return default

  def setdefault(self, key, default=None):
    if key in self:
      return self[key]
    self.add(key, default)
    return default

  def setlistdefault(self, key, default=[]):
    """
    Similar to setdefault() except <default> is a list of values to set for
    <key>. If <key> already exists, its existing list of values is returned.

    Returns: List of <key>'s values if <key> exists in the dictionary, otherwise
    <default>.
    """
    if key in self._map:
      return self.getlist(key)
    self.addlist(key, default)
    return default

  def add(self, key, value=None):
    """
    Add <value> to the list of values for key <key>. If <key> is not in the
    dictionary, then <value> is added as the sole value for <key>. If <key> is
    already in the dictionary, <value> is added to the existing list of values
    for <key.
    
    Example:
      omd = omdict()
      omd.add(1,1)  # omd.allitems() == [(1,1)]
      omd.add(1,11) # omd.allitems() == [(1,1),(1,11)]
      omd.add(2,2)  # omd.allitems() == [(1,1),(1,11),(2,2)]

    Returns: self.
    """    
    self._map.setdefault(key, [])
    self._map[key].append(value)
    self._items.append((key, value))
    return self

  def addlist(self, key, valuelist=[]):
    """
    Add the values in <valuelist> to the list of values for key <key>. If <key>
    is not in the dictionary, then the values in <valuelist> are added as the
    only values for <key>. If <key> is already in the dictionary, the values in
    <valuelist> are added to <keys>'s existing list of values.

    Example:
      omd = omdict()
      omd.addlist(1,[1,11,111]) # omd.allitems() == [(1,1),(1,11),(1,111)]
      omd.addlist(2,[2) # omd.allitems() == [(1,1),(1,11),(1,111),(2,2)]

    Returns: self.
    """    
    for value in valuelist:
      self.add(key, value)
    return self

  def set(self, key, value=None):
    """
    Sets <key>'s value to <value>. Identical in function to __setitem__().

    Returns: self.
    """
    self[key] = value
    return self

  def setlist(self, key, valuelist=[]):
    """
    Sets <key>'s list of values to <valuelist>.

    Returns: self.
    """
    self.pop(key, None)
    self.addlist(key, valuelist)
    return self

  def pop(self, key, default=_absent):
    if key in self._map:
      return self.poplist(key)[0]
    elif key not in self._map and default is not _absent:
      return default
    raise KeyError(key)

  def poplist(self, key, default=_absent):
    """
    If <key> is in the dictionary, pop it and return its list of values. If
    <key> is not in the dictionary, return <default>. If <default> is not
    provided and <key> is not in the dictionary, a KeyError is raised.

    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.poplist(1) == [1, 11, 111] # omd.allitems() == [(2,2),(3,3)]
      omd.poplist(2) == [2] # omd.allitems() == [(3,3)]

    Raises: KeyError if <key> isn't in the dictionary and <default> isn't
      provided.
    Returns: List of <key>'s values.
    """
    if key in self._map:
      values = self.getlist(key)
      del self._map[key]
      self._items = [item for item in self._items if item[0] != key]
      return values
    elif key not in self._map and default is not _absent:
      return default
    raise KeyError(key)

  def popvalue(self, key, default=_absent, last=True):
    """
    If <key> is in the dictionary, pop its first or last value and return it,
    otherwise return <default>. After a value is popped, if <key> no longer has
    any values it is removed from the dictionary. If <default> is not provided
    and <key> is not in the dictionary, a KeyError is raised.

    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.popvalue(1, last=True) == 111 # omdict([(1,1),(1,11),(2,2),(3,3)])
      omd.popvalue(1) == 1 # omdict([(1,11),(2,2),(3,3)])

    Params:
      last: Boolean whether to return <key>'s first value (<last> is False) or
        last value (<last> is True).
    Raises: KeyError if <key> isn't in the dictionary and <default> isn't
      provided.
    Returns: The first or last of <key>'s values.
    """
    if key in self._map:
      value = self._map[key].pop(-1 if last else 0)
      if not self._map[key]:
        del self._map[key]
      if last:
        _rremove(self._items, (key, value))
      else:
        self._items.remove((key, value))
      return value
    elif key not in self._map and default is not _absent:
      return default
    raise KeyError(key)

  def popitem(self, fromall=False, last=True):
    """
    Pop and return a key:value item. If <fromall> is False, items()[0] will be
    popped if <last> is False or items()[-1] will be popped if <last> is
    True. If <fromall> is True, allitems()[0] will be popped if <last> is False
    or allitems()[-1] will be popped if <last> is True.

    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.popitem() == (3,3)
      omd.popitem(fromall=False, last=False) == (1,1)
      omd.popitem(fromall=False, last=False) == (2,2)

      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.popitem(fromall=True, last=False) == (1,1)
      omd.popitem(fromall=True, last=False) == (1,11)
      omd.popitem(fromall=True, last=True) == (3,3)
      omd.popitem(fromall=True, last=False) == (1,111)

    Params:
      fromall: Whether to pop an item from items() (<fromall> is True) or
        allitems() (<fromall> is False).
      last: Boolean whether to pop the first item or last item of items() or
        allitems().
    Returns: The first or last item from item() or allitem().
    """
    if not self._items:
      raise KeyError('popitem(): %s is empty' % self.__class__.__name__)

    if fromall:
      key, value = self._items[-1 if last else 0]
      return key, self.popvalue(key, last=last)
    else:
      key = self._map.keys()[-1 if last else 0]
      return key, self.pop(key)

  def popitemlist(self, last=True):
    """
    Pop and return a key:valuelist item comprised of a key and that key's list
    of values. If <last> is False, a two-tuple comprised of keys()[0] and its
    associated list of values will be popped and returned. If <last> is True, a
    two-tuple comprised of keys()[-1] and its associated list of values will be
    popped and returned.

    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.popitemlist(last=True) == (3,[3])
      omd.popitemlist(last=False) == (1,[1,11,111])

    Params:
      last: Boolean whether to pop the first or last key and its associated list
        of values.
    Returns: A two-tuple comprised of the first or last key and its associated
      list of values.
    """
    if not self._items:
      raise KeyError('popitemlist(): %s is empty' % self.__class__.__name__)

    key = self.keys()[-1 if last else 0]
    return key, self.poplist(key)

  def items(self, key=_absent):
    """
    Raises: KeyError if <key> is provided and not in the dictionary.
    Returns: List composed from iteritems(<key>). If <key> is provided and is a
      dictionary key, only items with key <key> will be returned.
    """
    return list(self.iteritems(key))

  def keys(self):
    return list(self.iterkeys())

  def values(self, key=_absent):
    """
    Raises: KeyError if <key> is provided and not in the dictionary.
    Returns: List composed from itervalues(<key>).If <key> is provided and is a
      dictionary key, only values of items with key <key> will be returned.
    """
    if key is not _absent and key in self._map:
      return list(self.getlist(key))
    return list(self.itervalues())

  def lists(self):
    """
    Returns: List composed from iterlists().
    """
    return list(self.iterlists())

  def iteritems(self, key=_absent):
    """
    Parity with dict.iteritems() except the optional <key> parameter has been
    added. If <key> is provided, only items with the provided key will be
    iterated over. If <key> is provided and not in the dictionary, a KeyError is
    raised.
    
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.iteritems(1) -> (1,1) -> (1,11) -> (1,111)
      omd.iteritems() -> (1,1) -> (1,11) -> (1,111) -> (2,2) -> (3,3)

    Raises: KeyError if <key> is provided and not in the dictionary.
    Returns: An iterator over the items() of the dictionary, or only items with
      the key <key> if <key> is provided.
    """
    if key is not _absent:
      if key in self._map:
        return izip(repeat(key), self._map[key])
      raise KeyError(key)
    return imap(lambda (k,v): (k, v[0]), self._map.iteritems())

  def iterkeys(self):
    return self._map.iterkeys()

  def itervalues(self, key=_absent):
    """
    Parity with dict.itervalues() except the optional <key> parameter has been
    added. If <key> is provided, only values from items with the provided key
    will be iterated over. If <key> is provided and not in the dictionary, a
    KeyError is raised.
    
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.itervalues(1) -> 1 -> 11 -> 111
      omd.itervalues() -> 1 -> 11 -> 111 -> 2 -> 3

    Raises: KeyError if <key> is provided and isn't in the dictionary.
    Returns: An iterator over the values() of the dictionary, or only the values
      of key <key> if <key> is provided.
    """
    if key is not _absent:
      if key in self._map:
        return iter(self._map[key])
      raise KeyError(key)
    return imap(lambda v: v[0], self._map.itervalues())

  def iterlists(self):
    '''
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.iterlists() -> [1,11,111] -> [2] -> [3]
    
    Returns: An iterator over the list of values for each key in the
    dictionary.
    '''
    return self._map.itervalues()

  def allitems(self, key=_absent):
    '''
    Raises: KeyError if <key> is provided and not in the dictionary.
    Returns: List composed from iterallitems(<key>).
    '''    
    return list(self.iterallitems(key))

  def allkeys(self):
    '''
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.allkeys() == [1,1,1,2,3]

    Returns: List composed from iterallkeys().
    '''    
    return list(self.iterallkeys())

  def allvalues(self, key=_absent):
    '''
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.allvalues() == [1,11,111,2,3]
      omd.allvalues(1) == [1,11,111]

    Raises: KeyError if <key> is provided and not in the dictionary.
    Returns: List composed from iterallvalues(<key>).
    '''    
    return list(self.iterallvalues(key))

  def iterallitems(self, key=_absent):
    '''
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.iterallitems() == (1,1) -> (1,11) -> (1,111) -> (2,2) -> (3,3)
      omd.iterallitems(1) == (1,1) -> (1,11) -> (1,111)

    Raises: KeyError if <key> is provided and not in the dictionary.
    Returns: An iterator over every item in the diciontary. If <key> is
      provided, only items with the key <key> are iterated over.
    '''
    if key is not _absent:
      return self.iteritems(key) # Raises KeyError if <key> is not in self._map.
    return iter(self._items)

  def iterallkeys(self):
    '''
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.iterallkeys() == 1 -> 1 -> 1 -> 2 -> 3
        
    Returns: An iterator over the keys of every item in the dictionary.
    '''
    for item in iter(self._items):
      yield item[0]

  def iterallvalues(self, key=_absent):
    '''
    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.iterallvalues() == 1 -> 11 -> 111 -> 2 -> 3
        
    Returns: An iterator over the values of every item in the dictionary.
    '''
    if key is not _absent:
      if key in self._map:
        return iter(self._map[key])
      raise KeyError(key)
    return iter(map(lambda p: p[1], self._items))

  def reverse(self):
    """
    Reverse the order of all items in the dictionary.

    Example:
      omd = omdict([(1,1),(1,11),(1,111),(2,2),(3,3)])
      omd.reverse()
      omd.allitems() == [(3,3),(2,2),(1,111),(1,11),(1,1)]

    Returns: self.
    """
    for key in self._map.iterkeys():
      self._map[key].reverse()
    self._items.reverse()
    return self

  def __eq__(self, other):
    others = other.iterallitems()
    for item1, item2 in izip_longest(self._items, others, fillvalue=_absent):
      if item1 != item2 or item1 is _absent or item2 is _absent:
        return False
    return True

  def __ne__(self, other):
    return not self.__eq__(other)

  def __len__(self):
    return len(self._map)

  def __iter__(self):
    for key in self.iterkeys():
      yield key

  def __contains__(self, item):
    if hasattr(item, '__len__') and callable(item.__len__) and len(item) == 2:
      return item in self._items
    return item in self._map

  def __getitem__(self, key):
    if key in self._map:
      return self.get(key)
    raise KeyError(key)

  def __setitem__(self, key, value):
    if key in self._map:
      self.poplist(key)
    self.add(key, value)

  def __delitem__(self, key):
    return self.pop(key)

  def __nonzero__(self):
    return bool(self._map)

  def __str__(self):
    return '{%s}' % ', '.join(map(lambda p: '%s: %s'%(p[0], p[1]), self._items))


def _rfind(lst, item):
  """
  Returns the index of the last occurance of <item> in <lst>. Returns -1 if
  <item> is not in <l>.
    ex: _rfind([1,2,1,2], 1) == 2
  """
  try:
    return (len(lst) - 1) - lst[::-1].index(item)
  except ValueError:
    return -1

def _rremove(lst, item):
  """
  Removes the last occurance of <item> in <lst>, or raises a ValueError if
  <item> is not in <list>.
    ex: _rremove([1,2,1,2], 1) == [1,2,2]
  """
  pos = _rfind(lst, item)
  if pos >= 0:
    lst.pop(pos)
    return lst
  else:
    raise ValueError('_rremove(list, x): x not in list')
