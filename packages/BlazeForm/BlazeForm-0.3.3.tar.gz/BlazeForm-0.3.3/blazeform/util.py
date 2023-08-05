from webhelpers.html import literal

class StringIndentHelper(object):

    def __init__(self):
        self.output = []
        self.level = 0
        self.indent_with = '    '

    def dec(self, value):
        self.level -= 1
        return self.render(value)

    def inc(self, value):
        self.render(value)
        self.level += 1

    def __call__(self, value, **kwargs):
        self.render(value)

    def render(self, value, **kwargs):
        self.output.append('%s%s' % (self.indent(**kwargs), value) )

    def indent(self, level = None):
        if level == None:
            return self.indent_with * self.level
        else:
            return self.indent_with * self.level

    def get(self):
        retval = '\n'.join(self.output)
        self.output = []
        return retval

def is_empty(value):
    if not value and value is not 0 and value is not False:
        return True
    return False

def multi_pop(d, *args):
    retval = {}
    for key in args:
        if d.has_key(key):
            retval[key] = d.pop(key)
    return retval

class NotGivenBase(object):
    """ an empty sentinel object """

    def __str__(self):
        return ''

    def __unicode__(self):
        return u''

    def __nonzero__(self):
        return False

    def __ne__(self, other):
        if other == '' or other == u'' or other is None or isinstance(other, NotGivenBase):
            return False
        return True

    def __eq__(self, other):
        if other == '' or other == u'' or other is None or isinstance(other, NotGivenBase):
            return True
        return False
NotGiven = NotGivenBase()

class NotGivenIterBase(NotGivenBase):
    def __str__(self):
        return '[]'

    def __unicode__(self):
        return u'[]'

    def __nonzero__(self):
        return False

    def __ne__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return False
        return True

    def __eq__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return True
        return False

    # we also want to emulate an empty list
    def __iter__(self):
        return self

    def next(self):
        raise StopIteration

    def __len__(self):
        return 0
NotGivenIter = NotGivenIterBase()

def tolist(x, default=[]):
    if x is None:
        return default
    if isinstance(x, list):
        return x
    if isinstance(x, tuple):
        return list(x)
    return [x]

def is_iterable(possible_iterable):
    if isinstance(possible_iterable, basestring):
        return False
    try:
        iter(possible_iterable)
        return True
    except TypeError:
        return False

def is_notgiven(object):
    return isinstance(object, NotGivenBase)

def is_given(object):
    return not isinstance(object, NotGivenBase)

class ElementRegistrar(object):
    def __init__(self, formref, is_group = False):
        self._formref = formref
        self._is_group = is_group

    def __getattr__(self, name):
        """
            we want to enable add_* methods on the object
            that correspond to elements we have available
        """
        if name.startswith('add_'):
            type = name.replace('add_', '')
            func = self._create_element
        elif self._formref.els.has_key(name):
            return self._formref.els[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

        def wrapper(eid, *args, **kwargs):
            return func(type, eid, *args, **kwargs)
        return wrapper

    def _create_element(self, type, eid, *args, **kwargs):
        if type == 'file':
            self._formref.set_attr('enctype', 'multipart/form-data')
        if self._formref.els.has_key(eid):
            raise ValueError('element id "%s" already used' % eid)

        try:
            eclass = self._formref._registered_types[type]
        except KeyError:
            raise ValueError('"%s" is not a registered element type' % type)

        el = eclass(self._formref, eid, *args, **kwargs)
        if self._is_group:
            el.renders_in_group = True
            self.els[eid] = el
        self._formref.els[eid] = el
        return el

class HtmlAttributeHolder(object):
    def __init__(self, **kwargs):
        self._cleankeys(kwargs)
        #: a dictionary that represents html attributes
        self.attributes = kwargs

    def set_attrs(self, **kwargs ):
        self._cleankeys(kwargs)
        self.attributes.update(kwargs)

    def set_attr(self, key, value):
        if key.endswith('_'):
            key = key[:-1]
        self.attributes[key] = value

    def add_attr(self, key, value):
        """
            Creates a space separated string of attributes.  Mostly for the
            "class" attribute.
        """
        if key.endswith('_'):
            key = key[:-1]
        if self.attributes.has_key(key):
            self.attributes[key] = self.attributes[key] + ' ' + value
        else:
            self.attributes[key] = value

    def del_attr(self, key):
        if key.endswith('_'):
            key = key[:-1]
        del self.attributes[key]

    def get_attrs(self):
        return self.attributes

    def get_attr(self, key, defaultval = NotGiven):
        try:
            if key.endswith('_'):
                key = key[:-1]
            return self.attributes[key]
        except KeyError:
            if defaultval is not NotGiven:
                return defaultval
            raise

    def _cleankeys(self, dict):
        """
            When using kwargs, some attributes can not be sent directly b/c
            they are Python key words (i.e. "class") so that have to be sent
            in with an underscore at the end (i.e. "class_").  We want to
            remove the underscore before saving
        """
        for key, val in dict.items():
            if key.endswith('_'):
                del dict[key]
                dict[key[:-1]] = val
