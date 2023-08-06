
def evaluate(fn):
    '''
    Evaluates the function immediately and returns the result. Useful for not
    filling up namespaces with junk.
    '''
    return fn()
