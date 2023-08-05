Developer documentation
=======================

This documentation is intended for other developers that would like to contribute with the development of Pydap, or extend it in new ways. It assumes that you have a basic knowledge of Python and HTTP, and understands how data is stored in different formats. It also assumes some familiarity with the `Data Access Protocol <http://opendap.org/>`_, though a lot of its inner workings will be explained in detail here.

The DAP data model
------------------

The DAP is a protocol designed for the efficient transmission of scientific data over the internet. In order to transmit data from the server to a client, both must agree on a way to represent data: *is it an array of integers?*, *a multi-dimensional grid?* In order to do this, the specification defines a *data model* that, in theory, should be able to represent any existing dataset.

Metadata
~~~~~~~~

Pydap has a series of classes in the ``pydap.model`` module, representing the DAP data model. The most fundamental data type is called ``BaseType``, and it represents a value or an array of values. Here an example of creating one of these objects:

.. doctest::

    >>> from pydap.model import *
    >>> a = BaseType(
    ...         name='a',
    ...         data=1,
    ...         shape=(),
    ...         dimensions=(),
    ...         type=Int32,
    ...         attributes={'long_name': 'variable a'})

All Pydap types have five attributes in common. The first one is the ``name`` of the variable; in this case, our variable is called "a":

.. doctest::

    >>> print a.name
    a

Note that there's a difference between the variable name (the local name ``a``) and its attribute ``name``; in this example they are equal, but we could reference our object using any other name:

.. doctest::

    >>> b = a  # b now points to a
    >>> print b.name
    a

We can use special characters for the variable names; they will be quoted accordingly:

.. doctest::

    >>> c = BaseType(name='long & complicated')
    >>> print c.name
    long%20%26%20complicated

The second attribute is called ``id``. In the examples we've seen so far, ``id`` and ``name`` are equal:

.. doctest::

    >>> print a.name, a.id
    a a
    >>> print c.name, c.id
    long%20%26%20complicated long%20%26%20complicated

This is because the id is used to show the position of the variable in a given dataset, and in these examples the variables do not belong to any datasets. First let's store our variables in a container object called ``StructureType``. A ``StructureType`` is a special type of ordered dictionary that holds other Pydap types:

.. doctest::

    >>> s = StructureType(name='s')
    >>> s['a'] = a
    >>> s['c'] = c
    Traceback (most recent call last):
        ...
    KeyError: 'Key "c" is different from variable name "long%20%26%20complicated"!'

Note that the variable name has to be used as its key on the ``StructureType``. This can be easily remedied:

.. doctest::

    >>> s[c.name] = c

There is a special derivative of the ``StructureType`` called ``DatasetType``, which represent the dataset. The difference between the two is that there should be only one ``DatasetType``, but it may contain any number of ``StructureType`` objects, which can be deeply nested. Let's create our dataset object:

.. doctest::

    >>> dataset = DatasetType(name='example')
    >>> dataset['s'] = s
    >>> print dataset.id
    example
    >>> print dataset['s'].id
    s
    >>> print dataset['s']['a'].id
    s.a

Note that for objects on the first level of the dataset, like ``s``, the id is identical to the name. Deeper objects, like ``a`` which is stored in ``s``, have their id calculated by joining the names of the variables with a period. One detail is that we can access variables stored in a structure using a "lazy" syntax like this:

.. doctest::

    >>> print dataset.s.a.id
    s.a

The third common attribute that variables share is called ``attributes``, which hold most of its metadata. This attribute is a dictionary of keys and values, and the values themselves can also be dictionaries. For our variable ``a`` we have:

.. doctest::

    >>> print a.attributes
    {'long_name': 'variable a'}

These attributes can be accessed lazily directly from the variable:

.. doctest::

    >>> print a.long_name
    variable a

But if you want to create a new attribute you'll have to insert it directly into ``attributes``:

.. doctest::

    >>> a.history = 'Created by me'
    >>> print a.attributes
    {'long_name': 'variable a'}
    >>> a.attributes['history'] = 'Created by me'
    >>> print a.attributes
    {'long_name': 'variable a', 'history': 'Created by me'}

