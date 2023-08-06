import decimal

from formencode import Invalid
from formencode.validators import FancyValidator

from blazeform.exceptions import ValueInvalid
from blazeform.util import tolist, is_iterable, is_notgiven


class Select(FancyValidator):
    """
    Invalid if the value(s) did not come from the options or came from the
    invalid options list
    """
    
    invalid = []
    as_empty = []
    handles_multiples = True
    __unpackargs__ = ('options', 'invalid', 'as_empty')
    messages = {
        'notthere': "the value did not come from the given options",
        'invalid': "the value chosen is invalid",
        }
    
    def _to_python(self, value, state):
        valiter = tolist(value)
        as_empty = [unicode(d) for d in tolist(self.as_empty)]
        vallist = [unicode(d) for d in valiter]
        # single
        if len(vallist) == 1:
            if vallist[0] in as_empty:
                return None
            return value
        # multiple
        to_remove = []
        for index, val in enumerate(vallist):
            if val in as_empty:
                to_remove.append(index)
        adjust = 0
        for index in to_remove:
            del valiter[index-adjust]
            adjust += 1
        return valiter
        
    def validate_other(self, values, state):
        soptions = set([unicode(d[0] if isinstance(d, tuple) else d) for d in self.options])
        sinvalid = set([unicode(d) for d in tolist(self.invalid)])
        svalues = set([unicode(d) for d in tolist(values)])
 
        if len(sinvalid.intersection(svalues)) != 0:
            raise Invalid(self.message('invalid', state), values, state)

        if len(soptions.intersection(svalues)) != len(svalues):
            raise Invalid(self.message('notthere', state), values, state)
        
        return
    
class Confirm(FancyValidator):
    """
        Matches one field's value with another
    """
    
    __unpackargs__ = ('tomatch', )
    messages = {
        'notequal': 'does not match field "%(field)s"'
        }

    def is_empty(self, value):
        """need to override, otherwise validate_python never gets called"""
        return False
    
    def validate_python(self, value, state):
        if self.tomatch.is_valid() and self.tomatch.value != value:
            raise Invalid(self.message('notequal', state, field=str(self.tomatch.label)), value, state)

    
class MultiValues(FancyValidator):
    """
        Ensures that single value fields never get a list/tuple and therefore
        always return a non-iterable value.  For INTERNAL use.
    """
    
    multi_check = True
    __unpackargs__ = ('validator','multi_check')
    messages = {
        'nonmultiple': 'this field does not accept more than one value'
        }
    
    def is_empty(self, value):
        """ need this so our confirm element can function correctly """
        if isinstance(self.validator, FancyValidator):
            return self.validator.is_empty(value)
        # None and '' are "empty"
        return value is None or value == '' or (
            isinstance(value, (list, tuple, dict)) and not value)
    
    def _to_python(self, value, state):
        field = state
        multiple = getattr(field, 'multiple', False)
        if self.multi_check:
            if not multiple:
                if is_iterable(value):
                    raise Invalid(self.message('nonmultiple', state), value, state)

        # now apply the validator to the value
        if not multiple or is_notgiven(value) or getattr(self.validator, 'handles_multiples', False):
            return self.validator.to_python(value, state)
        else:
            retval = []
            for v in tolist(value):
                retval.append(self.validator.to_python(v, state))
            return retval

class Wrapper(FancyValidator):

    """
    Used to convert functions to validator/converters.

    You can give a simple function for `to_python`, `from_python`,
    `validate_python` or `validate_other`.  If that function raises an
    ValueInvalid exception, the value is considered invalid.  Whatever value
    the function returns is considered the converted value.

    Unlike validators, the `state` argument is not used.

    """

    func_to_python = None
    func_from_python = None
    func_validate_python = None
    func_validate_other = None

    def __init__(self, *args, **kw):
        for n in ['to_python', 'from_python', 'validate_python',
                  'validate_other']:
            if kw.has_key(n):
                kw['func_%s' % n] = kw[n]
                del kw[n]
        FancyValidator.__init__(self, *args, **kw)
        self._to_python = self.wrap(self.func_to_python)
        self._from_python = self.wrap(self.func_from_python)
        self.validate_python = self.wrap(self.func_validate_python)
        self.validate_other = self.wrap(self.func_validate_other)

    def wrap(self, func):
        if not func:
            return None
        def result(value, state, func=func):
            try:
                return func(value)
            except ValueInvalid, e:
                raise Invalid(str(e), {}, value, state)
        return result

class Decimal(FancyValidator):

    def _to_python(self, value, state):
        try:
            return decimal.Decimal(value)
        except decimal.DecimalException, e:
            raise Invalid(str(e), value, state)
        