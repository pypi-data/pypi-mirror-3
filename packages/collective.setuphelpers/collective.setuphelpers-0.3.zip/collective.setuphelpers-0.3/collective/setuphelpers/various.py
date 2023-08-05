import logging

from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.utils import getToolByName
from Products.TinyMCE.interfaces.utility import ITinyMCE
try:
    from plone.outputfilters.setuphandlers import install_mimetype_and_transforms
except ImportError:
    from Products.TinyMCE.setuphandlers import install_mimetype_and_transforms
    

from plone.app.controlpanel.filter import IFilterSchema

from zope.component import getUtility

logger = logging.getLogger('Sitesetup tools:various')

def registerDisplayViews(portal, views):
    """ Register additional display views for content types based on "views"
        dictionary containing list of additional view ids for each content type.

        @example views dictionary:

        DISPLAY_VIEWS = {
            'Folder': [
                'short-listing',
                'extended-listing'
            ],
            
            'Document': [
                'article-view',
                'fancy-document-view'
            ]
        }

        @call from setup handler:

        from tools.sitesetup import registerDisplayViews
        registerDisplayViews(portal, DISPLAY_VIEWS)

    """

    portal_types = getToolByName(portal, 'portal_types')

    for ptype in views.keys():
        for view_method in views[ptype]:
            type_info = portal_types.getTypeInfo(ptype)
            if view_method not in type_info.view_methods:
                type_info.view_methods = type_info.view_methods + (view_method,)
                logger.info('"%s" display view installed for %s.' % (view_method, ptype))


def unregisterDisplayViews(portal, views):
    """ Unregister additional display views for content types based on "views"
        dictionary containing list of additional view ids for each content type
        (the same as for registerDisplayViews method).
    """

    portal_types = getToolByName(portal, 'portal_types')

    for ptype in views.keys():
        updated_views = ()
        type_info = portal_types.getTypeInfo(ptype)
        for view_method in type_info.view_methods:
            if view_method not in views[ptype]:
                updated_views += (view_method,)
            else:
                logger.info('Removing "%s" display view for %s.' % (view_method, ptype))
        type_info.view_methods = updated_views


def setupCatalog(portal, indexes={}, metadata=[]):
    """ Register portal catalog indexes and metadata columns. """
    catalog = getToolByName(portal, 'portal_catalog')

    idxs = catalog.indexes()
    mtds = catalog.schema()
    
    for index in indexes.keys():
        if index not in idxs:
            catalog.addIndex(index, indexes[index])
            logger.info('Catalog index "%s" installed.' % index)
    
    for mt in metadata:
        if mt not in mtds:
            catalog.addColumn(mt)
            logger.info('Catalog metadata "%s" installed.' % mt)


def hideActions(portal, actions):
    """ Hide actions given dict of action categories with values as list of action ids """

    atool = getToolByName(portal, 'portal_actions')
    logger.info('Configuring portal actions..');
    for category in actions.keys():
        if category in atool.objectIds():
            for action in actions[category]:
                if action in atool[category].objectIds():
                    atool[category][action].visible = False
                    logger.info('Action "%s" in category "%s" made hidden.' % (action, category))
                else:
                    logger.warning('Action "%s" in category "%s" not found!' % (action, category))
        else:
            logger.warning('Category "%s" not found!' % category)
    
def registerActions(portal, actions={}):
    """ Register new portal actions using dict of action attributes like in the following
        example:
        CUSTOM_ACTIONS = {
            '1': { # order in which will be action registered
                'id': 'my-action',
                'category': 'site_actions',
                'title': 'My action',
                'i18n_domain': 'myi18n.domain',
                'url_expr': string:${globals_view/navigationRootUrl}/my-action-view',
                'permissions': ('View',),
                'visible': True
            }
        }
    """
    
    atool = getToolByName(portal, 'portal_actions')
    
    action_keys = sorted(actions.keys())

    for key in action_keys:
        info = actions[key]
        uid = info.get('id')
        category = atool.get(info.get('category', None))
        if category is not None:
            category._setObject(uid, Action(
                    uid,
                    title       = info.get('title'),
                    i18n_domain = info.get('i18n_domain'),
                    url_expr    = info.get('url_expr'),
                    permissions = info.get('permissions'),
                    visible     = info.get('visible', False)
                    )
            )
            logger.warning("Action \"%s\" successfully registered" % uid)
        else:
            logger.warning("Can't register action \"%s\" for nonexisting category \"%s\"" % (uid, info.get('category')))


