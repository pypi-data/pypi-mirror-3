from imposm.base import Node, Way, Relation
import sys
import os

import marshal

from ctypes import CDLL
from ctypes.util import find_library as _find_library
from ctypes import (
   c_void_p,
   c_char_p,
   c_int,
   c_double,
   c_long,
   c_int64,
   c_uint32,
   byref,
   cast,
   Structure,
   POINTER,
   pointer,
   create_string_buffer,
   addressof,
   sizeof,
   memmove,
   string_at,
   CFUNCTYPE,
)

default_locations = dict(
    darwin=dict(
        paths = ['/opt/local/lib'],
        exts = ['.dylib'],
    ),
    win32=dict(
        paths = [os.path.dirname(os.__file__) + '/../../../DLLs'],
        exts = ['.dll']
    )
)

#additional_lib_path = os.environ.get('MAPPROXY_LIB_PATH')
#if additional_lib_path:
#    additional_lib_path = additional_lib_path.split(os.pathsep)
#    additional_lib_path.reverse()
#    for locs in default_locations.values():
#        for path in additional_lib_path:
#            locs['paths'].insert(0, path)
#
def load_library(lib_names, locations_conf=default_locations):
    """
    Load the `lib_name` library with ctypes.
    If ctypes.util.find_library does not find the library,
    different path and filename extensions will be tried.
    
    Retruns the loaded library or None.
    """
    if isinstance(lib_names, basestring):
        lib_names = [lib_names]
    
    for lib_name in lib_names:
        lib = load_library_(lib_name, locations_conf)
        if lib is not None: return lib

def load_library_(lib_name, locations_conf=default_locations):
    lib_path = find_library(lib_name)
    
    if lib_path:
        return CDLL(lib_path)
    
    if sys.platform in locations_conf:
        paths = locations_conf[sys.platform]['paths']
        exts = locations_conf[sys.platform]['exts']
        lib_path = find_library(lib_name, paths, exts)
    
    if lib_path:
        return CDLL(lib_path)
        

def find_library(lib_name, paths=None, exts=None):
    """
    Search for library in all permutations of `paths` and `exts`.
    If nothing is found None is returned.
    """
    if not paths or not exts:
        lib = _find_library(lib_name)
        if lib is None and lib_name.startswith('lib'):
            lib = _find_library(lib_name[3:])
        return lib
    
    for lib_name in [lib_name] + ([lib_name[3:]] if lib_name.startswith('lib') else []):
        for path in paths:
            for ext in exts:
                lib_path = os.path.join(path, lib_name + ext)
                if os.path.exists(lib_path):
                    return lib_path
    
    return None
    
#cdef extern from "Python.h":
#    object PyString_FromStringAndSize(char *s, Py_ssize_t len)
#
#cdef extern from "marshal.h":
#    object PyMarshal_ReadObjectFromString(char *string, Py_ssize_t len)
#    object PyMarshal_WriteObjectToString(object value, int version)
#

TCBDB = c_void_p
BDBCUR = c_void_p
TCCMP = CFUNCTYPE(c_int, c_char_p, c_int, c_char_p, c_int, c_void_p)

