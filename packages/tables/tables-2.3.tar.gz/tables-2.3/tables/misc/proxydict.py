"""
Proxy dictionary for objects stored in a container
==================================================

:Author:   Ivan Vilata i Balaguer
:Contact:  ivan@selidor.net
:Created:  2005-07-07
:License:  BSD
:Revision: $Id$
"""

import weakref



class ProxyDict(dict):

    """A dictionary which uses a container object to store its values."""

    def __init__(self, container):
        self.containerRef = weakref.ref(container)
        """A weak reference to the container object."""


    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)

        # Values are not actually stored to avoid extra references.
        return self._getValueFromContainer(self._getContainer(), key)


    def __setitem__(self, key, value):
        # Values are not actually stored to avoid extra references.
        super(ProxyDict, self).__setitem__(key, None)


    def __repr__(self):
        return object.__repr__(self)


    def __str__(self):
        # C implementation does not use `self.__getitem__()`. :(
        itemFormat = '%r: %r'
        itemReprs = [itemFormat % item for item in self.iteritems()]
        return '{%s}' % ', '.join(itemReprs)


    def values(self):
        # C implementation does not use `self.__getitem__()`. :(
        valueList = []
        for key in self.iterkeys():
            valueList.append(self[key])
        return valueList


    def itervalues(self):
        # C implementation does not use `self.__getitem__()`. :(
        for key in self.iterkeys():
            yield self[key]
        raise StopIteration


    def items(self):
        # C implementation does not use `self.__getitem__()`. :(
        itemList = []
        for key in self.iterkeys():
            itemList.append((key, self[key]))
        return itemList


    def iteritems(self):
        # C implementation does not use `self.__getitem__()`. :(
        for key in self.iterkeys():
            yield (key, self[key])
        raise StopIteration


    def _getContainer(self):
        container = self.containerRef()
        if container is None:
            raise ValueError("the container object does no longer exist")
        return container
