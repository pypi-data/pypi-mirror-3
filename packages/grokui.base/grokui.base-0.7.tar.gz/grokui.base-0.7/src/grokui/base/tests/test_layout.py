"""
Building panels using `GrokUIView`
===================================

We create a browser to watch our views:

    >>> from zope.app.wsgi.testlayer import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False

To create a view that automatically comes with the GrokUI layout, we
can derive from `grokui.base.AdminView`.

Instances of `AdminView` are in fact `grok.Page` instances
that render the content provided by a template or `render` method
into a given layout.

When we render PlainAdminView, we will get a complete Grok UI page
with the contents delivered by the `render()` method inserted:

    >>> browser.open('http://localhost/++grokui++/caveview')
    >>> print browser.contents
    <html xmlns="http://www.w3.org/1999/xhtml">
    ...
     <title>Grok User Interface</title>
    ...
    <BLANKLINE>
        <div id="grokui-content">Hello from CaveAdminView</div>
    <BLANKLINE>
    ...
    </html>

We also provided a ``title`` with our page. Therefore we will get an
entry in the navigation bar:

    >>> print browser.contents
    <html xmlns="http://www.w3.org/1999/xhtml">
    ...
    <ul id="grokui-menu-entries">
      <li>
        <a href="http://localhost/++grokui++/caveview"
           title="cave management">cave management</a>
      </li>
    </ul>
    ...
    </html>

"""
import grokui.base
import unittest
import doctest
import grok
from grokui.base import GrokUIView
from zope.fanstatic.testing import ZopeFanstaticBrowserLayer


class CaveAdminView(GrokUIView):
    """An admin page to administer caves.
    """
    grok.name('caveview')
    # This title will appear in the navigation bar:
    grok.title('cave management')

    def render(self):
        """This will go into a standard Grok UI page.
        """
        return u'Hello from CaveAdminView'


def test_suite():
    suite = unittest.TestSuite()
    test = doctest.DocTestSuite(
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = ZopeFanstaticBrowserLayer(grokui.base)
    suite.addTest(test)
    return suite
