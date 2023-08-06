# -*- coding: utf-8 -*-

from zope.site.interfaces import IRootFolder
from zope.component import getUtility, getMultiAdapter
from zope.browsermenu.interfaces import IBrowserMenu
import grok
from megrok.menu import Menu
from grokui.base import IGrokUIRealm, GrokUILayer

grok.layer(GrokUILayer)
grok.context(IGrokUIRealm)


class Header(grok.ViewletManager):
    grok.name('grokui_header')


class Footer(grok.ViewletManager):
    grok.name('grokui_footer')


class Messages(grok.ViewletManager):
    grok.name('grokui_messages')


class MainMenu(Menu):
    grok.name('grokui_mainmenu')
    grok.title('Grok user interface panels')


class Index(grok.View):
    """Redirect to the grokui namespace.

    Redirect to the first item displayed in grokui-namespaced main
    menu.
    """
    grok.name('index')
    grok.context(IRootFolder)
    grok.require('zope.ManageServices')
    grok.layer(grok.IDefaultBrowserLayer)

    def render(self):
        menu = getUtility(IBrowserMenu, 'grokui_mainmenu')
        realm = getMultiAdapter((self.context, self.request),
                                name='grokui')
        items = menu.getMenuItems(realm, self.request)
        if len(items) == 0:
            # No grokui panel installed.
            return u'No further grokui components are installed.'
        first_name = items[0]['action']
        grokui_url = self.url(self.context) + '/++grokui++/@@' + first_name
        self.redirect(grokui_url)
        return
