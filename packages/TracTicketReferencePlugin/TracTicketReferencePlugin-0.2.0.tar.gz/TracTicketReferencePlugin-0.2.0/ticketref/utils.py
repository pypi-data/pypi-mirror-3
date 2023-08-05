# -*- coding: utf-8 -*-

import re

_RE_REFS_WITH_IDS = re.compile(r"""
    ^.*?(?P<ref_text>(ref.*?)\s+(\#\d+[,|\s]*){1,})
""", re.U | re.X)

def get_refs_in_comment(comment):
    """ pick out reference text and convert text to ids
    >>> get_refs_in_comment(u"refs. #1")
    set([1])
    >>> get_refs_in_comment(u"refs. #1ab")
    set([1])
    >>> get_refs_in_comment(u"refs. a#1b")
    set([])
    >>> get_refs_in_comment(u"some refer #1, #3, some")
    set([1, 3])
    >>> get_refs_in_comment(u"some refer #1,#3,#5 # 7 some")
    set([1, 3, 5])
    >>> get_refs_in_comment(u"ref #1,#3  ref, #5 #7 refs")
    set([1, 3])
    >>> get_refs_in_comment(u"ref #1,#3  ref #5, #7")
    set([1, 3])
    >>> get_refs_in_comment(u"refs#1")
    set([])
    >>> get_refs_in_comment(u"reference#1 #3, #5")
    set([1, 3, 5])
    """
    ref_ids = set([])
    match = re.match(_RE_REFS_WITH_IDS, comment)
    if match:
        ref_text = match.groupdict().get("ref_text")
        ref_ids = get_ref_ids_in_comment(ref_text)
    return ref_ids

_RE_TICKET_IDS = re.compile(r"(#\d+)", re.U)

def get_ref_ids_in_comment(text):
    """ return only id numbers with list
    >>> get_ref_ids_in_comment("")
    set([])
    >>> get_ref_ids_in_comment("#1")
    set([1])
    >>> get_ref_ids_in_comment("refs #1")
    set([1])
    >>> get_ref_ids_in_comment("refs #1, ")
    set([1])
    >>> get_ref_ids_in_comment("refs #1, #2")
    set([1, 2])
    >>> get_ref_ids_in_comment("refs #1,#2,   #3 ids")
    set([1, 2, 3])
    """
    ref_ids = re.findall(_RE_TICKET_IDS, text)
    return set([int(id_.replace("#", "")) for id_ in ref_ids])

def cnv_text2list(refs_text):
    """ convert text to list
    >>> cnv_text2list("")
    set([])
    >>> cnv_text2list(", ")
    set([])
    >>> cnv_text2list("1")
    set([1])
    >>> cnv_text2list("1, 3")
    set([1, 3])
    >>> cnv_text2list("  1,3,   5")
    set([1, 3, 5])
    >>> cnv_text2list(",  1,3,")
    set([1, 3])
    """
    refs = set([])
    if refs_text:
        refs_text = refs_text.strip(" ,")
    if refs_text:
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

def cnv_sorted_refs(orig_text, extra_refs):
    """
    >>> cnv_sorted_refs(u"", set([]))
    u''
    >>> cnv_sorted_refs(u"1", set([]))
    u'1'
    >>> cnv_sorted_refs(u"", set([3, 1]))
    u'1, 3'
    >>> cnv_sorted_refs(u"1, 5", set([3, 1]))
    u'1, 3, 5'
    >>> cnv_sorted_refs(u"2, 1, 5", set([3, 1, 2]))
    u'1, 2, 3, 5'
    """
    refs = cnv_text2list(orig_text)
    refs.update(extra_refs)
    return cnv_list2text(refs)
