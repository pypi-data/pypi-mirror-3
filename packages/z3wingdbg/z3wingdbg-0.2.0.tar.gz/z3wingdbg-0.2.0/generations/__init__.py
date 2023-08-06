# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope.app.generations.generations import SchemaManager
from zope.app.publication.zopepublication import ZopePublication

key = 'z3wingdbg.generations'

z3wingdbgSchemaManager = SchemaManager(
    minimum_generation=1,
    generation=1,
    package_name=key)

def getRootFolder(context):
    return context.connection.root().get(ZopePublication.root_name, None)
