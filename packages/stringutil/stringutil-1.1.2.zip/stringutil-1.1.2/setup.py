from distutils.core import setup

setup(
    name       = 'stringutil',
    version    = '1.1.2',
    py_modules = ['stringutil'],
    author     = 'sidedoor',
    author_email = 'johnfraboni@gmail.com',
    url          = 'http://www.johnfraboni.com',
    description  = 'A collection of basic string utility methods, mostly created for learning python: ' +
                      'Fixes in 1.1.1: 1. Adding recursive setting of indentation boolean.' +
                      'Fixes in 1.1.2: 1. Adding four arg to allow printing to different outputs',
    )
