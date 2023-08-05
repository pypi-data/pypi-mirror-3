"""jpl application'schema

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import RelationDefinition

class repository_branch(RelationDefinition):
    subject = 'Version'
    object = 'String'
    description = _('repository branch matching this version')
