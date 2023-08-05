from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from valentine.multiparagraphpage import multiparagraphpageMessageFactory as _

class IMultiParagraphPage(Interface):
    """Page with a list of manageable paragraphs"""
    
    # -*- schema definition goes here -*-