def setupTinyMCE(portal, settings):
    """ Configures tinymce wysiwyg editor. Here is an example settings object:
    EDITOR_SETTINGS = {
        'attributes': {
            'contextmenu': False,
            'link_using_uids': True,
            'allow_captioned_images': True,
            '...': True
        },
        'commands': {
            'install_transforms': True
        },
        'toolbar': {
            'advhr':False,
            'anchor':False,
            'attribs':False,
            'backcolor':False,
            'bold':True,
            'bullist':True,
            'charmap':False,
            'cleanup':False,
            'code':True,
            'copy':False,
            'cut':False,
            'definitionlist':False,
            'emotions':False,
            'external':False,
            'forecolor':False,
            'fullscreen':False,
            'hr':False,
            'iespell':False,
            'image':True,
            'indent':False,
            'insertdate':False,
            'inserttime':False,
            'italic':True,
            'justifycenter':False,
            'justifyfull':False,
            'justifyleft':False,
            'justifyright':False,
            'link':True,
            'media':False,
            'nonbreaking':False,
            'numlist':True,
            'outdent':False,
            'pagebreak':False,
            'paste':False,
            'pastetext':False,
            'pasteword':False,
            'preview':False,
            'print':False,
            'redo':False,
            'removeformat':False,
            'replace':False,
            'save':False,
            'search':False,
            'strikethrough':False,
            'style':True,
            'sub':False,
            'sup':False,
            'tablecontrols':True,
            'underline':False,
            'undo':False,
            'unlink':True,
            'visualaid':False,
            'visualchars':False,
            'width':u'440'
        },
        'styles': [
            'Subheading|h3',
            '...|..'
        ],
        'tablestyles': [
            'Subdued grid|plain',
            '...|...'
        ],
        'linkable': [
            'News Item',
            '...'
        ],
        'containsanchors': [
            'Document',
            '...'
        ],
        'containsobjects': [
            'Folder',
            '...'
        ],
        'imageobjects': [
            'Image',
            '...'
        ],
    }
    """

    tiny = getUtility(ITinyMCE)
    
    logger.info('Configuring TinyMCE..')
    for k,v in settings.get('attributes', {}).items():
        setattr(tiny, k, v)
        logger.info('"%s" set to: %s' % (k, v))

    commands = settings.get('commands', {})
    if commands.get('install_transforms', False):
        logger.info('Running command: install_mimetype_and_transforms..')
        install_mimetype_and_transforms(portal)
    
    for k,v in settings.get('toolbar', {}).items():
        setattr(tiny, 'toolbar_' + k, v)
        logger.info('Toolbar action "toolbar_%s" set to: %s' % (k, v))

    for group in ['styles', 'tablestyles', 'linkable', 'containsanchors', 'containsobjects', 'imageobjects']:
        if settings.has_key(group):
            val = u'\n'.join(settings.get(group, []))
            setattr(tiny, group, val)
            logger.info('"%s" set to: %s' % (group, val))

    logger.info('TinyMCE configuration completed.')