def init_libtokyo_util():
    libtokyocabinet = load_library('libtokyocabinet')
    
    if libtokyocabinet is None: return
    
    #???
    #libtokyocabinet.TCCMP.argtypes = []
    #libtokyocabinet.TCCMP.restype = c_int
    #
    libtokyocabinet.tccmpint32.argtypes = []
    libtokyocabinet.tccmpint32.restype = c_int
    
    libtokyocabinet.tccmpint64.argtypes = []
    libtokyocabinet.tccmpint64.restype = c_long
    
    libtokyocabinet.tcbdbnew.argtypes = []
    libtokyocabinet.tcbdbnew.restype = TCBDB
    
    libtokyocabinet.tcbdbdel.argtypes = [TCBDB]
    libtokyocabinet.tcbdbdel.restype = None
    
    libtokyocabinet.tcbdbecode.argtypes = [TCBDB]
    libtokyocabinet.tcbdbecode.restype = c_int
    
    libtokyocabinet.tcbdbtune.argtypes = [TCBDB, c_int, c_int, c_int, c_int, c_int, c_int]
    libtokyocabinet.tcbdbtune.restype = c_int
    
    libtokyocabinet.tcbdbsetcache.argtypes = [TCBDB, c_int, c_int]
    libtokyocabinet.tcbdbsetcache.restype = c_int
    
    CMPFUNC = CFUNCTYPE(c_long)
    libtokyocabinet.tcbdbsetcmpfunc.argtypes = [TCBDB, c_void_p, c_void_p]
    libtokyocabinet.tcbdbsetcmpfunc.restype = c_int
    
    libtokyocabinet.tcbdbsetmutex.argtypes = [TCBDB]
    libtokyocabinet.tcbdbsetmutex.restype = c_int
    
    libtokyocabinet.tcbdbopen.argtypes = [TCBDB, c_char_p, c_int]
    libtokyocabinet.tcbdbopen.restype = c_int
    
    libtokyocabinet.tcbdbclose.argtypes = [TCBDB]
    libtokyocabinet.tcbdbclose.restype = c_int
    
    libtokyocabinet.tcbdbput.argtypes = [TCBDB, c_void_p, c_int, c_void_p, c_int]
    libtokyocabinet.tcbdbput.restype = c_int
    
    libtokyocabinet.tcbdbget.argtypes = [TCBDB, c_void_p, c_int, POINTER(c_int)]
    libtokyocabinet.tcbdbget.restype = c_void_p
    
    libtokyocabinet.tcbdbget3.argtypes = [TCBDB, c_void_p, c_int, POINTER(c_int)]
    libtokyocabinet.tcbdbget3.restype = c_void_p
    
    libtokyocabinet.tcbdbrnum.argtypes = [TCBDB]
    libtokyocabinet.tcbdbrnum.restype = c_long
    
    libtokyocabinet.tcbdbcurnew.argtypes = [TCBDB]
    libtokyocabinet.tcbdbcurnew.restypes = BDBCUR
    
    libtokyocabinet.tcbdbcurdel.argtypes = [BDBCUR]
    libtokyocabinet.tcbdbcurdel.restypes = None
    
    libtokyocabinet.tcbdbcurfirst.argtypes = [BDBCUR]
    libtokyocabinet.tcbdbcurfirst.restypes = c_int
    
    libtokyocabinet.tcbdbcurnext.argtypes = [BDBCUR]
    libtokyocabinet.tcbdbcurnext.restypes = c_int
    
    libtokyocabinet.tcbdbcurkey3.argtypes = [BDBCUR, POINTER(c_int)]
    libtokyocabinet.tcbdbcurkey3.restypes = c_void_p
    
    libtokyocabinet.tcbdbcurval3.argtypes = [BDBCUR, POINTER(c_int)]
    libtokyocabinet.tcbdbcurval3.restypes = c_void_p
    
    return libtokyocabinet

libtokyocabinet = init_libtokyo_util()

BDBFOPEN = 1 << 0
BDBFFATAL = 1 << 1

BDBOREADER = 1 << 0 # /* open as a reader */
BDBOWRITER = 1 << 1 # /* open as a writer */
BDBOCREAT = 1 << 2  # /* writer creating */
BDBOTRUNC = 1 << 3  # /* writer truncating */
BDBONOLCK = 1 << 4  # /* open without locking */
BDBOLCKNB = 1 << 5  # /* lock without blocking */
BDBOTSYNC = 1 << 6  # /* synchronize every transaction */

BDBTLARGE = 1 << 0  # /* use 64-bit bucket array */
BDBTDEFLATE = 1 << 1 # /* compress each page with Deflate */
BDBTBZIP = 1 << 2   # /* compress each record with BZIP2 */
BDBTTCBS = 1 << 3   # /* compress each page with TCBS */
BDBTEXCODEC = 1 << 4 # /* compress each record with outer functions */

COORD_FACTOR = 11930464.7083 # ((2<<31)-1)/360.0

def _coord_to_uint32(x):
    return int((x + 180.0) * COORD_FACTOR)

def _uint32_to_coord(x):
    return ((x / COORD_FACTOR) - 180.0)

