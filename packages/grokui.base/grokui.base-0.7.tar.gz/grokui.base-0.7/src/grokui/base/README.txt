
.. contents::


Detailed Description
********************

``grokui.base`` provides tools to assemble a coherent environment.


The ``++grokui++`` namespace
============================

In order to keep a sane and clean naming policy, the grokui components
are compartmented in a logical namespace, ``++grokui++``, which is
defined and registered in `grokui.base`.

This namespace is a multi-adapter that will act like a parent for the
view. It's the natural context of all the grokui pages. Let's get out
first contact with this namespace::

  >>> from grokui.base import GrokUINamespace
  >>> from grokui.base import IGrokUIRealm

  >>> IGrokUIRealm.implementedBy(GrokUINamespace)
  True

Example
-------

We can build a simple admin screen that fits into the environment like
this:

    >>> from martian.testing import FakeModule
    >>> import grok
    >>> from zope.interface import Interface
    >>> from grokui.base import GrokUILayer

    >>> class mymodule(FakeModule):
    ...     class MyAdminScreen(grok.View):
    ...       grok.layer(GrokUILayer)
    ...       grok.name('helloadmin')
    ...       grok.context(Interface)
    ...       def render(self):
    ...         return u'Hello admin!'
    >>> from martiantest.fake.mymodule import MyAdminScreen

The important thing here is, that we set our view to belong to the
GrokUI namespace, which is named ``++grokui++`` in URLs.

We grok this view to register it with the component architechture:

    >>> from grokcore.component.testing import grok_component
    >>> grok_component('MyAdminScreen', MyAdminScreen)
    True

Let's create a browser to lookup this view:

    >>> from zope.app.wsgi.testlayer import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

We can get this screen when we ask for the correct namespace:

    >>> browser.open('http://localhost/++grokui++/@@helloadmin')
    >>> print browser.contents
    Hello admin!

If we ask for this view without the namespace set correctly, the view
will not be found:

    >>> browser.open('http://localhost/@@helloadmin')
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found


GrokUI Pages
============

We can, however, also create admin pages, that fit completely into the
GrokUI layout without much hassle, providing a menu bar, images and
all other parts of the standard grokui layout automatically for your
page.

To do so, we derive our admin page from ``GrokUIView``, give it a
title, and optionally set an order number:

    >>> from grokui.base.layout import GrokUIView
    >>> from grokui.base.namespace import GrokUILayer

    >>> class mymodule(FakeModule):
    ...   class CaveManagementScreen(GrokUIView):
    ...     # Name where we can access this page via URL:
    ...     grok.name('managecave')
    ...     # Also optional, but highly recommended:
    ...     grok.require('zope.ManageServices')
    ...     # Set title of page in menu bar:
    ...     grok.title('admin stuff')
    ...     # Display this entry very far to the left in menu bar:
    ...     grok.order(-1)
    ...
    ...     def render(self):
    ...       # Instead of render() we could also define a page template
    ...       # for the actual contents of this page.
    ...       return u'Hello cave manager!'
    >>> from martiantest.fake.mymodule import CaveManagementScreen
    >>> grok_component('CaveManagementScreen', CaveManagementScreen)
    True

While the title will be displayed in the main menu bar of the GrokUI
layout automatically, the ``order`` tells at which position in the
menu we want our page to appear. Pages without a title do not appear
in the menu bar at all.

Instances of `GrokUIView` are in fact `grok.Page` instances
that render the content provided by a template or `render` method
into a given layout (here: the general GrokUI layout).

We can access the page in GrokUI namespace ``++grokui++`` under the
name given above (``managecave``):

    >>> browser.open('http://localhost/++grokui++/managecave')
    >>> print browser.contents
    <html xmlns="http://www.w3.org/1999/xhtml">
    ...<head>
    ...<title>Grok User Interface</title>
    ...<base href="http://localhost/++grokui++/" />
    ...Hello cave manager!...
    ...

Making your admin page the default target page
==============================================

The above admin page was set up with order number ``-1``. That means,
that its menu entry will appear at far left position in the menu
bar. As we have currently no menu entries with a lower order number,
the entry will even appear at leftmost position.

Furthermore this leftmost entry is also the default page if someone
wants to see the index page of the running Zope instance at all:

    >>> browser.open('http://localhost/')
    >>> browser.url
    'http://localhost/++grokui++/@@managecave'

This means, we've been redirected to our cave admin page.

If we want to change this default, for instance in order to set
another page as default, we simply have to provide a lower order
number for that other admin page. The redirect will then redirect to
it.
