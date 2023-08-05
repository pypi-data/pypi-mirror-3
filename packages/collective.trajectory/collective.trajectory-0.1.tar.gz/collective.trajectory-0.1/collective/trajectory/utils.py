from zope.app.component.hooks import getSite
from zope.globalrequest import getRequest

def getApp():
    return getRequest()['TRAJECTORY_APP']
