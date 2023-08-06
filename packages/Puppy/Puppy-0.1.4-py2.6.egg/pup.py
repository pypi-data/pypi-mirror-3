import numpy


class Dimension(object):
    def __init__(self, length):
        self.length = length


class Variable(object):
    def __init__(self, data, dimensions=None, record=False, **kwargs):
        # replace masked data --if any-- with missing_value.
        missing_value = (
                kwargs.get('missing_value') or
                kwargs.get('_FillValue') or 
                getattr(data, 'fill_value', 999999))
        kwargs.setdefault('missing_value', missing_value)
        kwargs.setdefault('_FillValue', missing_value)
        self.data = numpy.ma.asarray(data).filled(missing_value)

        self.dimensions = dimensions
        self.record = record
        self.attributes = kwargs


class NetCDF(object):
    @classmethod
    def save(klass, filename, **kwargs):
        # find netcdf loader
        if hasattr(klass, 'loader') and callable(getattr(klass, 'loader')):
            loader = getattr(klass, 'loader')
        else:
            from pupynere import netcdf_file as loader
        out = loader(filename, 'w', **kwargs)

        # add attributes
        for name in dir(klass):
            attr = getattr(klass, name)
            if isinstance(attr, basestring) and not attr.startswith('_'):
                setattr(out, name, attr)

        # add explicitly defined dimensions
        for name in dir(klass):
            attr = getattr(klass, name)
            if isinstance(attr, Dimension):
                out.createDimension(name, attr.length)

        # set variable names from the class
        for name in dir(klass):
            attr = getattr(klass, name)
            if isinstance(attr, Variable):
                attr.name = name

        # add variables, and add their dimensions if necessary
        for name in dir(klass):
            attr = getattr(klass, name)
            if isinstance(attr, Variable):
                # add dimension?
                if attr.dimensions is None:
                    attr.dimensions = [ attr ]
                for dim in attr.dimensions:
                    if dim.name not in out.dimensions:
                        if dim.record:
                            out.createDimension(dim.name, None)
                        else:
                            out.createDimension(dim.name, len(dim.data))

                # create var
                if attr.data.dtype == numpy.int64:
                    attr.data = attr.data.astype(numpy.int32)
                var = out.createVariable(
                        attr.name, 
                        attr.data.dtype, 
                        tuple(dim.name for dim in attr.dimensions))
                var[:] = attr.data[:]
                for k, v in attr.attributes.items():
                    setattr(var, k, v)

        out.close()
