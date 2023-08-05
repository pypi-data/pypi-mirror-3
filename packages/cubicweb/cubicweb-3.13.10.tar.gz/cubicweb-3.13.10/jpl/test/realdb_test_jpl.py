from cubicweb.devtools import buildconfig, loadconfig
from cubicweb.devtools.testlib import RealDBTest

def setup_module(options):
    if options.source:
        configcls = loadconfig(options.source)
    elif options.dbname is None:
        raise Exception('either <sourccubes.file> or <dbname> options are required')
    else:
        configcls = buildconfig(options.dbuser, options.dbpassword,
                                               options.dbname, options.euser,
                                               options.epassword)
    RealDatabaseTC.configcls = configcls
    

class RealDatabaseTC(RealDBTest):
    configcls = None # set by setup_module()
    
    def test_all_primaries(self):
        etypes = None # ('Ticket',)
        for rset in self.iter_individual_rsets(limit=50, etypes=etypes):
            yield self.view, 'primary', rset, rset.req.reset_headers()
            yield self.view, 'oneline', rset, rset.req.reset_headers()
    
    def test_startup_views(self):
        for vid in self.list_startup_views():
            req = self.request()
            yield self.view, vid, None, req


    def test_foo(self):
        rset = self.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertEquals(len(rset), 1)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
