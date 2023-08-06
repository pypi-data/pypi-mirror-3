from zope.pagetemplate.pagetemplate import PageTemplate

def patch(__ac_permissions__, permission, attributes):
    """Patch set __ac_permissions__.  __ac_permissions__ is the
    original __ac_permissions__, permission is the name of the
    permission to set attributes for, and attributes is a tuple
    of strings with names of attributes to set."""
    new__ac_permissions__ = ()
    for permission_, attributes_ in __ac_permissions__:
        if permission_ == permission:
            new__ac_permissions__ += ((permission_, attributes_ + attributes))
            break
    else:
        new__ac_permissions__ += ((permission, attributes))
    return new__ac_permissions__

def pt_filled_slots(self, template=None):
    """Returns names of slots filled."""
    template = template or self
    filled_slots = ()
    for item in template._v_program:
        if item[0] == 'useMacro':
            for entry in item[1][3]:
                if entry[0] == 'fillSlot':
                    filled_slots = filled_slots + (entry[1][0],)
    return filled_slots

PageTemplate.pt_filled_slots = pt_filled_slots
PageTemplate.__ac_permissions__ = patch((),
                                        'View', ('pt_filled_slots',))
