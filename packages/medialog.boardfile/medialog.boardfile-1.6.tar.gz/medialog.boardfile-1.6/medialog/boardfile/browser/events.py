"""
    Time based events
    A lot of code taken from collective.timedevents
    Mikko Ohtamaa <mikko.ohtamaa@twinapex.com

"""

__author__ = "spen Moe-Nilssen <espen@medialog.no>"
__license__ = "GPL"
__docformat__ = "epytext"

# Python imports
import logging

# Zope imports
import zope
from DateTime import DateTime
from zope.component import adapter
from zope.app.component.hooks import getSite

# Local imports
from interfaces import ITickEvent


# Plone imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.log import logger

 
# Design for testing:
# Number of items last call expired
triggered_count = 0



class TickEvent(object):
    """This class implements the ITickEvent interface.
    """
    zope.interface.implements(ITickEvent)

    def __init__(self, date_time, next_tick):
        self.date_time = DateTime(date_time)
        self.next_tick = DateTime(next_tick)


@adapter(ITickEvent)
def tick_logger(tick_event):
    """This function is a handler for the ITickEvent. Its purpose is to log all
       ticks.
    """
    l = logging.getLogger('timedevents')
    l.info('(%s) TICK detected...' % tick_event.date_time.ISO())



class TransitionTriggerTicker:
    """ Perform automatic transitions for workflows after certain amount of time is reached in some content attribute.
    """

    # Which WF attribute we check for the expiration
    # http://localhost:8080/Plone/portal_workflow/plone_workflow/variables/manage_workspace
    time_variable = "submit_time"

    
    def __call__(self, event):
        """

        @param event: zope event object
        """
        global triggered_count

        now = event.date_time
        
        #time before the workflow happens  20 days
        delta = 20
        
        site = getSite()
        logger.debug("Running timed workflow transitions checks at %s, site is: %s, transition is %s" % (str(now), str(site), self.transition))

        pct = getToolByName(site, 'portal_catalog')
        wf = getToolByName(site, 'portal_workflow')

        query = {}
        #query["object_provides"]=self.marker_interface.__identifier__
        query["portal_type"]="PublicationRequest"
        # Assumes WF stores its state in review_state variable
        query["review_state"]=self.state
        # Expires expression
        #query[self.time_index]={'query':DateTime() - self.delta, 'range':'min'}
        catalog_data = pct.unrestrictedSearchResults(**query)
        
 
        # The following loop is a bit expensive, since it
        # wakes up every object to get last transition time
        for item in catalog_data:

            obj = item.getObject()
            status = wf.getStatusOf(self.workflow, obj)

            logger.debug("Checking autotransition for:" + str(obj))

            if now >= status[self.time_variable] + self.delta:
                # Perform workflow transitions.
                # This triggers content rule based actions,
                # so we can put the actual action logic in the content rule
                logger.info("Triggering auto transition for:" + str(obj) + " state:" + status["review_state"] + " transition:" + self.transition)

                wf.doActionFor(obj, self.transition)

                triggered_count += 1

class AutoExpireDocument(TransitionTriggerTicker):
    """ Define a sample time based trigger. """

    workflow = "multiapprove_workflow"

    state = "pending"

    transition = "auto_publish"

    #marker_interface = ITickEvent
    #using content type instead
    
    pt = "Boardfile" #You need to change this in query lines above

    delta = 20 # 1 days
    
auto_expire = AutoExpireDocument()