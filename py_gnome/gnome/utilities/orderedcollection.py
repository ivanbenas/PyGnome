#!/usr/bin/env python


class OrderedCollection(object):
    '''
    Generalized Container for a set of objects of a particular type which
    preserves the order of insertion and supports replacement of not only
    an object in the list, but the key/id that references it. (a normal
    OrderedDict can't do this)
    - The order of insertion is preserved.
    - Objects are accessed by id, as if in a dictionary.
    - Objects can be replaced in order.  The objects will be referenced
    by a new id, and still be in the correct order.
    '''

    def __init__(self, elems=None, dtype=None):
        if elems and not isinstance(elems, list):
            raise TypeError('%s: needs a list of objects'
                            % self.__class__.__name__)
        if not elems:
            elems = []

        if not dtype and len(elems) == 0:
            raise TypeError('%s: specify a data type if list is empty'
                            % self.__class__.__name__)
        elif not dtype:
            self.dtype = type(elems[0])
        else:
            self.dtype = dtype

        if not all([isinstance(e, self.dtype) for e in elems]):
            raise TypeError('%s: needs a list of %s'
                            % (self.__class__.__name__, self.dtype))

        # a bunch of Gnome classes have an id property defined, which we will
        # prefer
        # otherwise, we just take the id(e) value
        # NOTE: we stringify the e.id value since it could be of a type that
        # is hard to reference as a key

        self._elems = elems[:]
        self._d_index = \
            {self._s_id(elem): idx for idx, elem in enumerate(self._elems)}

        self.callbacks = {}

    def _s_id(self, elem):
        'return the id of the object as a string'
        if hasattr(elem, 'id'):
            return str(elem.id)
        else:
            return str(id(elem))

    def remake(self):
        '''
        remove None elements from self._elems and renumber the indices in
        self._d_index
        '''
        if None in self._elems:
            self._elems = [elem for elem in self._elems if elem is not None]
            for ix, elem in enumerate(self._elems):
                self._d_index[self._s_id(elem)] = ix

    def get(self, ident):
        '''
        can get the object either by 'id' or by index in the order in which
        it was added
        '''
        try:
            # ident is an index into list
            idx = sorted(self._d_index.values())[ident]
            return self._elems[idx]
        except TypeError:
            # ident is the 'id' string
            return self._elems[self._d_index[ident]]

    def add(self, elem):
        'Add an object to the collection '
        if isinstance(elem, self.dtype):
            l__id = self._s_id(elem)

            if l__id not in list(self._d_index.keys()):
                self._d_index[l__id] = len(self._elems)
                self._elems.append(elem)

                # fire add event only if elem is not already in the list
                self.fire_event('add', elem)
        else:
            # assume its an iterable list/tuple of items to be added
            try:
                for e in elem:
                    if not isinstance(e, self.dtype):
                        raise
                    self.add(e)
            except:
                raise TypeError('{0}: expected {1!r}, '
                                'got {2!r}'.format(self.__class__.__name__,
                                                   self.dtype,
                                                   elem))

    def append(self, elem):
        self.add(elem)

    def remove(self, ident):
        '''
        Remove an object from the collection:
        1) can remove by index (similar to a list)
        2) can remove by id of object (similar to a dict)
        '''
        if ident in self._d_index:
            # ident is object id
            obj_id = ident
        else:
            # ident is index into _elems list
            obj_id = self._s_id(self[ident])

        item = self[obj_id]
        self._elems[self._d_index[obj_id]] = None
        del self._d_index[obj_id]

        # fire remove event before removing from collection
        # let gc delete item if it is no longer referenced
        self.fire_event('remove', item)

    def replace(self, ident, new_elem):
        '''
        replace an object in the collection:
        1) replace by index (similar to a list)
        2) replace by id of object (similar to a dict)

        raise exception if 'id' is not found.
        '''
        if not isinstance(new_elem, self.dtype):
            raise TypeError('{0}: expected {1}, '
                            'got {2}'.format(self.__class__.__name__,
                                             self.dtype,
                                             type(new_elem)))

        if isinstance(ident, int):
            l__key = self._s_id(self._elems[ident])
            idx = ident
        else:
            if ident in self._d_index:
                l__key = ident
            else:
                raise KeyError('Cannot find object by this "id" in '
                               'OrderedCollection')

            idx = self._d_index[l__key]

        # found existing object
        del self._d_index[l__key]
        self._elems[idx] = new_elem
        self._d_index[self._s_id(new_elem)] = idx
        self.fire_event('replace', new_elem)  # returns the newly added object

    def index(self, elem):
        '''
        acts like index method in a list.
        It returns the index associated with self._elems[index] = elem
        It can also take the 'id' as input and returns the index of the object
        in the list
        '''
        try:
            # first check if elem is the 'id'
            idx = self._d_index[elem]
        except KeyError:
            # if its not a valid ID, then check if its the object
            ident = self._s_id(elem)
            try:
                idx = self._d_index[ident]
            except KeyError:
                raise ValueError('{0} is not in OrderedCollection'
                                 .format(elem))

        return sorted(self._d_index.values()).index(idx)

    def __len__(self):
        return len(list(self._d_index.keys()))

    def __iter__(self):
        for i in sorted(self._d_index.values()):
            yield self._elems[i]

    def __contains__(self, elem):
        id_ = self._s_id(elem)
        # NOTE: following is not a good test:
        #    return elem in self._elems
        # since it just checks to see if
        # there is some element in the list self._elems == elem.
        # We want to know if there is some index for which
        # self._elems[ix] is elem
        # Check to see if there is an 'id' for this object
        # in self._d_index dict
        return id_ in self._d_index

    def _slice_attr(self, ident):
        'support for slice operations like a list'
        start = (ident.start, 0)[ident.start is None]
        stop = (ident.stop, len(self))[ident.stop is None]
        step = (ident.step, 1)[ident.step is None]
        return (start, stop, step)

    def __getitem__(self, ident):
        'slicing works just like it does for lists'
        if isinstance(ident, slice):
            (start, stop, step) = self._slice_attr(ident)
            return [self.get(ix) for ix in range(start, stop, step)]
        else:
            return self.get(ident)

    def __setitem__(self, ident, new_elem):
        '''
        does not yet support slice assignment.
        There is no need but is easy to add if required
        '''
        self.replace(ident, new_elem)

    def __delitem__(self, ident):
        '''
        does not yet support slice assignment.
        There is no need but is easy to add if required
        '''
        self.remove(ident)

    def __iadd__(self, rop):
        self.add(rop)
        return self

    def __str__(self):
        # order by position in list
        itemlist = sorted(list(self._d_index.items()), key=lambda x: x[1])

        # reference the value in list
        itemlist = [(k, self._elems[v]) for (k, v) in itemlist]

        if len(itemlist) > 6:  # should we abbreviate the list?
            strlist = ['\t%s: %s,' % i for i in itemlist[:2]]
            strlist += ('\t...', '\t...')
            strlist += ['\t%s: %s,' % i for i in itemlist[-2:]]
        else:
            strlist = ['\t%s: %s,' % i for i in itemlist]

        return ('{0}({{\n'
                '{1}\n'
                '}})'.format(self.__class__.__name__, '\n'.join(strlist)))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """ Equality of two ordered collections """

        if not isinstance(other, OrderedCollection):
            return False

        if len(self) != len(other):
            return False

        for oc in zip(self, other):
            if oc[0] != oc[1]:
                return False

        return True

    def __ne__(self, other):
        return not self == other

    def to_dict(self):
        '''
        Method takes the instance of ordered collection and outputs a list of
        dicts, each with two fields::

            {obj_type: object type <module.class>,
            id: IDs of each object}
        '''
        items = []

        for obj in self:
            try:
                obj_type = '{0.__module__}.{0.__class__.__name__}'.format(obj)
            except AttributeError:
                obj_type = '{0.__class__.__name__}'.format(obj)
            item = {'obj_type': obj_type, 'id': self._s_id(obj)}
            items.append(item)

        return items

    def register_callback(self, callback,
                          events=('add', 'replace', 'remove')):
        '''
        callbacks registered for following events:
        - add: item is added
        - replace:
        - remove: callback invoked after removing the item
        '''
        if not isinstance(events, (list, tuple)):
            events = (events, )

        for event in events:
            if event not in ('add', 'remove', 'replace'):
                raise ValueError("Events must be either "
                                 "('add', 'remove', 'replace'). "
                                 "{0} is not supported".format(event))

        self.callbacks[callback] = events

    def fire_event(self, event, obj_):
        for (callback, reg_event) in list(self.callbacks.items()):
            if event in reg_event:
                callback(obj_)  # this should be all that is required

    def clear(self):
        '''
        clear all elements from collection
        '''
        del self._elems[:]
        self._d_index.clear()

    def values(self):
        'return list of items contained in collection'
        return [item for item in self._elems if item is not None]
