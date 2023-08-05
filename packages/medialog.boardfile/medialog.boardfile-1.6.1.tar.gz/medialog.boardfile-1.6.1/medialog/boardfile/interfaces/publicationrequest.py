from zope import schema
from zope.interface import Interface 

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from medialog.boardfile import boardfileMessageFactory as _


class IPublicationrequest(Interface):
    """Publication Request content type"""
    
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
    

    wp = schema.TextLine(
        title=_(u"WP"), 
        required=True,
        description=_(u"Select one"),
    )


    file = schema.Bytes(
        title=_(u"File"), 
        required=True,
        description=_(u"File to upload. If you have many, please zip them first"),
    )
 
