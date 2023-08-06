from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

try:
    # Plone 4
    from plone.app.layout.viewlets.common import ContentViewsViewlet
except ImportError:
    # Plone 3 only had a template here, not a class
    ContentViewsViewlet = ViewletBase
from zope.component import getMultiAdapter
from kss.core import KSSView, kssaction


class XMProjectHeaderViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/project_header.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        self.site_url = portal_state.portal_url()
        self.site_title = portal_state.portal_title()
        self.project_title = self._get_project_title()
        self.project_url = self._get_project_url()

    def _get_project(self):
        try:
            project = self.context.getProject()
        except AttributeError:
            project = None
        return project

    def _get_project_title(self):
        project = self._get_project()
        if project is not None and project.title != '':
            return project.title
        else:
            return self.site_title

    def _get_project_url(self):
        project = self._get_project()
        if project is not None:
            return project.absolute_url()
        else:
            return self.site_url


class XMSearchBoxViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/searchbox.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        tools = getMultiAdapter((self.context, self.request),
                                        name=u'plone_tools')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_url = portal_state.portal_url()
        self.anonymous = portal_state.anonymous()
        self.checkPermission = tools.membership().checkPermission
        props = tools.properties()
        livesearch = props.site_properties.getProperty('enable_livesearch',
                                                       False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = ""

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class XMMyProjectsViewlet(ViewletBase):

    def update(self):
        pass


class GoogleSearchViewlet(ViewletBase):

        render = ViewPageTemplateFile('templates/googlesearch.pt')


class XMPersonalBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/personal_bar.pt')

    def update(self):
        super(XMPersonalBarViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
        self.user_actions = context_state.actions().get('user', None)
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.anonymous = self.portal_state.anonymous()


class KSSFullname(KSSView):
    # We have to use a page template to make sure CacheFu adds the headers

    @kssaction
    def xm_fullname(self):
        """ replace span with username"""

        mtool = getToolByName(self.context, "portal_membership")
        anonymous = mtool.isAnonymousUser()
        if not anonymous:
            userid = mtool.getAuthenticatedMember().getId()
            member_info = mtool.getMemberInfo(userid)
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                plone_utils = getToolByName(self.context, 'plone_utils')
                charset = plone_utils.getSiteEncoding()
                fullname = fullname.decode(charset)
                user_name = fullname
            else:
                user_name = userid

            self.getCommandSet('core').replaceInnerHTML('.userName', user_name)


class XMContentViewsViewlet(ContentViewsViewlet):
    index = ViewPageTemplateFile('templates/contentviews.pt')