It's always better to use the correct syntax instead of the lazy one when writing code. Use the lazy syntax only when introspecting a dataset on the Python interpreter, to save a few keystrokes.

The fourth attribute is called ``data``, and it holds a representation of the actual data. We'll take a detailed look of this attribute in the next subsection.

Finally, all variables have also an attribute called ``_nesting_level``. This attribute has value 1 if the variable is inside a ``SequenceType`` object, 0 if it's outside, and >1 if it's inside a nested sequence. This will become clearer later when we talk about sequential data.

Data
~~~~

As we saw on the last subsection, all Pydap objects have a ``data`` attribute that holds a representation of the variable data. This representation will vary depending on the variable type. 

``BaseType``
************

For the simple ``BaseType`` objects the ``data`` attributes is usually a Numpy array, though we can also use a Numpy scalar or Python number:

.. doctest::

    >>> a = BaseType(name='a', data=1)
    >>> print a.data
    1

    >>> import numpy
    >>> b = BaseType(name='b', data=numpy.arange(4), shape=(4,))
    >>> print b.data
    [0 1 2 3]

Note that the default type for variables is ``Int32``:

.. doctest::

    >>> print a.type, b.type
    <class 'pydap.model.Int32'> <class 'pydap.model.Int32'>

When you *slice* a ``BaseType`` array, the slice is simply passed onto the data attribute. So we may have:

.. doctest::

    >>> print b[-1]
    3
    >>> print b[:2]
    [0 1]
    >>> print a[0]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pydap/model.py", line 188, in __getitem__
    TypeError: 'int' object is unsubscriptable
    
You can think of a ``BaseType`` object as a thin layer around Numpy arrays, until you realize that the ``data`` attribute can be *any* object implementing the array interface! This is how the DAP client works -- instead of assigning an array with data directly to the attribute, we assign a special object which behaves like an array and acts as a *proxy* to a remote dataset. 

Here's an example:

.. doctest::

    >>> from pydap.proxy import ArrayProxy
    >>> pseudo_array = ArrayProxy(
    ...         'SST.SST',
    ...         'http://test.opendap.org/dap/data/nc/coads_climatology.nc',
    ...         (12, 90, 180))
    >>> print pseudo_array[0, 10:14, 10:14]  # download the corresponding data
    [[ -1.26285708e+00  -9.99999979e+33  -9.99999979e+33  -9.99999979e+33]
     [ -7.69166648e-01  -7.79999971e-01  -6.75454497e-01  -5.95714271e-01]
     [  1.28333330e-01  -5.00000156e-02  -6.36363626e-02  -1.41666666e-01]
     [  6.38000011e-01   8.95384610e-01   7.21666634e-01   8.10000002e-01]]
    
In the example above, the data is only downloaded in the last line, when the pseudo array is sliced. The object will construct the appropriate DAP URL, request the data, unpack it and return a Numpy array. 

``StructureType``
*****************

A ``StructureType`` holds no data; instead, its ``data`` attribute is a property that collects data from the children variables:

.. doctest::

    >>> s = StructureType(name='s')
    >>> s[a.name] = a
    >>> s[b.name] = b
    >>> print a.data
    1
    >>> print b.data
    [0 1 2 3]
    >>> print s.data
    (1, array([0, 1, 2, 3]))

The opposite is also true; it's possible to specify the structure data and have it propagated to the children:

.. doctest::

    >>> s.data = (1, 2)
    >>> print s.a.data
    1
    >>> print s.b.data
    2

``SequenceType``
****************

A ``SequenceType`` object is a special kind of ``StructureType`` holding sequential data. Here's an example of a sequence holding the variables ``a`` and ``c`` that we created before:

.. doctest::

    >>> s = SequenceType(name='s')
    >>> s[a.name] = a
    >>> s[c.name] = c

Let's add

Handlers
--------

(easy way vs. efficient way)

Responses
---------
