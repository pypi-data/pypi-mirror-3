# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    #dict(name='calendar_date_format', type_='string', value='%A %d %B %Y'),
    ]

def import_various(context):
    if context.readDataFile('monet.calendar.extensions-various.txt') is None:
        return
