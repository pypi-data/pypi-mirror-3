import logging
from Products.Archetypes.utils import shasattr

log = logging.getLogger('slc.autocategorize/events.py')

def autocategorize(obj, event):
    """ Event handler registered for object adding
    """
    folders = []
    ancestor = parent = obj.aq_parent

    while ancestor.meta_type != 'Plone Site':
        if not shasattr(ancestor, 'Schema'):
            # TODO: We cannot yet deal with Dexterity content types
            ancestor = ancestor.aq_parent
            continue

        categorize_field = ancestor.Schema().get('autoCategorizeNewContent')
        categorize = categorize_field and categorize_field.get(ancestor)
        if not categorize:
            ancestor = ancestor.aq_parent
            continue

        if ancestor == parent:
            folders.append(ancestor)
        else:
            recurse_field = ancestor.Schema().get('recursiveAutoCategorization')
            recurse = recurse_field and recurse_field.get(ancestor)
            if recurse:
                folders.append(ancestor)

        ancestor = ancestor.aq_parent

    if not folders:
        return

    ocats = list(obj.Subject())
    for parent in folders:
        pcats = parent.Subject()
        if pcats:
            ocats = ocats + [c for c in pcats if c not in ocats]

    obj.setSubject(ocats)
    log.info('Object %s have been autocategorized with %s' \
                                    % (obj.Title(), str(ocats)))


