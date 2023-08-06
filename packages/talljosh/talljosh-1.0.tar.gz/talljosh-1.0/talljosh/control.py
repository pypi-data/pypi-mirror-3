import inspect

def entry_point(fn, stack_levels=1):
    '''
    Defines the given function to be run only if this module is being executed,
    not if the module is being imported.

    @param stack_levels: the number of stack levels to ascend to find the
            __name__ variable.

    @returns: the original function, so that entry_point is safe for use as a
            decorator.
    '''

    parent_frame = inspect.currentframe()
    for i in xrange(stack_levels):
        parent_frame = parent_frame.f_back

    name = parent_frame.f_locals.get('__name__')
    if name == '__main__':
        fn()
    return fn

