"""forge web user interface

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance
from cubicweb.web import uicfg, facet
from cubicweb.web.views.urlrewrite import (
    SimpleReqRewriter, SchemaBasedRewriter, rgx, build_rset)


class ForgeURLRewriter(SchemaBasedRewriter):
    """handle path with the form::

        project/<name>/documentation     -> view project's documentation
        project/<name>/screenshots       -> view project's screenshots
        project/<name>/tickets           -> view project's tickets
        project/<name>/versions          -> view project's versions in state ready
                                            or development, or marked as
                                            prioritary.
        project/<name>/[version]         -> view version
        project/<name>/[version]/tickets -> tickets for this version
    """
    priority = 10
    rules = [
        (rgx('/project/([^/]+)/documentation'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projectdocumentation')),
        (rgx('/project/([^/]+)/screenshots'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projectscreenshots')),
        (rgx('/project/([^/]+)/([^/]+)/tickets'),
         build_rset(rql='Any T WHERE T is Ticket, T done_in V, V version_of P, P name %(project)s, V num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)],
                    vtitle=_('tickets for %(project)s - %(num)s'))),
        (rgx('/project/([^/]+)/versions'),
         build_rset(rql='Any X,N ORDERBY version_sort_value(N) '
                    'WHERE X num N, X version_of P, P name %(project)s, '
                    'EXISTS(X in_state S, S name IN ("dev", "ready")) '
                    'OR EXISTS(T tags X, T name IN ("priority", "prioritaire"))',
                    rgxgroups=[('project', 1)], vid='ic_progress_table_view',
                    vtitle=_('upcoming versions for %(project)s'))),
        (rgx('/project/([^/]+)/tickets'),
         build_rset(rql='Any T WHERE T is Ticket, T concerns P, P name %(project)s',
                    rgxgroups=[('project', 1)], vid='table',
                    vtitle=_('tickets for %(project)s'))),
        (rgx('/project/([^/]+)/([^/]+)'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)])),
        (rgx('/project/([^/]+)/([^/]+)'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)])),
        (rgx('/p/([^/]+)'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1),])),
        (rgx('/t/([^/]+)'),
         build_rset(rql='Ticket T WHERE T eid %(teid)s',
                    rgxgroups=[('teid', 1),])),
         ]

# XXX some of those tags should be in tracker cube
_afs = uicfg.autoform_section
_afs.tag_attribute(('Version', 'progress_target'), 'main', 'hidden')
_afs.tag_attribute(('Version', 'progress_todo'), 'main', 'hidden')
_afs.tag_attribute(('Version', 'progress_done'), 'main', 'hidden')
_afs.tag_attribute(('Ticket', 'load'), 'main', 'attributes')
_afs.tag_attribute(('Ticket', 'load_left'), 'main', 'attributes')
_afs.tag_attribute(('Ticket', 'load'), 'muledit', 'attributes')
_afs.tag_attribute(('Ticket', 'load_left'), 'muledit', 'attributes')

_pvs = uicfg.primaryview_section

_pvs.tag_object_of(('*', 'documented_by', '*'), 'hidden')

_pvs.tag_subject_of(('Ticket', 'attachment', '*'), 'sideboxes')
_pvs.tag_object_of(('*', 'generate_bug', 'Ticket'), 'sideboxes')

_pvs.tag_subject_of(('Ticket', 'follow_up', '*'), 'hidden')
_pvs.tag_object_of(('*', 'follow_up', 'Ticket'), 'hidden')

_pvs.tag_attribute(('ExtProject', 'name'), 'hidden')

_pvs.tag_attribute(('License', 'name'), 'hidden')
_pvs.tag_attribute(('License', 'url'), 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('*', 'for_version', '*'), False)

_abaa.tag_subject_of(('Ticket', 'attachment', 'File'), True)

_abaa.tag_object_of(('Ticket', 'filed_under', 'Folder'), False)
_abaa.tag_object_of(('Version', 'filed_under', 'Folder'), False)

class TicketHasAttachmentFacet(facet.HasRelationFacet):
    __regid__ = 'forge.attachment-facet'
    __select__ = facet.HasRelationFacet.__select__ & is_instance('Ticket')
    rtype = 'attachment'
    role = 'subject'
