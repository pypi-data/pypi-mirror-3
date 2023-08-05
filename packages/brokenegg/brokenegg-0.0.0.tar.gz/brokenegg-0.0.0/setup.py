from setuptools import setup, find_packages

version = '0.0.0'

long_description = """
brokenegg
=========

Sometimes when you are testing Python tooling you need an egg with
a syntax error. Well I did. So here is one.
"""

setup(
    name = 'brokenegg',
    version = version,
    description = "Ann egg with SyntaxErrors",
    long_description = long_description,
    author = "John Carr",
    author_email = "john.carr@isotoma.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    zip_safe = False,
    )

