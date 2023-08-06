# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt
brains = list(context.portal_catalog.searchResults(portal_type='Keyword'))
brains.sort(key=lambda x:x.name.lower())
return brains
