# -*- coding: utf-8 -*-

def cnv_text2list(refs_text):
    """ convert text to list
    >>> cnv_text2list("")
    set([])
    >>> cnv_text2list("1")
    set([1])
    >>> cnv_text2list("1, 3")
    set([1, 3])
    >>> cnv_text2list("  1,3,   5")
    set([1, 3, 5])
    """
    refs = set([])
    if refs_text and refs_text.strip():
        refs = set([int(id_.strip()) for id_ in refs_text.split(",")])
    return refs

def cnv_list2text(refs):
    """ convert list to text
    >>> cnv_list2text(set([]))
    u''
    >>> cnv_list2text(set([1]))
    u'1'
    >>> cnv_list2text(set([3, 1]))
    u'1, 3'
    """
    return u", ".join(str(i) for i in sorted(refs))
