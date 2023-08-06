from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from acted.projects import projectsMessageFactory as _

class IACTEDProject(Interface):
    """Details about a particular ACTED Project"""
    
    # -*- schema definition goes here -*-
