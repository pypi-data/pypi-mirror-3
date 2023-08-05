from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from Products.CMFCore.utils import getToolByName
from Products.PloneTemplates import MessageFactory as _
from plone.memoize.instance import memoize


class TemplateSubMenuItem(BrowserSubMenuItem):
    title = _(u"label_actions_menu", default=u"Templates")
    description = _(u"title_actions_menu", 
            default=u"Create new content based on existing templates.")
    submenuId = "plone_contentmenu_templates"

    order = 25
    extra = dict(id="plone-contentmenu-templates")

    @property
    def action(self):
        context_state=getMultiAdapter((self.context, self.request),
                                      name='plone_context_state')
        add_context_url=context_state.folder().absolute_url()
        return add_context_url+"/template_overview",

    @memoize
    def available(self):
        # Punt if our tool is not present 
        ptt=getToolByName(self.context, "PloneTemplates_tool", None)
        if ptt is None:
            return False

        # Use the same logic as the standard Plone 3 factory menu: only
        # offer to create new content if the user is looking at a folder
        # or its default page.
        context_state=getMultiAdapter((self.context, self.request), name='plone_context_state')
        addContext=context_state.folder()
        if addContext.absolute_url()!=self.context.absolute_url() \
                and not context_state.is_default_page():
            return False

        return bool(ptt.getTemplates(aq_inner(self.context)))

    def disabled(self):
        return False

    def selected(self):
        return False


class TemplateMenu(BrowserMenu):
    @memoize
    def getMenuItems(self, context, request):
        ptt=getToolByName(context, "PloneTemplates_tool")
        templates=ptt.getTemplates(context)
        context_state=getMultiAdapter((context, request), name='plone_context_state')
        add_context_url=context_state.folder().absolute_url()

        def makeMenuItem(template):
            info=dict(title=template.title_or_id(),
                      description=template.Description(),
                      selected=False,
                      icon=template.getAutoIcon(),
                      extra={ "id" : "template_%s" % template.UID(),
                              "separator" : None,
                              "class" : ""
                              },
                      submenu=None)
            if template.getShowUsage():
                info["action"]="%s/template_usage?templateUID=%s" % \
                        (add_context_url, template.UID())
            else:
                info["action"]="%s/instantiateTemplate?templateUID=%s" % \
                        (add_context_url, template.UID())

            return info

        menu=[makeMenuItem(item) for item in templates[:10]]
        if len(templates)>10:
            menu.append(dict(title=_(u"More\u2026"),
                             description=u"",
                             action=add_context_url+"/template_overview",
                             selected=False,
                             icon=None,
                             extra={ "id" : "template_overview",
                                     "separator" : "actionSeparator",
                                     "class" : ""
                                     },
                             submenu=None))

        return menu


