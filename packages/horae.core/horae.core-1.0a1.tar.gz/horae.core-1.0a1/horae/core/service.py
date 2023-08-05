import grok
import transaction

from z3c.taskqueue import service, interfaces, startup
import z3c.taskqueue

from zope.site.hooks import getSite, setSite

from zope import component, interface
from zope.event import notify
from zope.security import management
from zope.processlifetime import IDatabaseOpenedWithRoot
from zope.app.publication.zopepublication import ZopePublication

from horae.core.interfaces import IHorae

task_service = None


class IHoraeServiceInitialized(interface.Interface):
    """ Notifies the initialization of the horae task service
    """

    service = interface.Attribute('The task service instance')


class HoraeServiceInitialized(object):
    interface.implements(IHoraeServiceInitialized)

    def __init__(self, service):
        self.service = service


@grok.subscribe(IDatabaseOpenedWithRoot)
def databaseOpened(event, productName='z3c.taskqueue'):
    global task_service
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    if not 'HoraeTaskService' in root_folder:
        root_folder['HoraeTaskService'] = service.TaskService()
        root_folder['HoraeTaskService'].__name__ = 'HoraeTaskService'
        notify(HoraeServiceInitialized(root_folder['HoraeTaskService']))
    task_service = root_folder['HoraeTaskService']
    task_service.processorArguments = {}
    component.provideUtility(task_service, interfaces.ITaskService, name='HoraeTaskService')
    transaction.commit()

    # START copy from z3c.taskqueue.startup.databaseOpened
    startup.log.info('handling event IDatabaseOpenedEvent')

    startup.storeDBReferenceOnDBOpened(event)

    from zope.app.appsetup.product import getProductConfiguration
    configuration = getProductConfiguration(productName)
    startSpecifications = startup.getStartSpecifications(configuration)

    for sitesIdentifier, servicesIdentifier in startSpecifications:
        startedAnything = False
        sites = startup.getSites(sitesIdentifier, root_folder)
        for site in sites:
            if servicesIdentifier == '*':
                started = startup.startAllServices(site, root_folder)
            else:
                started = startup.startOneService(site, servicesIdentifier)
            startedAnything = startedAnything or started

        if sitesIdentifier == "*" and not startedAnything:
            msg = 'no services started by directive *@%s'
            startup.log.warn(msg % servicesIdentifier)
    # END copy from z3c.taskqueue.startup.databaseOpened


def sites():
    db = z3c.taskqueue.GLOBALDB
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    interaction = management.getInteraction()
    participation = interaction.participations[0]
    participation.setPrincipal(management.system_user)
    transaction.commit()
    _site = getSite()
    for site in root_folder.values():
        if IHorae.providedBy(site):
            setSite(site)
            yield site
    setSite(_site)
    transaction.commit()
    connection.close()
