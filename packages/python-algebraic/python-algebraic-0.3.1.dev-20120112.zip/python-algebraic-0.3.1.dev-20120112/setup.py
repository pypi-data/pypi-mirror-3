from setuptools import setup, find_packages

setup (
    name         = 'python-algebraic',
    version      = '0.3.1',
    description  = 'Algebraic modeling system for Python',
    author       = "Ryan J. O'Neil",
    author_email = 'ryanjoneil@gmail.com',
    url          = 'https://github.com/rzoz/python-algebraic',

    package_dir = {'': 'src'},
    packages    = find_packages('src', exclude=['tests', 'tests.*']),
    zip_safe    = True,
    test_suite  = 'tests',

    keywords    = 'algebraic modeling model modeler',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics'
    ]
)
