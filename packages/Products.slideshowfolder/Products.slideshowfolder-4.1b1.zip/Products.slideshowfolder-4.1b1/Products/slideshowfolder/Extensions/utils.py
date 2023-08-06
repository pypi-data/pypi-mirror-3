from Products.CMFCore.utils import getToolByName
from Products.slideshowfolder.browser import FolderSlideShowView


def restoreAllFolders(portal):
    """Walk the catalog and unmake all folders that appear to be slideshow folders"""
    count = 0
    catalog = getToolByName(portal, 'portal_catalog')
    for brain in catalog(portal_type="Folder"):
        folder = brain.getObject()
        view = FolderSlideShowView(folder, None)
        if view.isSlideshow():
            view.unmakeSlideshow()
            count += 1

    return "Reverted %s slideshow folders to normal folders" % count


def removeAction(id_to_delete, portal_actions):
    """Delete a single action from portal actions"""

    actions = portal_actions._cloneActions()
    for action in actions:
        if action.id == id_to_delete:
            actions.remove(action)
    portal_actions._actions=tuple(actions)
