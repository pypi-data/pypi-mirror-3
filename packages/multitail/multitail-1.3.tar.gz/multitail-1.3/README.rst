Python generator which implements `tail -f`-like behavior, with support for tailing multiple files.
====================================================================================================

Usage
-----

::

    from multitail import multitail
    for fn, line in multitail('/var/log1', '/var/log2', '/var/log3'):
        print '%s: %s' % (fn, line)
        

