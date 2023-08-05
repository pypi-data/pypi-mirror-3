"""install some monkey patches to ease API"""

from __future__ import with_statement

from logilab.common.decorators import monkeypatch

from cubicweb import schema


schema.INTERNAL_TYPES.add('CWPermission')
schema.SYSTEM_RTYPES.add('require_group')
schema.SYSTEM_RTYPES.add('require_permission')
schema.SYSTEM_RTYPES.add('has_group_permission')
schema.NO_I18NCONTEXT.add('require_permission')


try:
    from cubicweb.server import repository, session
except ImportError:
    pass
else:
    # cubicweb-server configuration / monkey-patching

    repository.NO_CACHE_RELATIONS.add( ('require_permission', 'object') )

    @monkeypatch(session.InternalManager, 'has_permission')
    @staticmethod
    def has_permission(self, pname, contexteid=None):
        return True


try:
    from cubicweb import devtools
    from cubicweb.devtools import testlib
except ImportError:
    pass
else:
    # cubicweb-dev configuration / monkey-patching

    @monkeypatch(testlib.CubicWebTC, 'grant_permission')
    @staticmethod
    def grant_permission(session, entity, group, pname=None, plabel=None):
        """insert a permission on an entity. Will have to commit the main
        connection to be considered
        """
        pname = unicode(pname)
        plabel = plabel and unicode(plabel) or unicode(group)
        e = getattr(entity, 'eid', entity)
        with session.security_enabled(False, False):
            peid = session.execute(
            'INSERT CWPermission X: X name %(pname)s, X label %(plabel)s,'
            'X require_group G, E require_permission X '
            'WHERE G name %(group)s, E eid %(e)s',
            locals())[0][0]
        return peid

    devtools.SYSTEM_ENTITIES.add('CWPermission')
    devtools.SYSTEM_RELATIONS.add('require_group')
    devtools.SYSTEM_RELATIONS.add('require_permission')
