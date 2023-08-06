from Acquisition import Explicit

from kss.core import KSSView
from kss.core import kssaction
from plone.memoize.view import memoize
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MyProjectList(Explicit):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    def update(self):
        pass

    render = ViewPageTemplateFile('templates/my_projects.pt')

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    @memoize
    def my_projects(self):
        pview = getMultiAdapter((self.context, self.request),
                                name=u'myprojects')
        pbrains = pview.projectlist
        projects = []
        for pbrain in pbrains:
            projects.append(dict(title = pbrain.Title,
                                 url = pbrain.getURL,
                                 description = pbrain.Description))
        projects.sort(cmp=lambda x,y: cmp(x['title'].lower(), y['title'].lower()))
        return projects

    @memoize
    def has_projects(self):
        if len(self.my_projects()) >= 1:
            return True
        return False

    @memoize
    def has_single_project(self):
        if len(self.my_projects()) == 1:
            return True
        return False


class KSSProjectsList(KSSView):

    @kssaction
    def xm_insert_projects_list(self):
        """Insert the list of projects for the user."""
        core = self.getCommandSet('core')
        zope = self.getCommandSet('zope')
        selector = core.getHtmlIdSelector('my-projects')
        zope.refreshProvider(selector, 'xm.my_project_list')
