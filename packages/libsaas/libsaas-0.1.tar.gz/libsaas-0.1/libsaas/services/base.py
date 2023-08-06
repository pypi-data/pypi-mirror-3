import inspect
from functools import update_wrapper

from libsaas import http, parsers
from libsaas.executors import current

decorator = None
try:
    import decorator
except ImportError:
    pass


def wrap(wrapper, wrapped):
    """
    Either use the decorator module, or the builtin functools.update_wrapper
    function to wrap one function with another.

    Using decorator is preferred, because it maintains argument specification,
    making automatic documentation output look better.
    """
    if decorator:
        return decorator.decorator(wrapper, wrapped)
    return update_wrapper(wrapper, wrapped)


class MethodNotSupported(NotImplementedError):
    """
    This resource does not implement the method.
    """
    def __str__(self):
        return self.__class__.__doc__


def apimethod(f):

    def wrapped(*args, **kwargs):
        # when using decorator the first argument passed to the wrapping
        # function is the wrapped function, so discard it if it's the case
        if args and args[0] is f:
            args = args[1:]

        # call the wrapped function, apply the filters and pass the result on
        # to the executor
        request, parser = f(*args, **kwargs)
        args[0].apply_filters(request)
        return current.process(request, parser)

    wrapped = wrap(wrapped, f)
    wrapped.is_apimethod = True
    return wrapped


def resource(*klasses):

    def wrapper(f):
        f.is_resource = True
        f.produces = klasses
        return f

    return wrapper


def methods_with_attribute(cls, attribute):
    return [name for name, method in
            inspect.getmembers(cls, (lambda obj: inspect.ismethod(obj) and
                                     getattr(obj, attribute, False)))]


class Resource(object):
    """
    Base class for all resources.
    """
    filters = ()
    parent = None

    @classmethod
    def list_resources(cls):
        return methods_with_attribute(cls, 'is_resource')

    @classmethod
    def list_methods(cls):
        return methods_with_attribute(cls, 'is_apimethod')

    def __init__(self, parent):
        self.parent = parent

    def require(self, condition):
        if not condition:
            raise MethodNotSupported()

    def add_filter(self, filter_function):
        self.filters += (filter_function, )

    def apply_filters(self, request):
        if self.parent is not None:
            self.parent.apply_filters(request)

        for f in self.filters:
            f(request)


class HierarchicalResource(Resource):
    """
    Base class for resources whose URL is relative to a parent resource's URL.
    """
    path = None

    def __init__(self, parent, object_id=None):
        self.parent = parent
        self.object_id = object_id

    def get_url(self):
        if self.object_id is None:
            return '{0}/{1}'.format(self.parent.get_url(), self.path)

        return '{0}/{1}/{2}'.format(self.parent.get_url(), self.path,
                                    self.object_id)


class RESTResource(HierarchicalResource):
    """
    Base class for resources implementing the classical CRUD operations with
    HTTP verbs.
    """
    @apimethod
    def get(self):
        """
        For single-object resources, fetch the object's data. For collections,
        fetch all of the objects.
        """
        request = http.Request('GET', self.get_url())

        return request, parsers.parse_json

    @apimethod
    def create(self, obj):
        """
        Create a new resource.

        :var obj: a Python object representing the resource to be created,
            usually in the same as returned from `get`. Refer to the upstream
            documentation for details.
        """
        self.require_collection()
        request = http.Request('POST', self.get_url(), self.wrap_object(obj))

        return request, parsers.parse_json

    @apimethod
    def update(self, obj):
        """
        Update this resource.

        :var obj: a Python object representing the updated resource, usually in
            the same format as returned from `get`. Refer to the upstream
            documentation for details.
        """
        self.require_item()
        request = http.Request('PUT', self.get_url(), self.wrap_object(obj))

        return request, parsers.parse_json

    @apimethod
    def delete(self):
        """
        Delete this resource.
        """
        self.require_item()
        request = http.Request('DELETE', self.get_url())

        return request, parsers.parse_empty

    def require_collection(self):
        if self.object_id is not None:
            raise MethodNotSupported()

    def require_item(self):
        if self.object_id is None:
            raise MethodNotSupported()

    def wrap_object(self, obj):
        return obj
