'''The modul 'fkr' (function-keyword-replacer) offers the function
newkey. Which allows you to create functions out of functions with
new fixed keywords.'''


def newkey(function, **a):
    '''newkey expects a function and defind keywordsarguments
    (like end = '\n\n'). It returns a new function with replaced
    with the new defined kewords.'''
    def new_function(*b):
        return function(*b,**a )
    return new_function
