"""plugin authentication retriever

:organization: Logilab
:copyright: 2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from __future__ import with_statement
import threading

def url_args(url):
    from urllib import unquote
    import urlparse
    args = urlparse.urlsplit(url)[3]
    args = dict((unquote(k), unquote(v))
                for k, v in (arg.split('=')
                             for arg in args.split('&')))
    return args
