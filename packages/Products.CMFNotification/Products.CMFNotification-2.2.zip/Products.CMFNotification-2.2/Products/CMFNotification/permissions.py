"""Define CMFNotification specific permissions.

$Id: permissions.py 115106 2010-04-12 09:15:14Z jcbrand $
"""
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles
from config import PROJECT_NAME

security = ModuleSecurityInfo(PROJECT_NAME)

security.declarePublic('CMFNotification: Subscribe/unsubscribe')
## Warning: this value is also defined in ``profiles/default/rolemap.xml``
SUBSCRIBE_PERMISSION = 'CMFNotification: Subscribe/unsubscribe'
setDefaultRoles(SUBSCRIBE_PERMISSION, ())
