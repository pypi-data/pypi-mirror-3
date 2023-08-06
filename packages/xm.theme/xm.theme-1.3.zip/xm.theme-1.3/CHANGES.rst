History for xm.theme
====================

1.3 (2012-09-12)
----------------

- Moved to github: https://github.com/zestsoftware/xm.theme
  [maurits]

- Let the plone.contentviews viewlet work in both Plone 3 and 4,
  without AttributeError in Plone 4 for prepareObjectTabs.
  [maurits]


1.2 (2010-09-24)
----------------

- Added z3c.autoinclude.plugin target plone.
  [maurits]


1.1 (2010-05-01)
----------------

- Show Plone Site title in the header when you are not in a project,
  instead of showing hardcoded 'Extreme Management'.
  Fixes http://plone.org/products/extreme-management-tool/issues/203
  [maurits]

- cleaned up the other css files [mirella]

- cleaned up IEfixes [mirella]

- cleaned up forms.css.dtml [mirella]

- cleaned up columns.css [mirella]

- finished cleaning up authoring.css [mirella]

- started with cleaning up authoring.css [mirella]

- cleaned up public.css and base.css [mirella]

- more css code clean up [mirella]

- started with cleaning up css code [mirella]

- added german translation [jensens]

- Fix z-index for kupu-fulleditor-zoomed on #portal-top and 
  .documentContent. [laurens] 


1.0.1 (2009-03-22)
------------------

- Add-iteration css updated for planned iterations view [jladage]


1.0 (2009-03-15)
----------------
- removed cachesettings.xml because it contains site specifice configuration.
  It's now located in project.setup [jladage]

- added title to my projects menu

- added mockup folder for design proposals [laurens]

- moved two xm.theme specefic classes from extreme.css to xm.theme's main.css [laurens]

- removed two images from eXtremeManagement that weren't being used [laurens]

- disabled .myProject in print.css [laurens]

- Ticket #148 - Removed 'my project' link. [simon]

- Ticket #147 - Overrode path_bar template to remove 'Home'. [simon]

- Fixed KSSUnicodeError in the fullname viewlet when you have a
  non-ascii name.  [maurits]

- Added Products.eXtremeManagement>=2.0alpha3 to our dependencies in
  setup.py.  http://plone.org/products/extreme-management-tool/issues/157
  shows we need at least that version.  [maurits]


1.0rc2 (2009-02-25)
-------------------

- Added cachesettings.xml to store our xm rules.


1.0rc1 (2009-01-25)
-------------------

- Added extra viewlet for the my project stub in portaltop. [jladage]

- Fixed issue 100, insert list of projects on DOM load. [reinout +
  mark]

- Fixed issue 135, Titles of portlets are now not transformed to
  capitalized.  [jladage]

- Fixed issue 126, When adding a project the header was not displayed.
  [jladage]


1.0beta2 (2009-01-15)
---------------------

- Style and portlet cleanup by laurens and jladage. [laurens, jladage]


1.0beta1 (2009-01-09)
---------------------

- Overrode the login portlet template, added a footer to the Login portlet. [simon]


0.9 (2009-01-07)
----------------

- Also show Documents as attachments. [mark]

- Remove the viewlets which showed the iterations grouped by
  state since there is a porlet to do this. [mark]

- The username is not rendered on each page but on DOM load. This allows for
  caching based on roles instead of each user.[jladage]

- Images are moved to a skins folder, so they get cached properly using the
  HTTPCache. [jladage]

- The username in the personal_bar now links to the author page instead of the
  dashboard. [jladage]

- Added 'Iterations:' in front of the open/current/closed iterations list and
  show it only if we have iterations in the project.  [fredvd]

- Moved the employees_overview page to Products.eXtremeManagement.
  [maurits]

- Made the employees overview page much much faster.  The billable
  percentages are not quite the same as from the bookings per month
  pages they point to, but that is for another day.  [maurits]

- Protecting the big employees overview page with the Manage Portal
  permission now.  [maurits]


0.8 (2008-09-16)
----------------

- Added locales/en to work around i18n bug: with e.g. Dutch and
  English as allowed languages, Dutch as site default, English as
  browser language (the only one or not), you would get Dutch for all
  translations in the xm.theme domain, even though the rest of the UI
  is in English... [maurits]

- Fixed the livesearch.js customization to work with Plone 3.1.x We have to drop
  support for Plone 3.0.x for this one, because jquery.js is not available.
  [jladage]


0.7.3 (2008-08-01)
------------------

- Use gradient image in booking-per-month table heading.  [mirella]
  (Moved from Products.eXtremeManagement trunk by Maurits.)

- Made gradient images bigger in height for layout reasons. [mirella]

- Fixed name typo in css. [mirella]

- Placed the gradient images in bottom in the used classes. [mirella]

- Added translations and description for employees overview. [mirella]

- Added odd color and padding to employees overview. [mirella]

- Started HISTORY.txt (merged from 0.7.2).  [maurits]



0.7 (2008-05-15)
----------------

- No history recorded.


0.6 (2008-03-31)
----------------

- No history recorded.


0.5 (2008-03-03)
----------------

- No history recorded.


0.4 (2008-02-27)
----------------

- No history recorded.


0.3 (2008-02-26)
----------------

- No history recorded.


0.2 (2008-02-25)
----------------

- No history recorded.
