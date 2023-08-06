# -*- coding: utf-8 -*-
#
# Copyright John Reid 2011
#

"""
Gets svn revision. Based on code from Django.
"""

import stempy, re

def get_svn_revision(path=None):
    """
    Returns the SVN revision in the form svnXXXX,
    where XXXX is the revision number.

    Returns svnUnknown if anything goes wrong, such as an unexpected
    format of internal SVN files.

    If path is provided, it should be a directory whose SVN info you want to
    inspect. If it's not provided, this will use the root stempy/ package
    directory.
    """
    rev = None
    if path is None:
        path = stempy.__path__[0]
    entries_path = '%s/.svn/entries' % path

    try:
        entries = open(entries_path, 'r').read()
    except IOError:
        pass
    else:
        # Versions >= 7 of the entries file are flat text.  The first line is
        # the version number. The next set of digits after 'dir' is the revision.
        if re.match('(\d+)', entries):
            rev_match = re.search('\d+\s+dir\s+(\d+)', entries)
            if rev_match:
                rev = rev_match.groups()[0]
        # Older XML versions of the file specify revision as an attribute of
        # the first entries node.
        else:
            from xml.dom import minidom
            dom = minidom.parse(entries_path)
            rev = dom.getElementsByTagName('entry')[0].getAttribute('revision')

    if rev:
        return u'svn%s' % rev
    return u'svnUnknown'