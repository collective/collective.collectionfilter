from Products.CMFPlone.utils import safe_unicode


def safe_encode(val):
    """Safely encode a value to utf-8.
    """
    return safe_unicode(val).encode('utf-8')
