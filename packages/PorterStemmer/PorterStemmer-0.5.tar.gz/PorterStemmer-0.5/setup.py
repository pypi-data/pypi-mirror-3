from distutils.core import setup, Extension

stemmermodule = Extension("porterstemmer",
        sources=["porterstemmer.c"])

setup(name = "PorterStemmer",
        version = "0.5",
        description = "Porter Stemmer for Python",
        author = "Naoki INADA",
        author_email = "inada-n@klab.jp",
        ext_modules = [stemmermodule],
        url = "http://bitbucket.org/methane/porterstemmer/",

        long_description = """\
Python module for Porter Stemmer
<http://tartarus.org/~martin/PorterStemmer/>

This is Python wrapped Porter's original C implementation.""",

        classifiers = [
            'Development Status :: 4 - Beta',
            'License :: Public Domain',
            'Topic :: Text Processing :: General',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 2',
            ]
    )
