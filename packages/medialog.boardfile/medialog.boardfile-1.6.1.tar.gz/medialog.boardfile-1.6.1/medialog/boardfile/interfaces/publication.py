from zope import schema
from zope.interface import Interface 

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from medialog.boardfile import boardfileMessageFactory as _

class IPublication(Interface):
    """Publication content type"""
    
    publicationcategory= schema.TextLine(
        title=_(u"Publication Category"), 
        required=True,
        description=_(u"Please select a category"),
    )

    publicationtitle= schema.TextLine(
        title=_(u"Journal/Conference"), 
        required=True,
        description=_(u"Name of Journal/Conference."),
    )

    authorlist = schema.Text(
        title=_(u"Authorlist"), 
        required=True,
        description=_(u"List of Authors"),
    )


    wp = schema.TextLine(
        title=_(u"WP"), 
        required=True,
        description=_(u"Select one"),
    )
    
    deliverable = schema.Float(
        title=_(u"Deliverable number"), 
        required=False,
        description=_(u"The deliverable number"),
    )

    publishingyear = schema.Int(
        title=_(u"Publishing Year"), 
        required=True,
        description=_(u"Publishing Year"),
    )

