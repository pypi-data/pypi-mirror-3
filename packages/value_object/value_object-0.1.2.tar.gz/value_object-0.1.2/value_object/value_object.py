# --* encoding: utf-8 *--

from .helper import get_attributes


class ValueObject(object):
    '''
    Overrides '==', '!=', and '__hash__' methods.
    Instance which has same attribute value returns True for '=='.
    A Hashcode of this object depends on it's atrtribute value.
    '''

    def __eq__(self, other):
        '''Return True if other is same class and has same attribute value.'''
        if not isinstance(other, getattr(self, '__class__')):
            return False
        for name in get_attributes(self):
            self_attr = getattr(self, name)
            other_attr = getattr(other, name)
            if isinstance(self_attr, (list, tuple)):
                for a in self_attr:
                    if a not in other_attr:
                        return False
            else:
                if self_attr != other_attr:
                    return False
        return True

    def __ne__(self, other):
        '''Return oposit value of __eq__.'''
        return not self == other

    def __hash__(self):
        '''
        Return value is depend on it's attribute value.
        This method calculates it's attributets hashcode recursively.
        '''
        return reduce(lambda p, c: p * self.__hash(c),
                      [getattr(self, name) for name in get_attributes(self)],
                      1)

    def __hash(self, o):
        if isinstance(o, (list, tuple)):
            return self.__hash_itr(o)
        elif isinstance(o, dict):
            return self.__hash_dic(o)
        else:
            return hash(o)

    def __hash_itr(self, itr):
        return reduce(lambda p, c: p * self.__hash(c),
                      itr,
                      1)

    def __hash_dic(self, dic):
        return reduce(lambda p, c: p * self.__hash(c),
                      dic.values(),
                      1)
