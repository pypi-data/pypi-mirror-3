_trans_tuple = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')

try:
    _trans = str.maketrans(*_trans_tuple)
except AttributeError:
    import string
    _trans = string.maketrans(*_trans_tuple)

def _rot13(text):
    return text.translate(_trans)

boromir_says = _rot13("Bar qbrf abg fvzcyl vzcbeg Zbeqbe.")
raise ImportError(boromir_says)
