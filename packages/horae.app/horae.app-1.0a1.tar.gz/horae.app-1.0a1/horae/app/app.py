import grok

from zope.interface import classImplements
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zc.relation.interfaces import ICatalog
from z3c.relationfield import RelationCatalog

from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication

from horae.core.interfaces import IAppConfigurationHolder, IHorae
from horae.ticketing.interfaces import IClientContainerHolder
from horae.properties import interfaces

from horae.auth import auth
from horae.core import idmanager
from horae.search import catalog


class Horae(grok.Application, grok.Container):
    grok.implements(IHorae,
                    IClientContainerHolder,
                    IAppConfigurationHolder,
                    interfaces.IGlobalPropertiesHolder,
                    interfaces.IClientPropertiesHolder,
                    interfaces.IProjectPropertiesHolder,
                    interfaces.IMilestonePropertiesHolder,
                    interfaces.ITicketPropertiesHolder)
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=auth.setup_authentication)
    grok.local_utility(idmanager.IntIdManager)
    grok.local_utility(IntIds, provides=IIntIds)
    grok.local_utility(RelationCatalog, provides=ICatalog)
    grok.local_utility(catalog.Query)

try:
    from horae.resources import interfaces
    classImplements(Horae,
                    interfaces.IGlobalResourcesHolder,
                    interfaces.ICostUnitsHolder)
except ImportError: # horae.resources not available
    pass

try:
    from horae.workflow import interfaces
    classImplements(Horae,
                    interfaces.IClientWorkflowHolder,
                    interfaces.IProjectWorkflowHolder,
                    interfaces.IMilestoneWorkflowHolder,
                    interfaces.ITicketWorkflowHolder)
except ImportError: # horae.workflow not available
    pass
