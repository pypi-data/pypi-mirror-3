# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute


class IMainMenu(Interface):
    """A menu that allows the access to the different UI panels.
    """


class IUIPanel(Interface):
    """A panel of administration.
    """


class IGrokUIRealm(Interface):
    """Represents an abstract object that acts as the UI namespace.
    It provides an access to the very root folder and to the request.
    """
    root = Attribute("The root folder object.")
    request = Attribute("The HTTP request object.")
