# --* encoding: utf-8 *--

import types

invalid_types = [
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.ClassType,
    types.CodeType,
    types.DictProxyType,
    types.EllipsisType,
    types.FileType,
    types.FrameType,
    types.FunctionType,
    types.GetSetDescriptorType,
    types.LambdaType,
    types.MemberDescriptorType,
    types.MethodType,
    types.ModuleType,
    types.NotImplementedType,
    types.TracebackType,
    types.TypeType,
    types.UnboundMethodType,
]


def get_attr_names(o):
    '''Get attribute names of argument ofject except privates, functions.'''
    is_builtin = lambda x: x.startswith('__')
    is_invalid = lambda x: type(getattr(o, x)) in invalid_types
    return filter(lambda x: not is_builtin(x) and not is_invalid(x),
                  dir(o))
