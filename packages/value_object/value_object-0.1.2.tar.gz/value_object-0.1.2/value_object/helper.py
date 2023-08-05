# --* encoding: utf-8 *--

import types


def get_attributes(o):
    '''Get attributes of argument ofject except privates, functions.'''
    is_private = lambda x: x.startswith('__')
    is_method = lambda x: type(getattr(o, x)) == types.MethodType
    return filter(lambda x: not is_private(x) and not is_method(x),
                  dir(o))
