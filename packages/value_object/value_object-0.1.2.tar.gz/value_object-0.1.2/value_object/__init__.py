'''
    ValueObject
    ~~~~~~~~~~~

    A tiny python implementation of 'Value Object' of Eric Evans DDD.
    This provides ValueObject class and it's JSON encoder.

    For more details of DDD, see the website(http://domaindrivendesign.org/).

    Current version is development and unstable.
    I have to write, and test more, means you should not use this
    for your production codes.

    Give me mail if you find bugs or better solutions, thanks.

    :author: mikamix
    :email: tmp@mikamix.net
'''

__version__ = '0.1.2'

from .value_object import ValueObject
from .encoder import Encoder
