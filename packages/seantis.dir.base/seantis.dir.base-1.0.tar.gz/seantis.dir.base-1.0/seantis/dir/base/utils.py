import collections
from os import path

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder
from Products.CMFCore.utils import getToolByName
from zope import i18n

import pyuca

allkeys = path.join('/'.join(path.split(pyuca.__file__)[:-1]), 'allkeys.txt')
collator = pyuca.Collator(allkeys)

print 'loaded collator'

def flatten(l):
    """Generator for flattening irregularly nested lists. 'Borrowed' from here:
    http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python

    """
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def get_interface_fields(interface):
    """ Retrieve the field values from a schema interface. Returns a dictionary
    with the keys being the field names and the values being the fields.

    """
    return dict(getFieldsInOrder(interface))

def anonymousHasRight(folder, right='View'):
    """
    For a given Plone folder, determine whether Anonymous has the right
    given by parameter 'right' (String). This recurses to parents if
    'Acquire' is checked.
    Returns 1 if Anonymous has the right, 0 otherwise.

    via http://plone.org/documentation/kb/show-context-dependent-folder-icons-in-navigation-portlet
    """
    ps = folder.permission_settings()
    for p in ps:
        if (p['name'] == right):
            acquired = not not p['acquire']
            break
    if acquired:
        # recurse upwardly:
        parent = folder.aq_parent
        return anonymousHasRight(parent, right)
    else:
        for p in folder.rolesOfPermission(right):
            if p['name'] == "Anonymous":
                selected = not not p['selected']
                return selected

def get_current_language(context, request):
    """Returns the current language"""
    context = aq_inner(context)
    portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
    return portal_state.language()

def is_izug_portal(obj):
    """Returns true if the dictionary is running on the izug portal. 
    This function should not exist and will be removed as soon as possible.

    """
    skins = getToolByName(obj, 'portal_skins')
    return 'iZug' in skins.getDefaultSkin()

def add_count(text, count):
    """Adds a count to a text."""
    return '%s (%i)' % (text, count)

def remove_count(text):
    """Removes the count from with_count from a text."""
    pos = text.rfind(' (')
    if pos == -1:
        return text
    else:
        return text[:pos]

def translate(context, request, text):
    lang = get_current_language(context, request)
    return i18n.translate(text, target_language=lang)

def unicode_collate_sortkey():
    """ Returns a sort function to sanely sort unicode values.
    
    A more exact solution would be to use pyUCA but that relies on an external
    C Library and is more complicated

    See:
    http://stackoverflow.com/questions/1097908/how-do-i-sort-unicode-strings-alphabetically-in-python
    http://en.wikipedia.org/wiki/ISO_14651
    http://unicode.org/reports/tr10/
    http://pypi.python.org/pypi/PyICU
    http://jtauber.com/blog/2006/01/27/python_unicode_collation_algorithm/
    https://github.com/href/Python-Unicode-Collation-Algorithm

    """

    return collator.sort_key
