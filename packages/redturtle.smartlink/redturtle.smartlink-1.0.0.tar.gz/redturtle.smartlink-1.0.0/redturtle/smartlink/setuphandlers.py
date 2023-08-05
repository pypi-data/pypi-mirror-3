# -*- coding: utf-8 -*-


def setupVarious(context):
    portal = context.getSite()

    if context.readDataFile('redturtle.smartlink_various.txt') is None:
        return
