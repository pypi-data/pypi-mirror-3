# -*- coding: utf-8 -*-
import grok
from grokcore.message import UniqueMessageSource


class AdminMessageSource(UniqueMessageSource):
    """Source for the administration messages
    """
    grok.name('admin')

    def send(self, message, type="admin"):
        return UniqueMessageSource.send(self, message, type=type)

    def list(self, type="admin"):
        return UniqueMessageSource.list(self, type=type)