def coord_struct(x, y):
    return Coord(x=_coord_to_uint32(x), y=_coord_to_uint32(y))

class Coord(Structure):
    _fields_ = [("x", c_uint32),
                ("y", c_uint32)]

_modes = {
    'w': BDBOWRITER | BDBOCREAT,
    'r': BDBOREADER | BDBONOLCK,
}

class BDB(object):
    def __init__(self, filename, mode='w', estimated_records=0):
        self.db = libtokyocabinet.tcbdbnew()
        self._cur = None
        self._opened = 0
        self.filename = filename
        self._tune_db(estimated_records)

        tccmpint64 = TCCMP(('tccmpint64', libtokyocabinet))
        libtokyocabinet.tcbdbsetcmpfunc(self.db, tccmpint64, None)

        # libtokyocabinet.tcbdbsetcmpfunc(self.db, libtokyocabinet.tccmpint64._get_address(), None)
        if not libtokyocabinet.tcbdbopen(self.db, filename, _modes[mode]):
            raise IOError(libtokyocabinet.tcbdbecode(self.db))
        self._opened = 1
    
    def _tune_db(self, estimated_records):
        if estimated_records:
            lmemb = 128 # default
            nmemb = -1
            fpow = 13 # 2^13 = 8196
            bnum = int((estimated_records*3)/lmemb)
            libtokyocabinet.tcbdbtune(self.db, lmemb, nmemb, bnum, 5, fpow, BDBTLARGE | BDBTDEFLATE)
        else:
            libtokyocabinet.tcbdbtune(self.db, -1, -1, -1, 5, 13, BDBTLARGE | BDBTDEFLATE)
    
    def get(self, osmid):
        """
        Return object with given id.
        Returns None if id is not stored.
        """
        ret_size = c_int()
        ret = libtokyocabinet.tcbdbget3(self.db, byref(c_int64(osmid)), 8, byref(ret_size))
        if not ret: return None
        data = string_at(ret, ret_size.value)
        return self._obj(osmid, marshal.loads(data))

    def get_raw(self, osmid):
        """
        Return object with given id.
        Returns None if id is not stored.
        """
        ret_size = c_int()
        ret = libtokyocabinet.tcbdbget3(self.db, byref(c_int64(osmid)), 8, byref(ret_size))
        if not ret: return None
        return string_at(ret, ret_size.value)

    def put(self, osmid, data):
        return self.put_marshaled(osmid, marshal.dumps(data, 2))

    def put_marshaled(self, osmid, data):
        return libtokyocabinet.tcbdbput(self.db, byref(c_int64(osmid)), 8, byref(create_string_buffer(data)), len(data))

    def _obj(self, osmid, data):
        """
        Create an object from the id and unmarshaled data.
        Should be overridden by subclasses.
        """
        return data

    def __iter__(self):
        """
        Return an iterator over the database.
        Resets any existing iterator.
        """
        if self._cur:
            libtokyocabinet.tcbdbcurdel(self._cur)
            self._cur = None
        self._cur = libtokyocabinet.tcbdbcurnew(self.db)
        print self.db, self._cur
        #libtokyocabinet.tcbdbcurfirst(self._cur)
        #if not libtokyocabinet.tcbdbcurfirst(self._cur):
        #    return iter([])
        return self

    def __contains__(self, osmid):
        ret_size = c_int()
        ret = tcbdbget3(self.db, byref(c_int64(osmid)), 8, byref(ret_size));
        if ret:
            return 1
        else:
            return 0
    
    def __len__(self):
        return libtokyocabinet.tcbdbrnum(self.db)
    
    def next(self):
        """
        Return next item as object.
        """
        #cdef int64_t osmid
        if not self._cur: raise StopIteration

        osmid, data = self._get_cur()

        # advance cursor, set to NULL if at the end
        if libtokyocabinet.tcbdbcurnext(self._cur) == 0:
            libtokyocabinet.tcbdbcurdel(self._cur)
            self._cur = None
        
        # return objectified item
        return self._obj(osmid, data)

    def _get_cur(self):
        """
        Return the current object at the current cursor position
        as a tuple of the id and the unmarshaled data.
        """
        size = c_int()
        ret = libtokyocabinet.tcbdbcurkey3(self._cur, byref(size))
        osmid = byref(ret)[0]
        ret = libtokyocabinet.tcbdbcurval3(self._cur, byref(size))
        data = string_at(ret, size.value)
        value = marshal.loads(data)
        return osmid, value

    def close(self):
        if self._opened:
            libtokyocabinet.tcbdbclose(self.db)
        self._opened = 0
    
    def __dealloc__(self):
        if self._opened:
            libtokyocabinet.tcbdbclose(self.db)
        libtokyocabinet.tcbdbdel(self.db)

