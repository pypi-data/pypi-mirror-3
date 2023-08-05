#!/bin/sh

DOMAIN='monet.calendar.criteria'

i18ndude rebuild-pot --pot i18n/plone-${DOMAIN}.pot --create plone .
#i18ndude rebuild-pot --pot i18n/plone-${DOMAIN}.pot --merge i18n/plone-manual.pot --create plone .
i18ndude sync --pot i18n/plone-${DOMAIN}.pot ./i18n/plone-${DOMAIN}.po
