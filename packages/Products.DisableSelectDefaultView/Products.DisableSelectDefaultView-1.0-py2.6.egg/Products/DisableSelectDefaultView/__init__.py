from plone.app.contentmenu.menu import DisplaySubMenuItem
from zope.component import getMultiAdapter

old_disabled = DisplaySubMenuItem.disabled

def disabled(self):
    try:
        context = self.context
        portal_state = getMultiAdapter((context, context.REQUEST), name=u'plone_portal_state')
        if portal_state.member().has_role('Manager'):
            # Set to False if Manager should be able to
            # modify the default view
            return True
        return True
    except:
        return True

DisplaySubMenuItem.disabled = disabled
