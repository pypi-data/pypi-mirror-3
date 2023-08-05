#!/usr/bin/python
# -*- coding: utf-8 -*-
from cubicweb.dbapi import in_memory_cnx
from cubicweb.cubicwebconfig import CubicWebConfiguration

from cubicweb.server.utils import manager_userpasswd


def auth_info(config):
    try:
        authinfo = config.sources()['admin']
    except KeyError:
        print 'login / password to use to connect to application %s' % config.appid
        login, pwd = manager_userpasswd()
        authinfo = {'login': login, 'password': pwd}
    return authinfo


class SiteImporter:
    def __init__(self, fromapp_cnx, toapp_cnx, fromapp_url=None):
        self.fromapp_cnx = fromapp_cnx
        self.fromapp_url = fromapp_url
        if self.fromapp_url and not self.fromapp_url[-1] == '/':
            self.fromapp_url += '/'
        self.toapp_cnx = toapp_cnx
        self.eid_map = {}
        self.fromapp_cu = fromapp_cnx.cursor()
        self.fromapp_isession = fromapp_cnx._repo.internal_session()
        self.toapp_cu = toapp_cnx.cursor()
        self.toapp_session = toapp_cnx._repo._sessions[toapp_cnx.sessionid]
        self.schema = self.toapp_cnx.get_schema()

    def fromapp_execute(self, *args):
        self.fromapp_cu.execute(*args)

    def toapp_execute(self, *args):
        try:
            self.toapp_cu.execute(*args)
        except Exception, exc:
            print exc
            r = raw_input('continue ? [y/N]')
            if r.upper() != 'Y':
                raise

    def deactivate_hooks(self):
        # load here since modules have been reloaded
        from cubicweb.sobjects.notification import StatusChangeHook, RelationChangeHook, EntityChangeHook
        from cubicweb.sobjects.supervising import SomethingChangedHook, EntityDeleteHook
        from cubes.jpl.sobjects.hooks import ProjectAddedHook, InVersionChangeHook, BeforeStatusChangeHook
        for subevents in self.toapp_cnx._repo.hm._hooks.itervalues():
            for callbacks in subevents.itervalues():
                for cb in callbacks[:]:
                    if hasattr(cb, 'im_self') and \
                           isinstance(cb.im_self, (StatusChangeHook, RelationChangeHook, EntityChangeHook,
                                                   SomethingChangedHook, EntityDeleteHook,
                                                   ProjectAddedHook, InVersionChangeHook, BeforeStatusChangeHook)):
                        callbacks.remove(cb)
                    else:
                        try:
                            cls = cb.im_self.__class__
                            assert cls is getattr(sys.modules[cls.__module__], cls.__name__), cls
                        except AttributeError:
                            pass
        
    def insert_entity(self, etype, origentity=None, where=None, extraargs=None, objrels=(), **kwargs):
        relations = []
        kwargs.pop('eid', None)
        for key in kwargs:
            if self.schema.rschema(key).is_final():
                relations.append('X %s %%(%s)s' % (key, key))
            else:
                relations.append('X %s %s' % (key, kwargs[key]))
                assert where
        for objrel, var in objrels:
            relations.append('%s %s X' % (var, objrel))
        rql = 'INSERT %s X: %s' % (etype, ','.join(relations))
        if where:
            rql = '%s WHERE %s' % (rql, where)
            kwargs.update(extraargs)
            rset = self.toapp_execute(rql, kwargs, extraargs.keys())
        else:
            rset = self.toapp_execute(rql, kwargs)
        eid = rset[0][0]
        if origentity is not None:
            self.eid_map[origentity.eid] = eid
	    try:
   	        self.toapp_execute('SET X created_by U WHERE X eid %(x)s, U login %(l)s',
	                              {'x': eid, 'l': origentity.created_by[0].login}, 'x')
            except IndexError:
	        pass
        return eid

    def copy_users(self):
        isession = self.fromapp_isession
        toapp_session = self.toapp_session
        users_group = self.toapp_execute('CWGroup X WHERE X name "users"')[0][0]
        for euser in self.fromapp_execute('Any X,L,F,S WHERE X login L, X surname S, X firstname F').entities():
            # skip external (ldap) users
            if euser.metainformation()['source']['uri'] != 'system' or euser.login == 'admin' or euser.login.endswith('_old'):
                print '* skip user', euser.login, euser.metainformation()['source']['uri']
                continue
            print '* copy user', euser.login
            args = dict(euser)
            args['upassword'] = 'dummy'
            # XXX user already imported from another site
            eid = self.insert_entity('CWUser', euser, **args)
            # retreive crypted password using an internal session
            pwd = isession.execute('Any P WHERE X upassword P, X eid %(x)s', {'x': euser.eid}, 'x')[0][0]
            # and set it using sql to avoid reencryption
            toapp_session.system_sql('UPDATE CWUser SET upassword=%(pwd)s WHERE eid=%(eid)s',
                                     {'pwd': pwd.getvalue(), 'eid': eid})
            # set group
            self.toapp_execute('SET X in_group G WHERE X eid %(x)s, G eid %(g)s',
                               {'x': eid, 'g': users_group}, 'x')
            # copy email
            for email in euser.primary_email:
                print '* copy primary email', email.address
                self.insert_entity('EmailAddress', email,
                                   where='U eid %(u)s', extraargs={'u': eid},
                                   objrels=(('primary_email', 'U'),),
                                   alias=email.alias, address=email.address,
                                   canonical=email.canonical)
            for email in euser.use_email:
                # skip primary email
                if email.eid in self.eid_map:
                    continue
                print '* copy secondary email', email.address
                self.insert_entity('EmailAddress', email,
                                   where='U eid %(u)s', extraargs={'u': eid},
                                   objrels=(('use_email', 'U'),),
                                   alias=email.alias, address=email.address, canonical=email.canonical)
                
    def copy_extprojects(self):
        for project in self.fromapp_execute('Any X,N,U,DF,D WHERE X is ExtProject, X name N, X url U, '
                                               'X description_format DF, X description D').entities():
            print '* copy extproject', project.name
            self.insert_entity('ExtProject', project, **dict(project))
            
    def copy_files_and_images(self):
        for file in self.fromapp_execute('Any X,DA,DAF,DAE,N,DF,D WHERE X data DA, X data_format DAF, '
                                            'X data_encoding DAE, X name N, '
                                            'X description_format DF, X description D').entities():
            print '* copy file', file.name
            self.insert_entity(file.id, file, **dict(file))

    def copy_cards(self):
        for card in self.fromapp_execute('Any X,T,S,CF,C,W WHERE X title T, X synopsis S, '
                                            'X content_format CF, X content C, X wikiid W').entities():
            if card.wikiid in ('help', 'index'):
                continue
            print '* copy card', card.title
            self.insert_entity('Card', card, **dict(card))

    def copy_projects(self):
        for project in self.fromapp_execute('Any X,N,S,U,VU,RU,DU,DF,D WHERE X name N, X summary S, '
                                               'X url U, X vcsurl VU, X reporturl RU, X downloadurl DU, '
                                               'X description_format DF, X description D').entities():
            print '* copy project', project.name
            eid = self.insert_entity('Project', project, **dict(project))
            imported_permission = False
            # set users in related groups with related permissions
            for permission in self.fromapp_execute('Any P WHERE X require_permission P, X eid %(x)s',
                                                      {'x': project.eid}, 'x').entities():
                if permission.eid in self.eid_map:
                    self.toapp_execute('SET X require_permission P WHERE X eid %(x)s, P eid %(p)s',
                                       {'x': eid, 'p': self.eid_map[permission.eid]})
                    continue
                if not imported_permission:
                    shortname = project.name[:56] # group name limited to 64 characters
                    geid = self.insert_entity('CWGroup', name=u'%s clients'%shortname)
                    peid = self.insert_entity('CWPermission', permission,
                                              where='G eid %(g)s', extraargs={'g': geid},
                                              require_group='G', name=u'client', label=u'%s clients'%shortname)
                    self.toapp_execute('SET X require_permission P WHERE X eid %(x)s, P eid %(p)s',
                                       {'x': eid, 'p': peid})
                    imported_permission = True
                for group in permission.require_group:
                    for euser in group.reverse_in_group:
                        try:
                            self.toapp_execute('SET U in_group G WHERE U eid %(u)s, G eid %(g)s, NOT U in_group G',
                                               {'u': self.eid_map[euser.eid], 'g': geid})
                            print '* grant client permission to', euser.login
                        except KeyError:
                            print 'duh', euser.login
            # interested_in
            for euser in project.reverse_interested_in:
                try:
                    self.toapp_execute('SET U interested_in X WHERE X eid %(x)s, U eid %(u)s',
                                       {'x': eid, 'u': self.eid_map[euser.eid]}, 'x')
                    print '* mark interest to', euser.login
                except KeyError:
                    # external user
                    self.toapp_execute('SET U interested_in X WHERE X eid %(x)s, U login %(l)s',
                                       {'x': eid, 'l': euser.login}, 'x')
                    continue
        # secondary relations
        for rtype in ('uses', 'recommends', 'documented_by', 'screenshot'):
            for p1eid, p2eid in self.fromapp_execute('Any P1, P2 WHERE P1 %s P2' % rtype):
                self.toapp_execute('SET P1 %s P2 WHERE P1 eid %%(p1)s, P2 eid %%(p2)s' % rtype,
                                   {'p1': self.eid_map[p1eid], 'p2': self.eid_map[p2eid]})

    def copy_versions(self):
        for version in self.fromapp_execute('Any X,P,S,SN,N,DF,D,STD,PRD,PUD,CRD,MOD '
                                               'WHERE X num N, X version_of P, X in_state S, S name SN, '
                                               'X description_format DF, X description D, '
                                               'X starting_date STD, X prevision_date PRD, '
                                               'X publication_date PUD, X creation_date CRD, '
                                               'X modification_date MOD').entities():
            print '* copy version', version.num
            args = dict(version)
            peid = self.eid_map[version.project.eid]
            args['version_of'] = 'P'
            eid = self.insert_entity('Version', version, where='P eid %(p)s',
                                     extraargs={'p': peid}, **args)
            # workflow state
            self.toapp_execute('SET X in_state S WHERE X eid %(x)s, S name %(sn)s',
                               {'x': eid, 'sn': version.state}, 'x')
            # todo_by
            for euser in version.todo_by:
                self.toapp_execute('SET V todo_by U WHERE V eid %(x)s, U login %(l)s',
                                   {'x': eid, 'l': euser.login}, 'x')
        # secondary relations
        for rtype in ('conflicts', 'depends_on'):
            for v1eid, v2eid in self.fromapp_execute('Any V1, V2 WHERE V1 %s V2, V1 is Version' % rtype):
                self.toapp_execute('SET V1 %s V2 WHERE V1 eid %%(v1)s, V2 eid %%(v2)s' % rtype,
                                   {'v1': self.eid_map[v1eid], 'v2': self.eid_map[v2eid]})

    def copy_tickets(self):
        for ticket in self.fromapp_execute('Any X,P,V,S,SN,T,TY,PR,L,LF,D,DF,CRD,MOD '
                                              'WHERE X concerns P, X done_in V?, X in_state S, S name SN, '
                                              'X title T, X type TY, X priority PR, X load L, X load_left LF,'
                                              'X description_format DF, X description D, '
                                              'X creation_date CRD, X modification_date MOD').entities():
            print '* copy ticket', ticket.title
            args = dict(ticket)
            extra = {'p': self.eid_map[ticket.project.eid]}
            args['concerns'] = 'P'
            where = 'P eid %(p)s'
            if ticket.done_in:
                extra['v'] = self.eid_map[ticket.done_in[0].eid]
                args['done_in'] = 'V'
                where += ', V eid %(v)s'
            eid = self.insert_entity('Ticket', ticket, where=where,
                                     extraargs=extra, **args)
            # workflow state
            self.toapp_execute('SET X in_state S WHERE X eid %(x)s, S name %(sn)s',
                               {'x': eid, 'sn': ticket.state}, 'x')
            # set a comment on tickets to remember its old reference
            if self.fromapp_url is None:
                comment = u'ancien eid de ce ticket: #%s' % ticket.eid
            else:
                comment = u'ancienne référence de ce ticket: %sticket/%s' % (self.fromapp_url, ticket.eid)
            self.toapp_execute('INSERT Comment C: C content %(c)s, C comments X WHERE X eid %(x)s',
                               {'x': eid, 'c': comment}, 'x')
        # identical_to (symetric)
        found = set()        
        for teid1, teid2 in self.fromapp_execute('Any T1,T2 WHERE T1 identical_to T2'):
            if (teid2, teid1) in found:
                # symetric
                continue
            found.add((teid1, teid2))
            self.toapp_execute('SET T1 identical_to T2 WHERE T1 eid %(t1)s, T2 eid %(t2)s',
                               {'t1': self.eid_map[teid1], 't2': self.eid_map[teid2]}, ('t1', 't2'))
        # secondary relations
        for rtype in ('appeared_in', 'attachment', 'depends_on'):
            for teid, xeid in self.fromapp_execute('Any T, X WHERE T %s X' % rtype):
                self.toapp_execute('SET T %s X WHERE T eid %%(t)s, X eid %%(x)s' % rtype,
                                   {'t': self.eid_map[teid], 'x': self.eid_map[xeid]}, 'x')
            
    def copy_comments(self):
        # first level comments
        found = []
        for comment in self.fromapp_execute('Any C,X,CCF,CC,CRD,MOD WHERE C comments X, NOT X is Comment, '
                                            'C content_format CCF, C content CC, '
                                            'C creation_date CRD, C modification_date MOD').entities():
            args = dict(comment)
            args['comments'] = 'T'
            try:
                self.insert_entity('Comment', comment, where='T eid %(t)s',
                                   extraargs={'t': self.eid_map[comment.comments[0].eid]}, **args)
                print '* copy comment', comment.eid
                found.append(comment.eid)
            except KeyError:
                print 'W: found comment %s on a not backported entity %s' % (comment.eid, comment.comments[0].eid)
        # answers
        while found:
            eids = ','.join(str(ceid) for ceid in found)
            found = []
            for comment in self.fromapp_execute('Any C,X,CCF,CC,CRD,MOD WHERE C comments X, X eid IN(%s), '
                                                'C content_format CCF, C content CC,'
                                                'C creation_date CRD, C modification_date MOD'% eids).entities():
                print '* copy comment', comment.eid
                args = dict(comment)
                args['comments'] = 'C'
                self.insert_entity('Comment', comment, where='C eid %(c)s',
                                   extraargs={'c': self.eid_map[comment.comments[0].eid]}, **args)
                found.append(comment.eid)

    def copy_see_also(self):
        found = set()
        for xeid1, xeid2 in self.fromapp_execute('Any X1, X2 WHERE X1 see_also X2'):
            if (xeid2, xeid1) in found:
                # symetric
                continue
            found.add((xeid1, xeid2))
            try:
                self.toapp_execute('SET X1 see_also X2 WHERE X1 eid %(x1)s, X2 eid %(x2)s',
                                   {'x1': self.eid_map[xeid1], 'x2': self.eid_map[xeid2]}, ('x1', 'x2'))
            except KeyError:
                print 'W: found see_also on a not backported entity (either %s or %s or both)' % (xeid1, xeid2)

    def copy_tags(self):
        existing_tags = set(tn for tn, in self.toapp_execute('Any TN WHERE T is Tag, T name TN'))
        for x, tn in self.fromapp_execute('Any X,TN WHERE T tags X, T name TN'):
            if not tn in existing_tags:
                print 'inserting tag', tn
                self.toapp_execute('INSERT Tag X: X name %(tn)s', {'tn': tn})
                existing_tags.add(tn)
            try:
                self.toapp_execute('SET T tags X WHERE X eid %(x)s, T name %(tn)s',
                              {'x': self.eid_map[x], 'tn': tn}, 'x')
            except KeyError:
                pass
            
    def import_site(self):
        try:
            self.deactivate_hooks()
            print 'copying users'
            self.copy_users()
            print 'copying files and images'
            self.copy_files_and_images()
            print 'copying cards'
            self.copy_cards()
            print 'copying external projects'
            self.copy_extprojects()
            print 'copying projects'
            self.copy_projects()
            print 'copying versions'
            self.copy_versions()
            print 'copying tickets'
            self.copy_tickets()
            print 'copying comments'
            self.copy_comments()
            print 'copying tags'
            self.copy_tags()
            print 'copying see also'
            self.copy_see_also()
            print 'commit...'
            self.toapp_cnx.commit()
            # not copied: workflow history, folder, mailing list, license, test instances[, blog, link]
        finally:
            self.fromapp_cnx.close()
            self.toapp_cnx.close()
        
