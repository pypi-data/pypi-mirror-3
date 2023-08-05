from setuptools import setup

name = 'value_object'
version = '0.1.3'
short_description = 'Tiny implementation of Value Object of Eric Evans DDD'
long_description = '''
A tiny python implementation of 'Value Object' of Eric Evans DDD.
This provides ValueObject class and it's JSON encoder.
For more details of DDD, see the website(http://domaindrivendesign.org/).

Current version is development and unstable.
I have to write, and test more, means you should not use this for your production codes.
'''

classifiers = [
   'Development Status :: 2 - Pre-Alpha',
   'License :: OSI Approved :: BSD License',
   'Programming Language :: Python',
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['value object', 'ddd', 'domain driven design'],
    packages=('value_object',),
    license='BSD',
    platforms='any',
    author='mikamix',
    author_email='tmp@mikamix.net',
    url='http://blog.mikamix.net',
)
