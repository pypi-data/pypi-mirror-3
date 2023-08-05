r"""
A tiling Opendap-aware caching proxy server.

This program is a proxy to any Opendap server. Data requests (dods,
ascii and other configurable responses) are cached locally by an
Opendap-aware algorithm; this means that requests for a subset of
data that was already requested, eg, will be read from cache even
though the URLs may be completely different.

The caching mechanism works by splitting an n-dimensional dataset
in pairs of tiles, like a binary k-d tree::

        A 
       / \
      B   C
     /|   |\
    D E   F G

When a slice of the data is requested we check each tile to see if
the data is contained in that tile. The result may be this, eg::

        1 
       / \
      1   1
     /|   |\
    1 1   1 0

In order to download the data with the least transferred bytes we
need to request tiles B and F from the Opendap server, store it
locally, and then return the requested slice (which is contained
in the cached data). If the node E is already in the cache we can
request D instead of B, to minimize downloaded data.

(c) 2011 Roberto De Almeida <roberto@dealmeida.net>

"""
from __future__ import division

import sys, logging
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger('pydap')
logger.setLevel(logging.INFO)

import os
from urlparse import urljoin
from collections import defaultdict

from webob import Request
from paste.proxy import Proxy
import h5py
import numpy as np

from pydap.client import open_url
from pydap.handlers.lib import SimpleHandler
from pydap.lib import walk, combine_slices, fix_slice, hyperslab
from pydap.model import *
from pydap.proxy import ArrayProxy
from pydap.util.rwlock import ReadWriteLock


TILESIZE = int(2e6)  # bytes
LOCK = defaultdict(ReadWriteLock)

# TODO:
# clean code, implement explicit k-d tree
# improve storage
# check Last-modified and expire cache if stale
# check if cache has exceeded its size


class Node(object):
    pass


def KDTree(shape, data):
    """
    Build a k-d tree for a given shape and a data vector.

    """
    root = Node()
    root.start = list(0 for dim in shape)
    root.end = list(shape)

    queue = [ (0, root) ]
    while queue:
        i, node = queue.pop(0)
        node.value = data[i]

        if 2*i+2 < len(data):
            # split along longest dimension, finding the middle point
            shape = tuple(end-start for start, end in zip(node.start, node.end))
            axis = shape.index(max(shape))
            middle = int(node.start[axis] + np.floor(shape[axis] / 2))

            # left node goes from start to the middle point
            node.left = Node()
            node.left.start = node.start
            node.left.end = node.end[:]
            node.left.end[axis] = middle
            queue.append( (2*i+1, node.left) )

            # and right goes from middle to end
            node.right = Node()
            node.right.start = node.start[:]
            node.right.start[axis] = middle
            node.right.end = node.end
            queue.append( (2*i+2, node.right) )

    return root


class DapCache(object):
    def __init__(self, url, responses, cachedir):
        self.url = url
        self.responses = responses
        if not os.path.exists(cachedir):
            os.mkdir(cachedir)
        self.cachedir = cachedir

    def __call__(self, environ, start_response):
        req = Request(environ)
        if '.' in req.path_info:
            basename, response = req.path_info.rsplit('.', 1)
        else:
            basename, response = req.path_info, None

        # cache a local copy
        if response in self.responses:
            dataset = open_url(urljoin(self.url, basename))
            cachepath = os.path.join(self.cachedir, basename.replace('/', '_'))
            # here we an use mstat to check the mtime of the file, and 
            # do a HEAD on the dataset to compare with Last-Modified header
            CACHE_EXPIRED = False
            if CACHE_EXPIRED:
                os.unlink(cachepath)

            for var in walk(dataset, BaseType):
                var.data = CachingArrayProxy(
                        cachepath, var.type,
                        var.id, var.data.url, var.data.shape, var.data._slice)
            app = SimpleHandler(dataset)
        # pass this upstream
        else:
            app = Proxy(self.url)

        return app(environ, start_response)


