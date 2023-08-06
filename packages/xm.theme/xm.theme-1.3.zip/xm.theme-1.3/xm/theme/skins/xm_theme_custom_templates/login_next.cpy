## Controller Python Script "login_next"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Login next actions
##

from Products.CMFPlone import PloneMessageFactory as PMF
from xm.theme import xmMessageFactory as _
from DateTime import DateTime
import ZTUtils

REQUEST = context.REQUEST

util = context.plone_utils
membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    util.addPortalMessage(PMF(u'Login failed'), 'error')
    return state.set(status='failure')

util.addPortalMessage(PMF(u'Welcome! You are now logged in.'))

came_from = REQUEST.get('came_from', None)

# if we weren't called from something that set 'came_from' or if HTTP_REFERER
# is the 'logged_out' page, return the default 'login_success' form
if came_from is not None:
    scheme, location, path, parameters, query, fragment = util.urlparse(came_from)
    template_id = path.split('/')[-1]
    if template_id in ['login', 'login_success', 'login_password', 'login_failed',
                       'login_form', 'logged_in', 'logged_out', 'registered',
                       'mail_password', 'mail_password_form', 'join_form',
                       'require_login', 'member_search_results',
                       # We need localhost in the list, or Five.testbrowser tests
                       # won't be able to log in via login_form (since r17128).
                       'localhost']:
        came_from = ''
    # It is probably a good idea in general to filter out urls outside the portal.
    # An added bonus: this fixes some problems with a Zope bug that doesn't
    # properly unmangle the VirtualHostMonster stuff when setting ACTUAL_URL
    if not context.portal_url.isURLInPortal(came_from):
        came_from = ''
    if came_from == context.portal_url.getPortalObject().absolute_url():
        came_from = None

if came_from:
    # If javascript is not enabled, it is possible that cookies are not enabled.
    # If cookies aren't enabled, the redirect will log the user out, and confusion
    # may arise.  Redirect only if we know for sure that cookies are enabled.

    came_from = util.urlunparse((scheme, location, path, parameters, query, fragment))

    # redirect immediately
    return REQUEST.RESPONSE.redirect(came_from)


# Get all projects, sorted on modification date.
catalog = context.portal_catalog
projectbrains = catalog.searchResults(portal_type='Project',
                                      sort_on='modified',
                                      sort_order='reverse')

if len(projectbrains) == 1:
    # If there is only 1 project -> redirect directly
    return REQUEST.RESPONSE.redirect(projectbrains[0].getURL())
elif len(projectbrains) > 1:
    # If there is a cookie with a last project, use that project.
    cookies = REQUEST.cookies
    if 'last_project' in cookies:
        for projectbrain in projectbrains:
            if projectbrain.id == cookies['last_project']:
                util.addPortalMessage(_(u'You have been redirected to the '
                                        u'last project you visited.'))
                return REQUEST.RESPONSE.redirect(projectbrain.getURL())

    # Now we'll have smart...
    # For customers: show the most recent project.
    member = membership_tool.getAuthenticatedMember()
    memberid = member.id
    projectbrain = projectbrains[0]
    roles =  member.getRolesInContext(projectbrain.getObject())
    next_url = None
    if 'Customer' in roles:
        next_url = projectbrains[0].getURL()
    else:
        # For others: pick the most recent project with tasks assigned to
        # the user.
        for projectbrain in projectbrains:
            searchpath = projectbrain.getPath()
            taskbrains = catalog.searchResults(portal_type=['Task',
                                                            'PoiTask'],
                                               getAssignees=memberid,
                                               review_state=('open', 'to-do'),
                                               path=searchpath)
            if len(taskbrains) > 0:
                next_url = projectbrain.getURL()
                break
    if not next_url:
        next_url = context.portal_url.getPortalObject().absolute_url()
    util.addPortalMessage(_(u'You have been redirected to your '
                            u'most recent project.'))
else:
    next_url = context.portal_url.getPortalObject().absolute_url()

# redirect immediately
return REQUEST.RESPONSE.redirect(next_url)
