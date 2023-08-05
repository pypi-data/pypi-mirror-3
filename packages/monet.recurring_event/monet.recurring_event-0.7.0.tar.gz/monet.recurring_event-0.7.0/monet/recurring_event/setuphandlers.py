# -*- coding: utf-8 -*-

import logging
from plone.browserlayer.utils import unregister_layer

def uninstallVarious(context):
    if context.readDataFile('monet.recurring_event-uninstall.txt') is None:
        return
    
    logger = logging.getLogger('monet.recurring_event')

    # See http://blog.fourdigits.nl/removing-a-persistent-local-utility-part-ii
#    portal = context.getSite()
#    sm = portal.getSiteManager()
#    for x in sm._utility_registrations.keys():
#        if x[1] == 'monet.recurring_event':
#            del sm._utility_registrations[x]
#            logger.info("Removed %s" % x[1])

    unregister_layer('monet.recurring_event')
    logger.info("Removed monet.recurring_event browser layer")

