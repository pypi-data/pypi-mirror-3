This product adds a pt_filled_slots methods to page templates, so it
is possible from within or before a filled slot see which slots are
filled by the calling page template.

For example "python:'content-core' in template.pt_filled_slots" could
be called to see if content-core is defined.

After discovering some security-related issues with this approach
(access denied) I've also added the option of setting up the method as
an External Method:

 ID: pt_filled_slots
 Module name: Products.PageTemplateFilledSlots.pt_filled_slots
 Function name: pt_filled_slots

And this is called via for example "python:'content-core' in
context.pt_filled_slots(template)" in a page template.
