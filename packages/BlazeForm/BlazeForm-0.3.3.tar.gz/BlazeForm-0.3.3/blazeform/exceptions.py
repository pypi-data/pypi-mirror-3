
class ProgrammingError(Exception):
    """ used to signify an error on the part of the developer if the
        BlazeForm API is used incorrectly.
    """

class ElementInvalid(Exception):
    """ raised when .value is accessed on an element but the element is not valid """
    def __init__(self, label):
        desc = '"value" attribute accessed, but element "%s" is invalid' % label
        Exception.__init__(self, desc)

class ValueInvalid(Exception):
    """ raised inside callables that have been added to a form or element as
        a validator or processor respectively to signify an invalid condition.
        
        The description will be used as the error message.
    """
    def __init__(self, desc=''):
        Exception.__init__(self, desc)