cone.ugm.model.settings
=======================

App path for testing::

    >>> import os
    >>> import pkg_resources
    >>> path = pkg_resources.resource_filename('cone.ugm', '')
    >>> path = os.path.sep.join(path.split(os.path.sep)[:-3])
    >>> path
    '...cone.ugm'
    
    >>> import cone.ugm.model.utils
    >>> old_ugm_config_path = cone.ugm.model.utils.LDAP_CFG_FILE
    >>> cone.ugm.model.settings.LDAP_CFG_FILE = \
    ...     os.path.join(path, 'etc', 'ldap.xml')

Create dummy settings container::

    >>> from node.base import OrderedNode
    >>> from cone.ugm.model.settings import (
    ...     ServerSettings,
    ...     UsersSettings,
    ...     GroupsSettings,
    ... )
    >>> settings = OrderedNode()
    >>> settings['ugm_server'] = ServerSettings()
    >>> settings['ugm_users'] = UsersSettings()
    >>> settings['ugm_groups'] = GroupsSettings()

LDAP props::

    >>> props = settings['ugm_server'].ldap_props
    >>> props.uri
    u'ldap://127.0.0.1:12345'
    
    >>> props.user
    u'cn=Manager,dc=my-domain,dc=com'
    
    >>> props.password
    u'secret'
    
    >>> md = settings['ugm_server'].metadata
    >>> md.title
    'LDAP Props'
    
    >>> md.description
    'LDAP properties'

LDAP users config::

    >>> ucfg = settings['ugm_users'].ldap_ucfg
    >>> ucfg.baseDN
    u'ou=users,ou=groupOfNames_100_100,dc=my-domain,dc=com'
    
    >>> ucfg.attrmap
    {'cn': 'cn', 
    'userPassword': 'userPassword', 
    'sn': 'sn', 
    'mail': 'mail', 
    'login': 'uid', 
    'rdn': 'uid', 
    'id': 'uid'}
    
    >>> ucfg.scope
    1
    
    >>> ucfg.queryFilter
    u''
    
    >>> ucfg.objectClasses
    [u'top', u'person', u'organizationalPerson', u'inetOrgPerson']
    
    >>> md = settings['ugm_users'].metadata
    >>> md.title
    'Users Settings'
    
    >>> md.description
    'LDAP users settings'

LDAP groups config::

    >>> gcfg = settings['ugm_groups'].ldap_gcfg
    >>> gcfg.baseDN
    u'ou=groups,ou=groupOfNames_100_100,dc=my-domain,dc=com'
    
    >>> gcfg.attrmap
    {'rdn': 'cn', 
    'id': 'cn'}
    
    >>> gcfg.scope
    1
    
    >>> gcfg.queryFilter
    u''
    
    >>> gcfg.objectClasses
    [u'groupOfNames']
    
    >>> md = settings['ugm_groups'].metadata
    >>> md.title
    'Groups Settings'
    
    >>> md.description
    'LDAP groups settings'

LDAP connectivity tests::

    >>> from node.ext.ldap.properties import LDAPProps
    >>> props = LDAPProps(
    ...     uri='ldap://127.0.0.1:12346/',
    ...     user='',
    ...     password='',
    ...     cache=False,
    ... )
    
    >>> settings['ugm_server']._ldap_props = props
    
    >>> settings['ugm_server'].ldap_connectivity
    False
    
    >>> settings['ugm_users'].ldap_users_container_valid
    False
    
    >>> settings['ugm_groups'].ldap_groups_container_valid
    False
    
    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']
    
    >>> settings['ugm_server'].ldap_connectivity
    True
    
    >>> old_users_dn = settings['ugm_users'].attrs.users_dn
    >>> settings['ugm_users'].attrs.users_dn = \
    ...     u'ou=users,ou=groupOfNames_10_10,dc=my-domain,dc=com'
    
    >>> old_groups_dn = settings['ugm_groups'].attrs.groups_dn
    >>> settings['ugm_groups'].attrs.groups_dn = \
    ...     u'ou=groups,ou=groupOfNames_10_10,dc=my-domain,dc=com'
    
    >>> settings['ugm_users'].ldap_users_container_valid
    True
    
    >>> settings['ugm_groups'].ldap_groups_container_valid
    True

    >>> settings['ugm_users'].attrs.users_dn = old_users_dn
    >>> settings['ugm_groups'].attrs.groups_dn = old_groups_dn

Settings are written on ``__call__``. At the moment all settings are in one
file, so calling either ucfg, gcfg or props writes all of them::

    >>> settings['ugm_server']()

Test invalidate::

    >>> import cone.app
    >>> import cone.ugm
    >>> backend = cone.ugm.backend
    >>> backend
    
    >>> root = cone.app.root
    >>> from cone.ugm.model.utils import ugm_backend
    >>> backend = ugm_backend(root)
    
    >>> backend
    <Ugm object 'ugm' at ...>
    
    >>> backend is ugm_backend(root)
    True
    
    >>> settings = root['settings']
    >>> props = settings['ugm_server'].ldap_props
    >>> ucfg = settings['ugm_users'].ldap_ucfg
    >>> gcfg = settings['ugm_groups'].ldap_gcfg
    
    >>> props is settings['ugm_server'].ldap_props
    True
    
    >>> ucfg is settings['ugm_users'].ldap_ucfg
    True
    
    >>> gcfg is settings['ugm_groups'].ldap_gcfg
    True
    
    >>> settings['ugm_server'].invalidate()
    >>> backend is ugm_backend(root)
    False
    
    >>> props is settings['ugm_server'].ldap_props
    False
    
    >>> ucfg is settings['ugm_users'].ldap_ucfg
    False
    
    >>> gcfg is settings['ugm_groups'].ldap_gcfg
    False

Reset backend and prepare settings for following tests::

    >>> cone.ugm.backend = None
    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']