def setupCTAvailability(portal, settings):
    """ Use this method to allow/disable content types to be globally or locally addable.
        All non listed content types will be automatically disabled.
        Here is example settings object (NOTE: "DISABLE" key is used to disable
        content types adding globally):

        CONTENT_TYPES_AVAILABILITY = {
            'DISABLE': [
                'Event',
                'Link'
            ],
            'Plone Site': [
                'Folder',
                'Document'
            ]
        }
    """

    portal_types = getToolByName(portal, 'portal_types')
    for portal_type,info in settings.items():
        if portal_type == 'DISABLE':
            for v in info:
                type_info = portal_types.getTypeInfo(v)
                try:
                    type_info.global_allow = False
                except AttributeError:
                    raise AttributeError("Can't set \"global_allow\" attribute for \"%s\" content type. Make sure that this content type is already installed if it's your custom one by using import step depends element on \"types\" step in your import step registration (zcml)." % v)
                logger.info('"%s" disabled globally.' % v)

        else:
            type_info = portal_types.getTypeInfo(portal_type)
            setattr(type_info, 'filter_content_types', True)
            setattr(type_info, 'allowed_content_types', tuple(info))
            logger.info('Allowed types for "%s" set to: %s' % (portal_type, tuple(info)))

def setupHTMLFiltering(portal, settings):
    """ Update html filtering configlet settings, by passing dict of settings as in the
        following example for enabling embed html content in the richtext:

        HTML_FILTER = {
            'remove': {
                'nasty': ['embed', 'object'],
                'stripped': ['object', 'param'],
                'custom': []
            },
            'add': {
                'nasty': [],
                'stripped': [],
                'custom': ['embed']
            }
        }

        NOTE: you can ommit empty lists
    """

    adapter = IFilterSchema(portal)
    to_remove = settings.get('remove', {})
    to_add = settings.get('add', {})

    if to_remove:
        nasty = to_remove.get('nasty', [])
        stripped = to_remove.get('stripped', [])
        custom = to_remove.get('custom', [])

        current_nasty = adapter.nasty_tags
        for item in nasty:
            if item in current_nasty:
                current_nasty.remove(item)
        adapter.nasty_tags = current_nasty

        current_stripped = adapter.stripped_tags
        for item in stripped:
            if item in current_stripped:
                current_stripped.remove(item)
        adapter.stripped_tags = current_stripped

        current_custom = adapter.custom_tags
        for item in custom:
            if item in current_custom:
                current_custom.remove(item)
        adapter.custom_tags = current_custom

    if to_add:
        nasty = to_add.get('nasty', [])
        stripped = to_add.get('stripped', [])
        custom = to_add.get('custom', [])

        current_nasty = adapter.nasty_tags
        for item in nasty:
            if item not in current_nasty:
                current_nasty.append(item)
        adapter.nasty_tags = current_nasty

        current_stripped = adapter.stripped_tags
        for item in stripped:
            if item not in current_stripped:
                current_stripped.append(item)
        adapter.stripped_tags = current_stripped

        current_custom = adapter.custom_tags
        for item in custom:
            if item not in current_custom:
                current_custom.append(item)
        adapter.custom_tags = current_custom


def registerTransform(portal, name, module):
    """
    Usage:

    registerTransform(portal, 'web_intelligent_plain_text_to_html',
        'Products.intelligenttext.transforms.web_intelligent_plain_text_to_html')

    """
    transforms = getToolByName(portal, 'portal_transforms')
    if name not in transforms.objectIds():
        transforms.manage_addTransform(name, module)
        logger.info("Registered transform: %s" % name)
    else:
        logger.info("Transform with name: %s already exists." % name)

def unregisterTransform(portal, name):
    """
    Usage:

    unregisterTransform(portal, 'web_intelligent_plain_text_to_html')

    """
    transforms = getToolByName(portal, 'portal_transforms')
    try:
        if name in transforms.objectIds():
            transforms.unregisterTransform(name)
            logger.info("Removed transform: %s" % name)
        else:
            logger.info("Transform with name: %s doesn't exist" % name)
    except AttributeError:
        logger.info("Could not remove transform: %s" % name)

def setHomePage(portal, view_name):
    """ Set default view for the site root. """

    portal.setLayout(view_name)
    logger.info('Homepage set to "%s"' % view_name)