class CoordDB(BDB):
    def put(self, osmid, x, y):
        return self._put(osmid, x, y)
    
    def put_marshaled(self, osmid, x, y):
        return self._put(osmid, x, y)
    
    def _put(self, osmid, x, y):
        p = coord_struct(x, y)
        return libtokyocabinet.tcbdbput(self.db, byref(c_int64(osmid)), 8, byref(p), 8)

    def get(self, osmid):
        ret_size = c_int
        value = libtokyocabinet.tcbdbget3(self.db, byref(c_int64(osmid)), 8, byref(ret_size))
        if not value: return
        coord = Coord()
        memmove(addressof(coord), value, sizeof(Coord))
        return _uint32_to_coord(coord.x), _uint32_to_coord(coord.y)

    def get_coords(self, refs):
        ret_size = c_int()
        coords = list()
        for osmid in refs:
            value = libtokyocabinet.tcbdbget3(self.db, byref(c_int64(osmid)), 8, byref(ret_size))
            if not value: return
            coord = Coord()
            memmove(addressof(coord), value, sizeof(Coord))
            coords.append((_uint32_to_coord(coord.x), _uint32_to_coord(coord.y)))
            
        return coords

    def _get_cur(self):
        size = c_int()
        ret = tcbdbcurkey3(self._cur, byref(size))
        osmid = byref(ret)[0]
        value = libtokyocabinet.tcbdbcurval3(self._cur, byef(size))
        return osmid, (_uint32_to_coord(value.x), _uint32_to_coord(value.y))

    def _obj(self, osmid, data):
        return osmid, data

class NodeDB(BDB):
    def put(self, osmid, tags, pos):
        return self.put_marshaled(osmid, marshal.dumps((tags, pos), 2))
    
    def put_marshaled(self, osmid, data):
        return libtokyocabinet.tcbdbput(self.db, byref(c_int64(osmid)), 8, byref(create_string_buffer(data)), len(data))

    def _obj(self, osmid, data):
        return Node(osmid, data[0], data[1])

class InsertedWayDB(BDB):
    def put(self, osmid):
        return libtokyocabinet.tcbdbput(self.db, byref(c_int64(osmid)), 8, 'x', 1);

    def __next__(self):
        """
        Return next item as object.
        """
        size = None
        
        if not self._cur: raise StopIteration

        ret = libtokyocabinet.tcbdbcurkey3(self._cur, byref(size))
        osmid = byref(ret)[0]

        # advance cursor, set to NULL if at the end
        if libtokyocabinet.tcbdbcurnext(self._cur) == 0:
            libtokyocabinet.tcbdbcurdel(self._cur)
            self._cur = None

        return osmid

class RefTagDB(BDB):
    """
    Database for items with references and tags (i.e. ways/relations).
    """
    def put(self, osmid, tags, refs):
        return self.put_marshaled(osmid, marshal.dumps((tags, refs), 2))
    
    def put_marshaled(self, osmid, data):
        return libtokyocabinet.tcbdbput(self.db, byref(c_int64(osmid)), sizeof(int64_t), byref(create_string_buffer(data)), len(data))

class WayDB(RefTagDB):
    def _obj(self, osmid, data):
        return Way(osmid, data[0], data[1])

class RelationDB(RefTagDB):
    def _obj(self, osmid, data):
        return Relation(osmid, data[0], data[1])

from imposm.cache.internal import DeltaCoords as _DeltaCoords
from collections import deque
import bisect

