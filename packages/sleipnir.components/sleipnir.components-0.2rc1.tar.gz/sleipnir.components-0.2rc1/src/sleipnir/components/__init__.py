
"""
Sleipnir Component Subsystem. STRONGLY based on the one implemented by
TRAC project
"""


def __import(mod, names=None):
    """
    Names are imported from mod immediately, and then added to the
    global scope.  (It is equivalent to 'from mod import <names>')
    """
    # No lazy importing, import everything immediately.
    omod = __import__(mod, globals(), fromlist=names)
    if names:
        # from mod import <names>
        for name in names:
            globals()[name] = getattr(omod, name)
    else:
        # import mod
        globals()[mod] = omod

# Import Modules
__import('exceptions', ['CoreError', ])
__import('components', ['Component', 'implements', ])
__import('entrypoint', ['Interface', 'ExtensionPoint', ])
