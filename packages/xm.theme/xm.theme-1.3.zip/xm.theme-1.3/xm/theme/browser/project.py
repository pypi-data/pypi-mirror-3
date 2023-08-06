from Acquisition import Explicit
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from zope.component import adapts
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from xm.theme.browser.interfaces import IProjectContentView
from xm.theme.browser.interfaces import IProjectContentProvider


class ProjectContentView(BrowserView):
    """Return information about the contents of a project."""
    implements(IProjectContentView)

    @memoize
    def requested_type(self):
        """Return the requested portal type."""
        return self.request.form.get('type', None)

    @memoize
    def requested_state(self):
        """Return the requested state."""
        return self.request.form.get('state', None)

    def title(self):
        """Return the title for the page."""
        context = aq_inner(self.context)
        portal_type = self.requested_type()
        type_map = {'iteration': u'Iterations',
                    'offer': u'Offers',
                    'tracker': u'Issue trackers',
                    'other': u'Attachments',
                    }
        title = context.Title()
        if portal_type:
            type_title = type_map.get(portal_type)
            if type_title:
                title += ': %s' % type_title
        return title


class ProjectContentProvider(Explicit):
    """View to show specific items contained in a project."""
    implements(IContentProvider, IProjectContentProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    portal_type = None
    state = None

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.project_view = aq_inner(context).restrictedTraverse('@@project')

    def update(self):
        pass

    render = ViewPageTemplateFile('templates/project_content.pt')

    def _get_iteration(self):
        """Return the iterations.
        Optionally take the state into account, when requested.
        """
        state_map = {'open': ('new', ),
                     'closed': ('completed', 'invoiced', 'own-account'),
                     'current': ('in-progress', ),
                     }
        states = state_map.get(self.state, None)
        return self.project_view.getIterations(states)

    def _get_offer(self):
        """Return the offers."""
        return self.project_view.offers()

    def _get_tracker(self):
        """Return the issue trackers."""
        context = aq_inner(self.context)
        cfilter = dict(portal_type='PoiTracker')
        brains = context.getFolderContents(cfilter)
        tracker_list = []
        for brain in brains:
            tracker_list.append(dict(title = brain.Title,
                                     url = brain.getURL(),
                                     ))
        return tracker_list

    def _get_other(self):
        """Return all other content of a project,
        not being iterations, offers or trackers.
        """
        # First gather which content types should be treated differently.
        portal_props = getToolByName(self, 'portal_properties')
        site_props = portal_props['site_properties']
        view_types = site_props.typesUseViewActionInListings

        # Gather the content
        context = aq_inner(self.context)
        cfilter = {'portal_type': ('File', 'Image', 'Story', 'Document')}
        brains = context.getFolderContents(cfilter)

        # Build the result set
        result_list = []
        for brain in brains:
            url = brain.getURL()
            if brain.portal_type in view_types:
                        url += '/view'
            result_list.append(dict(title = brain.Title,
                                    url = url,
                                    ))
        return result_list

    @memoize
    def items(self):
        """Return the items to be shown."""
        method = '_get_%s' % str(self.portal_type).lower()
        if method in dir(self):
            return self.__getattribute__(method)()
        else:
            return []
