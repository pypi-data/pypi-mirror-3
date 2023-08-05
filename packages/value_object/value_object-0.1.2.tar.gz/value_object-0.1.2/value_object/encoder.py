# --* encoding: utf-8 *--

from .helper import get_attributes
from .value_object import ValueObject
from json.encoder import JSONEncoder


class Encoder(JSONEncoder):
    '''
    JSON encoder of ValueObject.
    Give this object to json.dumps 'cls' arg like below.

        json.dumps(value_object, cls=encoder)

    This encoder converts ValueObject for {attribute_name: attribute_value}.
    '''

    def default(self, o):
        '''Overrides json.JSONEncoder.default() to not rise TypeError.'''
        names = get_attributes(o)
        result = {}
        for name in names:
            attr = getattr(o, name)
            if isinstance(attr, ValueObject):
                return self.default(attr)
            else:
                result[name] = attr
        return result
