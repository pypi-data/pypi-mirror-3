from zope.traversing.browser.absoluteurl import absoluteURL
import grok
from grokui.base import IGrokUIRealm, GrokUILayer, IUIPanel, MainMenu
from grokui.base import resource
import megrok.menu

grok.layer(GrokUILayer)


class GrokUILayout(grok.Layout):
    """The general layout for the administration
    """
    grok.context(IGrokUIRealm)
    title = u"Grok User Interface"

    def update(self):
        resource.grok_css.need()
        resource.favicon.need()
        self.baseurl = absoluteURL(self.context, self.request) + '/'


class GrokUIView(grok.Page):
    """A grok ui view.
    """
    grok.baseclass()
    grok.context(IGrokUIRealm)
    grok.implements(IUIPanel)
    megrok.menu.menuitem(MainMenu)
