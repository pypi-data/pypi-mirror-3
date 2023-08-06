import logging

from AccessControl import ClassSecurityInfo

from App.class_init import default__class_init__ as InitializeClass

from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import \
    IExtractionPlugin, IChallengePlugin, IAuthenticationPlugin, \
    ICredentialsResetPlugin, ICredentialsUpdatePlugin

from anz.casclient.casclient import AnzCASClient
from anz.casclient.proxygrantingticketstorage import ProxyGrantingTicketStorage
from anz.casclient.sessionmappingstorage import SessionMappingStorage

root_logger = logging.getLogger('PluggableAuthService')
root_logger.setLevel(logging.DEBUG)

LOG = logging.getLogger('ewb_case.casclient')
    

add_cas_client_form = PageTemplateFile(
    '../browser/templates/add_cas_client_form.pt', globals()
)

def manage_add_cas_client(self, id, title=None, REQUEST=None):
    """ Add an instance of cas client to PAS.
    """
    obj = CasClient(id, title)
    self._setObject(obj.getId(), obj)
    
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '%s/manage_workspace'
            '?manage_tabs_message='
            'AnzCentralAuthService+added.'
            % self.absolute_url()
        )


class CasClient(AnzCASClient):
    meta_type = 'EWB Case CAS Client'

    email_format_string = "%s"

    _properties = getattr(AnzCASClient, '_properties', ()) + ({
        'id': 'email_format_string',
        'lable': 'Email Format String',
        'type': 'string',
        'mode': 'w',
    },)

    security = ClassSecurityInfo()

    def __init__(self, id, title, **kwargs):
        self._id = self.id = id
        self.title = title
        self._pgtStorage = ProxyGrantingTicketStorage()
        self._sessionStorage = SessionMappingStorage()
        
    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        if credentials['extractor'] != self.getId():
            return None
        
        login = credentials['login']
        acl_users = getToolByName(self, 'acl_users')
        if login is not None and acl_users.getUserById(login) is None:
            # create new user
            regtool = getToolByName(self, 'portal_registration')
            password = regtool.generatePassword()
            
            roles = {'Member': True}
            regtool.addMember(login, password, roles=roles, properties={
                'username' : login,
                'email' : self.email_format_string % login
            })
        return (login, login)
    

classImplements(
    CasClient,
    IExtractionPlugin,
    IChallengePlugin,
    ICredentialsResetPlugin,
    IAuthenticationPlugin)

InitializeClass(CasClient)
