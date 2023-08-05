# -*- coding: utf-8 -*-

import sys
import datetime
import time

if sys.version_info < (2, 6):
    Plone3 = True
    from Products.ATContentTypes.interface import IATTopicSearchCriterion as IBase
    from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
else:
    Plone3 = False
    from Products.ATContentTypes.interfaces import IATTopicSearchCriterion as IBase

from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.ATContentTypes import criteria
from Products.ATContentTypes.criteria import LIST_INDICES
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.date import ATDateCriteriaSchema, ATDateCriteria
from Products.ATContentTypes.criteria.daterange import ATDateRangeCriterionSchema, ATDateRangeCriterion
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.Archetypes.atapi import DisplayList
from DateTime import DateTime

from monet.calendar.criteria.config import PROJECTNAME


CompareOperations = DisplayList((
                   ('within_day', _(u'On the day')),
    ))

monet_ATDateCriteriaSchema = ATDateCriteriaSchema.copy()
monet_ATDateCriteriaSchema['operation'].vocabulary = CompareOperations


def date_range(start, end):
    if Plone3:
        start = datetime.datetime(*(time.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d')[0:6]))
        end = datetime.datetime(*(time.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d')[0:6]))        
    else:
        start = datetime.datetime.strptime(start.strftime('%Y-%m-%d'), '%Y-%m-%d')
        end = datetime.datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d')
    r = (end+datetime.timedelta(days=1)-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]

class IMonetTopicSearchCriterion(IBase):
    pass

class MonetATDateCriteria(ATDateCriteria):
    """A relative date criterion"""

    if Plone3:
        __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    else:
        implements(IMonetTopicSearchCriterion)
    

    security       = ClassSecurityInfo()
    schema         = monet_ATDateCriteriaSchema
    meta_type      = 'monet_ATFriendlyDateCriteria'
    archetype_name = 'Calendar friendly Date Criteria'
    shortDesc      = 'Calendar relative date'



    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        items = ATDateCriteria.getCriteriaItems(self)
        if not items:
            return ()

        query, range = items[0][1].values()
        if len(query) < 2:
            return ()

        result = []
        start, end = query
        current = DateTime()
        if current > start:
            end = current
        else:
            start = current
        value = tuple([a.strftime('%Y-%m-%d') for a in date_range(start, end)])

        result.append((self.Field(), { 'query': value}),)
        return tuple(result)


class MonetATDateRangeCriterion(ATDateRangeCriterion):
    """A date range criterion"""

    if Plone3:
        __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    else:
        implements(IMonetTopicSearchCriterion)

    security       = ClassSecurityInfo()
    schema         = ATDateRangeCriterionSchema
    meta_type      = 'monet_ATDateRangeCriterion'
    archetype_name = 'Calendar Date Range Criterion'
    shortDesc      = 'Calendar date range'


    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        items = ATDateRangeCriterion.getCriteriaItems(self)
        if not items:
            return ()

        query, range = items[0][1].values()
        if len(query) < 2:
            return ()

        result = []
        start, end = query
        value = tuple([a.strftime('%Y-%m-%d') for a in date_range(start, end)])

        result.append((self.Field(), { 'query': value}),)
        return tuple(result)

# trick for register the criteria in the project namespace, not Archetpyes ones
old = criteria.PROJECTNAME
criteria.PROJECTNAME = PROJECTNAME
criteria.registerCriterion(MonetATDateCriteria, LIST_INDICES)
criteria.registerCriterion(MonetATDateRangeCriterion, LIST_INDICES)
criteria.PROJECTNAME = old
