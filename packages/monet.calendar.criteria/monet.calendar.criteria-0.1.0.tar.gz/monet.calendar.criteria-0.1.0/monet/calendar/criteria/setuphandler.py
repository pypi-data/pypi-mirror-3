# -*- coding: utf-8 -*-

from monet.calendar.criteria import logger

INDEXES_TO_ADD = (
                  ('EventDuration', 'KeywordIndex', {'indexed_attrs': 'getISODates',},),
                  )

def _addKeysToCatalog(portal):
    portal_catalog = portal.portal_catalog

    indexes = portal_catalog.indexes()
    for idx in INDEXES_TO_ADD:
        if idx[0] in indexes:
            logger.info("Found the '%s' index in the catalog, nothing changed." % idx[0])
        else:
            portal_catalog.addIndex(name=idx[0], type=idx[1], extra=idx[2])
            logger.info("Added '%s' (%s) to the catalog." % (idx[0], idx[1]))

def extensions(context):
    if context.readDataFile('monet.calendar.event-various.txt') is None:
        return
    site = context.getSite()    
    _addKeysToCatalog(site)
