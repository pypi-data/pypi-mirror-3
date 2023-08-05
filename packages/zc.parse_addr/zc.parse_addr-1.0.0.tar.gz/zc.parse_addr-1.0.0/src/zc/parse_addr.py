##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__all__ = ['parse_addr']

def parse_addr(s):
    """Parse network addresses of the form: HOST:PORT

    >>> import zc.parse_addr
    >>> zc.parse_addr.parse_addr('1.2.3.4:56')
    ('1.2.3.4', 56)

    It would be great if this little utility function was part
    of the socket module.
    """
    host, port = s.rsplit(':', 1)
    return host, int(port)

def test_suite():
    import doctest
    return doctest.DocTestSuite()