class CachingArrayProxy(ArrayProxy):
    def __init__(self, cachepath, dtype, id, url, shape, slice_=None):
        super(CachingArrayProxy, self).__init__(id, url, shape, slice_)

        self.lock = LOCK[cachepath]
        self.fp = h5py.File(cachepath, 'a')

        # how many tiles are we using for the cache? we can calculate
        # this analytically, but this way is more explicit... ;)
        size = np.prod(shape) * dtype.size
        divisions = 0
        while size > TILESIZE:
            size = np.ceil(size/2)
            divisions += 1
        self.tiles = 2**divisions

        # open cache data/index and create arrays if necessary
        with self.lock.readlock:
            if id not in self.fp:
                with self.lock.writelock:
                    self.fp.create_dataset(id, shape, dtype.typecode)
            if 'index' not in self.fp:
                with self.lock.writelock:
                    self.fp.create_group('index')
            if id not in self.fp['index']:
                with self.lock.writelock:
                    self.fp['index'].create_dataset(id, (self.tiles,), bool)
        self.cache = self.fp[id]
        self.index = self.fp['index'][id]

    def __getitem__(self, index):
        """
        Download data for all the files containing the request.

        """
        slice_ = combine_slices(self._slice, fix_slice(index, self.shape))
        requested = self.parse_request(slice_)
        with self.lock.readlock:
            needed = requested & ~self.index[:]

            # update cache with needed data
            with self.lock.writelock:
                for tile in self.get_tiles(needed):
                    self.cache[tile] = super(CachingArrayProxy, self).__getitem__(tile)
                # update index with newly requested data
                self.index[:] = self.index[:] | needed

            return self.cache[slice_]

    def parse_request(self, slice_):
        """
        Parse a slice request into an array of requested tiles.

        We create a binary tree of the n-dimensional hypervolume of the
        dataset, and keep dividing it and marking if the request is inside
        the tiles. We then return the leaves of the tree, corresponding
        to the smallest tiles that are required, in order to compare them
        with the cache index.

        """
        root = KDTree(self.shape, np.zeros(self.tiles*2-1, dtype=bool))

        def contained(node, slice_):
            for s, min_, max_ in zip(slice_, node.start, node.end):
                if s.stop <= min_ or s.start >= max_:
                    break
            else:
                node.value = 1
                if node.left is not None and node.right is not None:
                    contained(node.left, slice_)
                    contained(node.right, slice_)

        contained(root, slice_)
        return root

        # binary tree as array
        tree = np.zeros(self.tiles*2-1, dtype=bool)

        def contained(i, slice_, start, end, axis=0):
            for s, min_, max_ in zip(slice_, start, end):
                if s.stop <= min_ or s.start >= max_:
                    break
            else:
                tree[i] = 1
                # find an axis in which to split the dataset.
                axis = axis % len(end)
                while end[axis] == 1:
                    axis = (axis + 1) % len(end)
                j = start[axis] + np.floor((end[axis] - start[axis]) / 2)
                end_, start_ = end[:], start[:]
                end_[axis] = start_[axis] = int(j)

                # check left and right nodes
                if 2*i+2 < len(tree):
                    contained(2*i+1, slice_, start, end_, axis+1) 
                    contained(2*i+2, slice_, start_, end, axis+1)

        # check root element and its children
        start = list(0 for dim in self.shape)
        end = list(self.shape)
        contained(0, slice_, start, end)

        return tree[-self.tiles:]

    def get_tiles(self, needed):
        r"""
        Combine needed tiles and return them as slices.

        We create a k-d tree and go from the top to the bottom.
        If for a given node all its lower children are needed, say::

                0 
               / \
              0   0
             /|   |\
            1 1   1 1
            
        We can make a request for a continuous region that contains
        all child nodes.

        """
        root = KDTree(self.shape, np.zeros(self.tiles*2-1, dtype=bool))
        
        def check_node(root):

        return check_node(root)



        # binary tree as array
        tree = np.zeros(self.tiles*2-1, dtype=bool)
        tree[-self.tiles:] = needed[:]

        def check_leaves(i):
            if i*2+2 > len(tree):
                return tree[i]
            else:
                return check_leaves(i*2+1) and check_leaves(i*2+2)

        def check_node(i, start, end, axis=0):
            if check_leaves(i):
                yield tuple(slice(min_, max_, 1) for min_, max_ in zip(start, end))
            else:
                # find an axis in which to split the dataset.
                axis = axis % len(end)
                while end[axis] == 1:
                    axis = (axis + 1) % len(end)
                j = start[axis] + np.floor((end[axis] - start[axis]) / 2)
                end_, start_ = end[:], start[:]
                end_[axis] = start_[axis] = int(j)

                # check left and right nodes
                if 2*i+2 < len(tree):
                    for slice_ in check_node(2*i+1, start, end_, axis+1):
                        yield slice_
                    for slice_ in check_node(2*i+2, start_, end, axis+1):
                        yield slice_

        # check root element and its children
        start = list(0 for dim in self.shape)
        end = list(self.shape)
        return check_node(0, start, end)


def make_cache(global_conf, url, responses, **kwargs):
    from paste.deploy.converters import aslist
    responses = aslist(responses)
    return DapCache(url, responses, **kwargs)


if __name__ == '__main__':
    app = DapCache('http://opendap.ccst.inpe.br/', ['dods', 'asc', 'ascii'], '.cache')
    from paste import httpserver
    httpserver.serve(app, '127.0.0.1', port=8003)