def import_site(fromappid, toappid, fromapp_url=None):
    CubicWebConfiguration.load_cubicwebctl_plugins()
    fromapp_cfg = CubicWebConfiguration.config_for(fromappid)
    toapp_cfg = CubicWebConfiguration.config_for(toappid)
    fromapp_authinfo = auth_info(fromapp_cfg)
    # use an in-memory connection to be able to retreive passwords
    fromapp_cnx = in_memory_cnx(fromapp_cfg, fromapp_authinfo['login'],
                                fromapp_authinfo['password'])[1]
    toapp_authinfo = auth_info(toapp_cfg)
    # use an in-memory connection to be able to set passwords
    toapp_cnx = in_memory_cnx(toapp_cfg, toapp_authinfo['login'],
                              toapp_authinfo['password'])[1]
    # reload objects from the first connection since toapp_cnx has
    # reloaded vobjects modules
    fromapp_cnx.load_vobjects(force_reload=False)
    toapp_cnx.load_vobjects(force_reload=False, subpath=('entities', 'views', 'sobjects'))
    importer = SiteImporter(fromapp_cnx, toapp_cnx, fromapp_url)
    importer.import_site()
    print '%s entities imported' % len(importer.eid_map)


if __name__ == '__main__':
    import sys
    if not 2 < len(sys.argv) < 5:
        print 'usage: import_site <fromapp id> <toapp id> [<fromapp url>]'
        sys.exit(1)
    try:
        import_site(*sys.argv[1:])
    except UnicodeError, exc:
        print exc
        print 'Try with LC_ALL=fr_FR.UTF-8'
