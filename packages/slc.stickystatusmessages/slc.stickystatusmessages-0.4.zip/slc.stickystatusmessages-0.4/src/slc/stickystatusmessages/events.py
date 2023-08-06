import logging
import utils
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from slc.stickystatusmessages import StickyStatusMessageFactory as _
from slc.stickystatusmessages.interfaces import IStickyStatusMessagesSettings
from slc.stickystatusmessages.interfaces import IStickyStatusMessagesLayer
log = logging.getLogger('slc.stickystatusmessages/events.py')


def safe_unicode(txt):
    if not isinstance(txt, unicode):
        txt = txt.decode('utf-8')
    return txt


def ifenabled(func):
    """ This is a decorator to be applied on the event handlers below. It
        checks if they should be enabled and runs them, otherwise it does
        nothing.
    """
    def wrapper(*args, **kwargs):
        # TODO read registry here
        registry = queryUtility(IRegistry)
        if registry is None:
            return func(*args, **kwargs)
        try:
            settings = registry.forInterface(IStickyStatusMessagesSettings)
        except KeyError:
            return func(*args, **kwargs)
        if settings is None:
            return func(*args, **kwargs)
        if settings.rolebased:
            return func(*args, **kwargs)

    wrapper.__doc__ = func.__doc__
    return wrapper


@ifenabled
def object_copied_event(obj, evt):
    """ """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    folder = obj.aq_parent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    message = _(
        u'%s <a href="%s">%s</a> has been copied into <a href="%s">%s</a>' \
            % ( obj.portal_type,
                '/'.join(obj.getPhysicalPath()),
                safe_unicode(obj_title),
                '/'.join(folder.getPhysicalPath()),
                safe_unicode(folder_title),
                )
            )
    utils.set_sticky_status_message(obj, message)


@ifenabled
def object_moved_event(obj, evt):
    """ """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    if obj.isTemporary() or not evt.newParent or not evt.oldParent:
        return

    if 'portal_factory' in evt.oldParent.getPhysicalPath():
        return

    folder = evt.newParent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    message = _(
                u'%s <em>%s</em> moved into <a href="%s">%s</a>' \
                                        % ( obj.portal_type,
                                            safe_unicode(obj_title),
                                            '/'.join(folder.getPhysicalPath()),
                                            safe_unicode(folder_title),
                                            )
                )
    utils.set_sticky_status_message(obj, message)


@ifenabled
def object_removed_event(obj, evt):
    """ """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    folder = obj.aq_parent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    message = _(
                u'%s <em>%s</em> removed from <a href="%s">%s</a>' \
                                        % ( obj.portal_type,
                                            safe_unicode(obj_title),
                                            '/'.join(folder.getPhysicalPath()),
                                             safe_unicode(folder_title),
                                            )
                )
    utils.set_sticky_status_message(obj, message)


@ifenabled
def object_created_event(obj, evt):
    """ """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    folder = obj.aq_parent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    message = _(
                u'%s <a href="%s">%s</a> created in <a href="%s">%s</a>' \
                                    % ( obj.portal_type,
                                        '/'.join(obj.getPhysicalPath()),
                                        safe_unicode(obj_title),
                                        '/'.join(folder.getPhysicalPath()),
                                        safe_unicode(folder_title),
                                        )
                )
    utils.set_sticky_status_message(obj, message)


@ifenabled
def object_edited_event(obj, evt):
    """ """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    folder = obj.aq_parent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    message = _(
                u'%s <a href="%s">%s</a> edited in <a href="%s">%s</a>' \
                                    % ( obj.portal_type,
                                        '/'.join(obj.getPhysicalPath()),
                                        safe_unicode(obj_title),
                                        '/'.join(folder.getPhysicalPath()),
                                        safe_unicode(folder_title),
                                        )
                )
    utils.set_sticky_status_message(obj, message)


@ifenabled
def object_state_changed_event(obj, evt):
    """ """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    folder = obj.aq_parent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    workflowTool = getToolByName(obj, "portal_workflow")
    chain = workflowTool.getChainFor(obj)
    status = workflowTool.getStatusOf(chain[0], obj)
    state = status["review_state"]
    message = _(
                u'The workflow state of %s <a href="%s">%s</a> ' \
                'in <a href="%s">%s</a> has been changed to <em>%s</em>' \
                    % ( obj.portal_type,
                        '/'.join(obj.getPhysicalPath()),
                        safe_unicode(obj_title),
                        '/'.join(folder.getPhysicalPath()),
                        safe_unicode(folder_title),
                        state,
                        )
                )

    utils.set_sticky_status_message(obj, message)


@ifenabled
def object_parent_edited_event(obj, evt):
    """ Notify children when the parent is edited
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return
    if not IStickyStatusMessagesLayer.providedBy(request):
        return

    folder = obj.aq_parent
    folder_title = folder.Title() or ''
    obj_title = obj.Title() or ''
    message = _(
                u'%s <a href="%s">%s</a> edited in <a href="%s">%s</a>' \
                                    % ( obj.portal_type,
                                        '/'.join(obj.getPhysicalPath()),
                                        safe_unicode(obj_title),
                                        '/'.join(folder.getPhysicalPath()),
                                        safe_unicode(folder_title),
                                        )
                )
    for child in obj.objectIds():
        utils.set_sticky_status_message(obj[child], message)

