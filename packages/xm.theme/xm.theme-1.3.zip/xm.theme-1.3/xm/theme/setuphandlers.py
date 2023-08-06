from zope.app.container.interfaces import INameChooser
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.app.portlets import portlets as plone_portlets
from Products.eXtremeManagement.portlets import project, portlet_tasks

# BBB configure_portlets can be removed completely after we drop 3.0 support


def UNUSED_configure_portlets(site, logger):
    """Set up the portlets.

    This is here for backward compatibility with Plone 3.0.
    As of Plone 3.1 Portlet Assignments are being managed by portlets.xml.

    """

    # Get some definitions.
    column = getUtility(IPortletManager, name="plone.leftcolumn", context=site)
    manager = getMultiAdapter((site, column), IPortletAssignmentMapping)
    chooser = INameChooser(manager)

    # First we'll remove everythin to get started with a clean slate.
    for key in manager.keys():
        del manager[key]
        logger.info('Removed portlet "%s" from the left column' % key)
    # Then we can add the portlets we actually need.
    assignments = [
        plone_portlets.login.Assignment(),
        project.Assignment(),
        plone_portlets.classic.Assignment('portlet_poi', 'portlet'),
        portlet_tasks.Assignment(),
# #        plone_portlets.classic.Assignment('portlet_tasks', 'portlet'),
        plone_portlets.classic.Assignment('portlet_stories', 'portlet'),
        ]
    for assignment in assignments:
        title = assignment.title
        if title not in [item.title for item in manager.values()]:
            manager[chooser.chooseName(title, assignment)] = assignment
            logger.info('Added portlet "%s" to left column.', title)

    # We do not need portlets on the right at all.
    column = getUtility(IPortletManager, name="plone.rightcolumn",
                        context=site)
    manager = getMultiAdapter((site, column), IPortletAssignmentMapping)
    for key in manager.keys():
        del manager[key]
        logger.info('Removed portlet "%s" from the right column' % key)


def setup_various(context):
    """Perform various setup steps."""
    if context.readDataFile('xm.theme_various.txt') is None:
        return
    logger = context.getLogger('xm.theme')
    site = context.getSite()
#    configure_portlets(site, logger)
