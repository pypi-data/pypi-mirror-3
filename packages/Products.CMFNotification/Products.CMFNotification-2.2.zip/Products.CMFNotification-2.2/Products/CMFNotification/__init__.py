"""Product initialization.

$Id: __init__.py 229577 2010-12-29 13:47:24Z dbaty $
"""
from Products.CMFCore import utils as CMFCoreUtils

## Apply monkey patches and set permissions
import Products.CMFNotification.patches
import Products.CMFNotification.permissions

def initialize(context):
    from Products.CMFNotification import NotificationTool
    tools = (NotificationTool.NotificationTool, )
    CMFCoreUtils.ToolInit(NotificationTool.META_TYPE,
                          tools=tools,
                          icon='tool.gif').initialize(context)