def unzip_nodes(nodes):
    ids, lons, lats = [], [], []
    last_id = last_lon = last_lat = 0
    for id, lon_f, lat_f in nodes:
        lon = _coord_to_uint32(lon_f)
        lat = _coord_to_uint32(lat_f)
        
        ids.append(id - last_id)
        lons.append(lon - last_lon)
        lats.append(lat - last_lat)
        last_id = id
        last_lon = lon
        last_lat = lat
    
    return ids, lons, lats

def zip_nodes(ids, lons, lats):
    nodes = []
    last_id = last_lon = last_lat = 0

    for i in range(len(ids)):
        last_id += ids[i]
        last_lon += lons[i]
        last_lat += lats[i]
    
        nodes.append((
            last_id,
            _uint32_to_coord(last_lon),
            _uint32_to_coord(last_lat)
        ))
    return nodes

class DeltaNodes(object):
    def __init__(self, data=None):
        self.nodes = []
        self.changed = False
        if data:
            self.deserialize(data)
    
    def changed(self):
        return self.changed
    
    def get(self, osmid):
        i = bisect.bisect(self.nodes, (osmid, ))
        if i != len(self.nodes) and self.nodes[i][0] == osmid:
            return self.nodes[i][1:]
        return None
    
    def add(self, osmid, lon, lat):
        # todo: overwrite
        self.changed = True
        if self.nodes and self.nodes[-1][0] < osmid:
            self.nodes.append((osmid, lon, lat))
        else:
            bisect.insort(self.nodes, (osmid, lon, lat))
    
    def serialize(self):
        ids, lons, lats = unzip_nodes(self.nodes)
        nodes = _DeltaCoords()
        nodes.ids.extend(ids)
        nodes.lons.extend(lons)
        nodes.lats.extend(lats)
        return nodes.SerializeToString()
    
    def deserialize(self, data):
        nodes = _DeltaCoords()
        nodes.ParseFromString(data)
        self.nodes = zip_nodes(
            nodes.ids, nodes.lons, nodes.lats)

class DeltaCoordsDB(object):
    def __init__(self, filename, mode='w', estimated_records=0, delta_nodes_cache_size=100, delta_nodes_size=6):
        self.db = BDB(filename, mode, estimated_records)
        self.mode = mode
        self.delta_nodes = {}
        self.delta_node_ids = deque()
        self.delta_nodes_cache_size = delta_nodes_cache_size
        self.delta_nodes_size = delta_nodes_size
    
    def put(self, osmid, lon, lat):
        if self.mode == 'r':
            return None
        delta_id = osmid >> self.delta_nodes_size
        if delta_id not in self.delta_nodes:
            self.fetch_delta_node(delta_id)
        delta_node = self.delta_nodes[delta_id]
        delta_node.add(osmid, lon, lat)
        return True
    
    put_marshaled = put
    
    def get(self, osmid):
        delta_id = osmid >> self.delta_nodes_size
        if delta_id not in self.delta_nodes:
            self.fetch_delta_node(delta_id)
        return self.delta_nodes[delta_id].get(osmid)
    
    def get_coords(self, osmids):
        coords = []
        for osmid in osmids:
            coord = self.get(osmid)
            if coord is None:
                return
            coords.append(coord)
        return coords
    
    def close(self):
        for node_id, node in self.delta_nodes.iteritems():
            self._put(node_id, node)
        self.delta_nodes = {}
        self.delta_node_ids = deque()
        self.db.close()
    
    def _put(self, delta_id, delta_node):
        data = delta_node.serialize()
        self.db.put_marshaled(delta_id, data)
    
    def _get(self, delta_id):
        return DeltaNodes(data=self.db.get_raw(delta_id))
    
    def fetch_delta_node(self, delta_id):
        if len(self.delta_node_ids) >= self.delta_nodes_cache_size:
            rm_id = self.delta_node_ids.popleft()
            rm_node = self.delta_nodes.pop(rm_id)
            if rm_node.changed:
                self._put(rm_id, rm_node)
        new_node = self._get(delta_id)
        if new_node is None:
            new_node = DeltaNodes()
        self.delta_nodes[delta_id] = new_node
        self.delta_node_ids.append(delta_id)

