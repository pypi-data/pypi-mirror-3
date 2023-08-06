# -*- coding: utf-8 -*-
'''appspace utilities'''

from keyword import iskeyword

from importlib import import_module

from stuf.six import strings

__all__ = ('checkname', 'lazyimport')


def lazyimport(path, attribute=None):
    '''
    deferred module loader

    @param path: something to load
    @param attribute: attribute on loaded module to return
    '''
    if isinstance(path, strings):
        try:
            dot = path.rindex('.')
            # import module
            path = getattr(import_module(path[:dot]), path[dot + 1:])
        # If nothing but module name, import the module
        except (AttributeError, ValueError):
            path = import_module(path)
        if attribute:
            path = getattr(path, attribute)
    return path


class CheckName(object):

    '''ensures string is legal Python name'''

    # Illegal characters for Python names
    ic = '()[]{}@,:`=;+*/%&|^><\'"#\\$?!~'

    def __call__(self, name):
        '''
        ensures string is legal python name

        @param name: name to check
        '''
        # Remove characters that are illegal in a Python name
        name = name.strip().lower().replace('-', '_').replace(
            '.', '_'
        ).replace(' ', '_')
        name = ''.join(i for i in name if i not in self.ic)
        # Add _ if value is a Python keyword
        return name + '_' if iskeyword(name) else name


checkname = CheckName()
