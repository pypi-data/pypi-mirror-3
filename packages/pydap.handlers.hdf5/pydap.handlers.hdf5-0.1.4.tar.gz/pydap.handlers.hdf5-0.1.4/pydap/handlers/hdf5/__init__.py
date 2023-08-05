import os
import re
import time
from stat import ST_MTIME
from email.utils import formatdate

import numpy
import h5py

from arrayterator import Arrayterator

from pydap.model import *
from pydap.handlers.lib import BaseHandler
from pydap.exceptions import OpenFileError


class Handler(BaseHandler):

    extensions = re.compile(r"^.*\.(h5|hdf5)$", re.IGNORECASE)

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_constraints(self, environ):
        buf_size = int(environ.get('pydap.handlers.netcdf.buf_size', 10000))

        try:
            fp = h5py.File(self.filepath, 'r')
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        last_modified = formatdate( time.mktime( time.localtime( os.stat(self.filepath)[ST_MTIME] ) ) )
        environ['pydap.headers'].append( ('Last-modified', last_modified) )

        dataset = DatasetType(name=os.path.split(self.filepath)[1],
                attributes={'NC_GLOBAL': dict(fp.attrs)})

        fields, queries = environ['pydap.ce']
        fields = fields or [[(name, ())] for name in fp.keys()]
        for var in fields:
            get_child(fp, dataset, var, buf_size)

        dataset._set_id()
        dataset.close = fp.close
        return dataset


def get_child(source, target, var, buf_size):
    while var:
        name, slice_ = var.pop(0)
        if name in source and isinstance(source[name], h5py.Dataset):
            target[name] = get_var(name, source, slice_, buf_size)
        elif name in source and isinstance(source[name], h5py.Group):
            attrs = dict(source[name].attrs)
            target.setdefault(name, StructureType(name=name, attributes=attrs))
            target = target[name]
            source = source[name]

            # when a group is requested by itself, return with all children
            if not var:
                for name in source.keys():
                    get_child(source, target, [(name, ())], buf_size)


def get_var(name, source, slice_, buf_size=10000):
    var = source[name]
    if var.shape:
        data = Arrayterator(var, buf_size)[slice_]
    else:
        data = numpy.array(var.value)
    typecode = var.dtype.char
    attrs = dict(var.attrs)
    attrs['_FillValue'] = var.fillvalue

    return BaseType(name=name, data=data, shape=data.shape,
            type=typecode, attributes=attrs)


if __name__ == '__main__':
    import sys
    from paste.httpserver import serve

    application = Handler(sys.argv[1])
    serve(application, port=8001)
