# -*- coding: utf-8 -*-
# $Id: __init__.py 76360 2008-11-23 22:25:42Z glenfant $

from Products.Archetypes.atapi import listTypes, process_types

GLOBALS = globals()

from config import DEFAULT_ADD_CONTENT_PERMISSION, PROJECTNAME

def initialize(context):
    from Products.Collage import content
    from Products.CMFCore import utils as cmfutils

    dummy = content # Keep pyflakes silent
    # initialize the content, including types and add permissions
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit('%s Content' % PROJECTNAME,
                         content_types = content_types,
                         permission = DEFAULT_ADD_CONTENT_PERMISSION,
                         extra_constructors = constructors,
                         fti = ftis,
                         ).initialize(context)
