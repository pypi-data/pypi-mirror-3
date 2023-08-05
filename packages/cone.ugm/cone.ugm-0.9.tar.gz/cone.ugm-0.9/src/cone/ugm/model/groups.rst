cone.ugm.model.groups
=====================

::

    >>> layer.login('manager')

    >>> from cone.ugm.model.groups import Groups
    >>> from cone.app import root 
    >>> groups = root['groups']
    >>> groups
    <Groups object 'groups' at ...>
    
    >>> isinstance(groups, Groups)
    True

Check Properties::

    >>> props = groups.properties

Groups object is not editable::

    >>> props.editable
    False

Check Metadata::

    >>> md = groups.metadata
    >>> md.title
    'Groups'
    
    >>> md.description
    'Container for Groups'

Check for test groups::

    >>> len([x for x in groups])
    10

Access inexistent child::

    >>> groups['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: u'inexistent'

The children are group application nodes::
    
    >>> group = groups['group0']
    >>> group
    <Group object 'group0' at ...>

If we delete a group, it's not deleted from the underlying backend, this is
needed for invalidation::

    >>> del groups['group0']
    >>> groups['group0']
    <Group object 'group0' at ...>

Test invalidation::

    >>> backend = groups.backend
    >>> backend
    <Groups object 'groups' at ...>
    
    >>> backend is groups.backend
    True
    
    >>> groups.invalidate()
    >>> backend is groups.backend
    False

Check if ugm is not configured properly::

    >>> settings = root['settings']['ugm_server']
    >>> settings.invalidate()
    >>> [k for k in groups]
    []

    >>> layer.logout()

Reset settings for following tests::

    >>> settings = root['settings']
    >>> settings['ugm_server'].invalidate()
    >>> settings['ugm_server']._ldap_props = layer['props']
    >>> settings['ugm_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ugm_groups']._ldap_gcfg = layer['gcfg']
