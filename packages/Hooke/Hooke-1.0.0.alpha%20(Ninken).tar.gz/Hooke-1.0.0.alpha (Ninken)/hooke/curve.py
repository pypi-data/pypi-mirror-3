# Copyright (C) 2010-2012 W. Trevor King <wking@drexel.edu>
#
# This file is part of Hooke.
#
# Hooke is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Hooke is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hooke.  If not, see <http://www.gnu.org/licenses/>.

"""The `curve` module provides :class:`Curve` and :class:`Data` for
storing force curves.
"""

from copy_reg import dispatch_table
from copy import _reconstruct, _copy_dispatch
import logging
import os.path

import numpy

from .command_stack import CommandStack

#from guppy import hpy; hp = hpy()
guppy = None
import sys
last_heap = None

class NotRecognized (ValueError):
    def __init__(self, curve):
        self.__setstate__(curve)

    def __getstate__(self):
        return self.curve

    def __setstate__(self, data):
        if isinstance(data, Curve):
            msg = 'Not a recognizable curve format: %s' % data.path
            super(NotRecognized, self).__init__(msg)
            self.curve = data


class Data (numpy.ndarray):
    """Stores a single, continuous data set.

    Adds :attr:`info` :class:`dict` to the standard :class:`numpy.ndarray`.

    See :mod:`numpy.doc.subclassing` for the peculiarities of
    subclassing :class:`numpy.ndarray`.

    Examples
    --------

    >>> d = Data(shape=(3,2), info={'columns':['distance (m)', 'force (N)']})
    >>> type(d)
    <class 'hooke.curve.Data'>
    >>> for i in range(3): # initialize d
    ...    for j in range(2):
    ...        d[i,j] = i*10 + j
    >>> d
    Data([[  0.,   1.],
           [ 10.,  11.],
           [ 20.,  21.]])
    >>> d.info
    {'columns': ['distance (m)', 'force (N)']}

    The information gets passed on to slices.

    >>> row_a = d[:,0]
    >>> row_a
    Data([  0.,  10.,  20.])
    >>> row_a.info
    {'columns': ['distance (m)', 'force (N)']}

    The data-type is also pickleable, to ensure we can move it between
    processes with :class:`multiprocessing.Queue`\s.

    >>> import pickle
    >>> s = pickle.dumps(d)
    >>> z = pickle.loads(s)
    >>> z
    Data([[  0.,   1.],
           [ 10.,  11.],
           [ 20.,  21.]])
    >>> z.info
    {'columns': ['distance (m)', 'force (N)']}

    The data-type is also YAMLable (see :mod:`hooke.util.yaml`).

    >>> import yaml
    >>> s = yaml.dump(d)
    >>> print s
    !hooke.curve.DataInfo
    columns: [distance (m), force (N)]
    <BLANKLINE>
    >>> z = yaml.load(s)
    >>> z
    Data([], shape=(0, 0), dtype=float32)
    """
    def __new__(subtype, shape, dtype=numpy.float, buffer=None, offset=0,
                strides=None, order=None, info=None):
        """Create the ndarray instance of our type, given the usual
        input arguments.  This will call the standard ndarray
        constructor, but return an object of our type.
        """
        obj = numpy.ndarray.__new__(
            subtype, shape, dtype, buffer, offset, strides, order)
        # add the new attribute to the created instance
        if info == None:
            info = {}
        obj.info = info
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        """Set any extra attributes from the original object when
        creating a new view object."""
        # reset the attribute from passed original object
        self.info = getattr(obj, 'info', {})
        # We do not need to return anything

    def __reduce__(self):
        """Collapse an instance for pickling.

        Returns
        -------
        reconstruct : callable
            Called to create the initial version of the object.
        args : tuple
            A tuple of arguments for `reconstruct`
        state : (optional)
            The state to be passed to __setstate__, if present.
        iter : iterator (optional)
            Yielded items will be appended to the reconstructed
            object.
        dict : iterator (optional)
            Yielded (key,value) tuples pushed back onto the
            reconstructed object.
        """
        base_reduce = list(numpy.ndarray.__reduce__(self))
        # tack our stuff onto ndarray's setstate portion.
        base_reduce[2] = (base_reduce[2], (self.info,))
        return tuple(base_reduce)

    def __setstate__(self, state):
        base_class_state,own_state = state
        numpy.ndarray.__setstate__(self, base_class_state)
        self.info, = own_state


