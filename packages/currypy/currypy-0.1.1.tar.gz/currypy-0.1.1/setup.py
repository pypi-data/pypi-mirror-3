from setuptools import setup, find_packages

setup(
    name='currypy',
    version='0.1.1',
    packages=find_packages(
        'src',exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_dir={'':'src'},
    test_suite="test",

    # metadata for upload to PyPI
    author = "michael j pan",
    author_email = "mikepan@gmail.com",
    description = "pickleable partial functions",
    license = "New BSD",
    keywords = "functools partial curry pickle",
    url = "http://code.google.com/p/currypy/",
    long_description = "functools.partial allows for the currying of arguments. However, being implemented in C, functools.partial objects are not pickleable. This package implements a wrapper class for the partial objects, such that enables pickling of the objects.",
    platforms = ["All"]

)
