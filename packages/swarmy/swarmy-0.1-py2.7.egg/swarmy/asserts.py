
def assert_lists_eq(l1, l2, strict=True):
    if strict:
        assert type(l1) == list, 'Expected a list for arg 0, got %s.' % str(type(l1))
        assert type(l2) == list, 'Expected a list for arg 1, got %s.' % str(type(l2))
    assert len(l1) == len(l2), 'Expected %d elements, Got %d elements' % (len(l2), len(l1))
    for i, element in enumerate(l1):
        assert element == l2[i], 'At index %d, Expected \'%s\', Got \'%s\'' % (i, l2[i], element)

def assert_dicts_eq(d1,d2):
    assert type(d1) == dict, 'First argument is not a dict()'
    assert type(d2) == dict, 'Second argument is not a dict()'
    assert len(d1.keys()) == len(d2.keys()),\
            'Got %d keys. Expected %d keys.' % (len(d1.keys()), len(d2.keys()))
    for k,v in d1.iteritems():
        assert k in d2, 'Got unexpected key %s' % k
        assert d1[k] == d2[k], "'%s' != '%s'" % (d1[k], d2[k])