class Curve (object):
    """A grouped set of :class:`Data` runs from the same file with metadata.

    For an approach/retract force spectroscopy experiment, the group
    would consist of the approach data and the retract data.  Metadata
    would be the temperature, cantilever spring constant, etc.

    Each :class:`Data` block in :attr:`data` must contain an
    :attr:`info['name']` setting with a unique (for the parent
    curve) name identifying the data block.  This allows plugins 
    and commands to access individual blocks.

    Each curve maintiains a :class:`~hooke.command_stack.CommandStack`
    (:attr:`command_stack`) listing the commands that have been
    applied to the `Curve` since loading.

    The data-type is pickleable, to ensure we can move it between
    processes with :class:`multiprocessing.Queue`\s.

    >>> import pickle
    >>> import yaml
    >>> from .engine import CommandMessage
    >>> c = Curve(path='some/path')

    We add a recursive reference to `c` as you would get from
    :meth:`hooke.plugin.curve.CurveCommand._add_to_command_stack`.

    >>> c.command_stack.append(CommandMessage('curve info', {'curve':c}))

    >>> s = pickle.dumps(c)
    >>> z = pickle.loads(s)
    >>> z
    <Curve path>
    >>> z.command_stack
    [<CommandMessage curve info {curve: <Curve path>}>]
    >>> z.command_stack[-1].arguments['curve'] == z
    True
    >>> print yaml.dump(c)  # doctest: +REPORT_UDIFF
    &id001 !!python/object:hooke.curve.Curve
    command_stack: !!python/object/new:hooke.command_stack.CommandStack
      listitems:
      - !!python/object:hooke.engine.CommandMessage
        arguments:
          curve: *id001
        command: curve info
        explicit_user_call: true
    name: path
    path: some/path
    <BLANKLINE>

    However, if we try and serialize the command stack first, we run
    into `Python issue 1062277`_.

    .. _Python issue 1062277: http://bugs.python.org/issue1062277

    >>> pickle.dumps(c.command_stack)
    Traceback (most recent call last):
      ...
        assert id(obj) not in self.memo
    AssertionError

    YAML still works, though.

    >>> print yaml.dump(c.command_stack)  # doctest: +REPORT_UDIFF
    &id001 !!python/object/new:hooke.command_stack.CommandStack
    listitems:
    - !!python/object:hooke.engine.CommandMessage
      arguments:
        curve: !!python/object:hooke.curve.Curve
          command_stack: *id001
          name: path
          path: some/path
      command: curve info
      explicit_user_call: true
    <BLANKLINE>
    """
    def __init__(self, path, info=None):
        self.__setstate__({'path':path, 'info':info})

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return u'<%s %s>' % (self.__class__.__name__, self.name)

    def __repr__(self):
        return self.__str__()

    def set_path(self, path):
        if path != None:
            path = os.path.expanduser(path)
        self.path = path
        if self.name == None and path != None:
            self.name = os.path.basename(path)

    def _setup_default_attrs(self):
        # .data contains: {name of data: list of data sets [{[x], [y]}]
        # ._hooke contains a Hooke instance for Curve.load()
        self._default_attrs = {
            '_hooke': None,
            'command_stack': [],
            'data': None,
            'driver': None,
            'info': {},
            'name': None,
            'path': None,
            }

    def __getstate__(self):
        state = dict(self.__dict__)  # make a copy of the attribute dict.
        del(state['_hooke'])
        return state

    def __setstate__(self, state):
        self._setup_default_attrs()
        self.__dict__.update(self._default_attrs)
        if state == True:
            return
        self.__dict__.update(state)
        self.set_path(getattr(self, 'path', None))
        if self.info in [None, {}]:
            self.info = {}
        if type(self.command_stack) == list:
            self.command_stack = CommandStack()

    def __copy__(self):
        """Set copy to preserve :attr:`_hooke`.

        :meth:`getstate` drops :attr:`_hooke` for :mod:`pickle` and
        :mod:`yaml` output, but it should be preserved (but not
        duplicated) during copies.

        >>> import copy
        >>> class Hooke (object):
        ...     pass
        >>> h = Hooke()
        >>> d = Data(shape=(3,2), info={'columns':['distance (m)', 'force (N)']})
        >>> for i in range(3): # initialize d
        ...    for j in range(2):
        ...        d[i,j] = i*10 + j
        >>> c = Curve(None)
        >>> c.data = [d]
        >>> c.set_hooke(h)
        >>> c._hooke  # doctest: +ELLIPSIS
        <hooke.curve.Hooke object at 0x...>
        >>> c._hooke == h
        True
        >>> c2 = copy.copy(c)
        >>> c2._hooke  # doctest: +ELLIPSIS
        <hooke.curve.Hooke object at 0x...>
        >>> c2._hooke == h
        True
        >>> c2.data
        [Data([[  0.,   1.],
               [ 10.,  11.],
               [ 20.,  21.]])]
        >>> d.info
        {'columns': ['distance (m)', 'force (N)']}
        >>> id(c2.data[0]) == id(d)
        True
        """
        copier = _copy_dispatch.get(type(self))
        if copier:
            return copier(self)
        reductor = dispatch_table.get(type(self))
        if reductor:
            rv = reductor(self)
        else:
            # :class:`object` implements __reduce_ex__, see :pep:`307`.
            rv = self.__reduce_ex__(2)
        y = _reconstruct(self, rv, 0)
        y.set_hooke(self._hooke)
        return y

    def __deepcopy__(self, memo):
        """Set deepcopy to preserve :attr:`_hooke`.

        :meth:`getstate` drops :attr:`_hooke` for :mod:`pickle` and
        :mod:`yaml` output, but it should be preserved (but not
        duplicated) during copies.

        >>> import copy
        >>> class Hooke (object):
        ...     pass
        >>> h = Hooke()
        >>> d = Data(shape=(3,2), info={'columns':['distance (m)', 'force (N)']})
        >>> for i in range(3): # initialize d
        ...    for j in range(2):
        ...        d[i,j] = i*10 + j
        >>> c = Curve(None)
        >>> c.data = [d]
        >>> c.set_hooke(h)
        >>> c._hooke  # doctest: +ELLIPSIS
        <hooke.curve.Hooke object at 0x...>
        >>> c._hooke == h
        True
        >>> c2 = copy.deepcopy(c)
        >>> c2._hooke  # doctest: +ELLIPSIS
        <hooke.curve.Hooke object at 0x...>
        >>> c2._hooke == h
        True
        >>> c2.data
        [Data([[  0.,   1.],
               [ 10.,  11.],
               [ 20.,  21.]])]
        >>> d.info
        {'columns': ['distance (m)', 'force (N)']}
        >>> id(c2.data[0]) == id(d)
        False
        """
        reductor = dispatch_table.get(type(self))
        if reductor:
            rv = reductor(self)
        else:
            # :class:`object` implements __reduce_ex__, see :pep:`307`.
            rv = self.__reduce_ex__(2)
        y = _reconstruct(self, rv, 1, memo)
        y.set_hooke(self._hooke)
        return y

    def set_hooke(self, hooke=None):
        if hooke != None:
            self._hooke = hooke

    def identify(self, drivers):
        """Identify the appropriate :class:`hooke.driver.Driver` for
        the curve file (`.path`).
        """
        if 'filetype' in self.info:
            driver = [d for d in drivers if d.name == self.info['filetype']]
            if len(driver) == 1:
                driver = driver[0]
                if driver.is_me(self.path):
                    self.driver = driver
                    return
        for driver in drivers:
            if driver.is_me(self.path):
                self.driver = driver # remember the working driver
                return
        raise NotRecognized(self)

    def load(self, hooke=None):
        """Use the driver to read the curve into memory.

        Also runs any commands in :attr:`command_stack`.  All
        arguments are passed through to
        :meth:`hooke.command_stack.CommandStack.execute`.
        """
        global last_heap
        self.set_hooke(hooke)
        log = logging.getLogger('hooke')
        log.debug('loading curve %s with driver %s' % (self.name, self.driver))
        print('loading curve %s with driver %s' % (self.name, self.driver))
        if guppy is not None:
            h = hp.heap()
            if last_heap is None:
                print(h)
            else:
                print last_heap.diff(h)
                last_heap = h
        sys.stdout.flush()
        data,info = self.driver.read(self.path, self.info)
        self.data = data
        for key,value in info.items():
            self.info[key] = value
        if self._hooke != None:
            log.debug('execute command stack for {}'.format(self))
            self.command_stack.execute(self._hooke)
        elif len(self.command_stack) > 0:
            log.warn(
                'could not execute command stack for %s without Hooke instance'
                % self.name)

    def unload(self):
        """Release memory intensive :attr:`.data`.
        """
        log = logging.getLogger('hooke')
        log.debug('unloading curve %s' % self.name)
        print('unloading curve %s' % self.name)
        self.data = None
