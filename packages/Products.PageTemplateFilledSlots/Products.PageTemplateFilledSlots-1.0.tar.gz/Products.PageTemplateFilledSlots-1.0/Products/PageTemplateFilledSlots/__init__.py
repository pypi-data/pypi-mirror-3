from zope.pagetemplate.pagetemplate import PageTemplate

def pt_filled_slots(self):
    """Returns names of slots filled."""
    filled_slots = ()
    for item in self._v_program:
        if item[0] == 'useMacro':
            for entry in item[1][3]:
                if entry[0] == 'fillSlot':
                    filled_slots = filled_slots + (entry[1][0],)
    return filled_slots

PageTemplate.pt_filled_slots = pt_filled_slots
