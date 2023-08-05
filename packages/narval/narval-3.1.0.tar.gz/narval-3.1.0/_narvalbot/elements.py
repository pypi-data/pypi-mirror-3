from narvalbot import prototype


class ErrorElement(object):
    """create an error element

    :param msg: the error message
    :param type: the error's type
    :param from_msg: optional Internet message which has triggered the error
    """
    def __init__(self, msg, type='', from_msg=None):
        assert msg
        self.msg = msg
        self.type = type
        self.from_msg = from_msg
        self.eid = None


class FilePath(object):
    def __init__(self, path, host=None, **kwargs):
        self.path = path
        self.host = host
        self.__dict__.update(kwargs)


class HashableDict(dict):

    def __hash__(self):
        return hash(id(self))

    def copy(self):
        return self.__class__(self)

class Options(HashableDict):
    """Dictionary which stores action options."""


class EnsureOptions(HashableDict):
    """Ensure some options are set to a given value."""

    def added_to_narval_memory(self, memory):
        for element in memory.get_elements():
            if isinstance(element, Options):
                element.update(self)
                break
        else:
            self.__class__ = Options

prototype.EXPR_CONTEXT['ErrorElement'] = ErrorElement
prototype.EXPR_CONTEXT['FilePath'] = FilePath
prototype.EXPR_CONTEXT['Options'] = Options
prototype.EXPR_CONTEXT['EnsureOptions'] = EnsureOptions
