import os
import re
import time
from stat import ST_MTIME
from email.utils import formatdate

import numpy

from arrayterator import Arrayterator

from pydap.model import *
from pydap.lib import fix_slice
from pydap.handlers.lib import BaseHandler
from pydap.exceptions import OpenFileError

from cdms2 import open as open_file


var_attrs = lambda var: dict(var.attributes)
get_value = lambda var: var.getValue()


class Handler(BaseHandler):

    extensions = re.compile(r"^.*\.(ctl|pp)$", re.IGNORECASE)

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_constraints(self, environ):
        buf_size = int(environ.get('pydap.handlers.grads.buf_size', 10000))

        try:
            fp = open_file(self.filepath)
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        last_modified = formatdate( time.mktime( time.localtime( os.stat(self.filepath)[ST_MTIME] ) ) )
        environ['pydap.headers'].append( ('Last-modified', last_modified) )

        dataset = DatasetType(name=os.path.split(self.filepath)[1],
                attributes={'NC_GLOBAL': var_attrs(fp)})
        for dim in fp.listdimension():
            #!FIXME: FileAxis.isUnlimited() doesn't work.  This has
            #        been reported to PCMDI
            if fp._file_.dimensions[dim] is None:
                dataset.attributes['DODS_EXTRA'] = {'Unlimited_Dimension': dim}
                break

        fields, queries = environ['pydap.ce']
        fields = fields or [[(name, ())] for name in fp.variables.keys() + fp.listdimension()]
        for var in fields:
            target = dataset
            while var:
                name, slice_ = var.pop(0)
                if (name in fp.listdimension() or
                        not fp.variables[name].listdimnames() or
                        target is not dataset):
                    target[name] = get_var(name, fp, slice_, buf_size)
                elif var:
                    attrs = var_attrs(fp.variables[name])
                    target.setdefault(name, StructureType(name=name, attributes=attrs))
                    target = target[name]
                else:  # return grid
                    attrs = var_attrs(fp.variables[name])
                    grid = target[name] = GridType(name=name, attributes=attrs)
                    grid[name] = get_var(name, fp, slice_, buf_size)
                    slice_ = list(slice_) + [slice(None)] * (len(grid.array.shape) - len(slice_))
                    for dim, dimslice in zip(fp.variables[name].listdimnames(), slice_):
                        grid[dim] = get_var(dim, fp, dimslice, buf_size)

        dataset._set_id()
        dataset.close = fp.close
        return dataset


def get_var(name, fp, slice_, buf_size=10000):
    if name in fp.variables:
        var = fp.variables[name]
        if var.shape: 
            data = Arrayterator(var, buf_size)[slice_]
        else:
            data = numpy.array(get_value(var))
        typecode = var.typecode()
        dims = tuple(var.listdimnames())
        attrs = var_attrs(var)
    elif name in fp.listdimension():
        var = fp.getAxis(name)
        slice_ = fix_slice(slice_, var.shape)[0]
        data = var[slice_]
        typecode = var.typecode()
        dims = (name,)
        attrs = var_attrs(var)
    else:
        if fp.listdimension().get(name) is not None:
            size = len(fp.dimensionobject(name))
        else:
            for var in fp.variables:
                var = fp.variables[var]
                if name in fp.variables[name].listdminames():
                    size = var.shape[
                            fp.variables[name].listdimnames().index(name)]
                    break
        data = numpy.arange(size)[slice_]
        typecode = data.dtype.char
        dims, attrs = (name,), {}

    return BaseType(name=name, data=data, shape=data.shape,
            type=typecode, dimensions=dims,
            attributes=attrs)


if __name__ == '__main__':
    import sys
    from paste.httpserver import serve

    application = Handler(sys.argv[1])
    serve(application, port=8001)
