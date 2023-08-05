"""jpl web user interface

:organization: Logilab
:copyright: 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import match_transition, is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import workflow, autoform

from cubes.tracker.views import forms as trackerforms

uicfg.primaryview_section.tag_attribute(('Version', 'repository_branch'), 'hidden')
uicfg.autoform_section.tag_attribute(('Version', 'repository_branch'), 'main', 'hidden')

def branches_for_version_choices(form, field, **kwargs):
    try:
        version = form.edited_entity
        env = version.project.has_apycot_environment[0]
        branches = env.repository.branches()
        return [(b, b) for b in branches]
    except:
        return []

uicfg.autoform_field_kwargs.tag_attribute(('Version', 'repository_branch'),
                                          {'choices': branches_for_version_choices})

def version_is_linked_to_local_repo(version):
    try:
        return bool(version.project.has_apycot_environment[0].repository)
    except:
        return False


class VersionChangeStateForm(workflow.ChangeStateForm):
    __select__ = is_instance('Version') & match_transition('ready')

    repository_branch = autoform.etype_relation_field('Version', 'repository_branch')
