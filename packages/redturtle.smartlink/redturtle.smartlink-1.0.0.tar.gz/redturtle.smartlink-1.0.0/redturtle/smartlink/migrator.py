# -*- coding: utf-8 -*-

from plone.app.blob.migrations import migrate

def migrateSmartLink(context):
    return migrate(context, 'Link', 'ATLink')
