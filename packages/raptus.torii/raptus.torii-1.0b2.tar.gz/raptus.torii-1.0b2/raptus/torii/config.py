import sys,os
import utilities
from raptus.torii.python import Python

utilities = dict(sdir=utilities.sdir, ls=utilities.ls)
""" utilities are a set of helper functions. They will appear as globals
    in your python prompt. The globals can be extended with additional
    packages. To extend take a look in raptus.torii.plone.
"""
properties = dict()
""" properties are a set of helper attributes. Similar to the utilities, but
    properties are called by each connection. The call of the function performed
    in the context of the connection. This means you can use local attributes
    in your function, like app, arguments ... Only the return value is stored 
    in the globals. To extend take a look in raptus.torii.plone.
"""

scripts = dict(pack= '%s/scripts/pack.py' % os.path.dirname(__file__))
""" scripts can be run directly without the python prompt over torii. It's
    easy to customize you own scripts. Again please take a look
    at raptus.torii.plone
"""

interpreter = Python
""" The standard python interpreter. To create you own interpreter subclass
    interpreter.AbstractInterpreter and override all methods. Take a look at
    raptus.torii.python and raptus.torii.ipython.ipython
"""

tab_replacement = '    '

