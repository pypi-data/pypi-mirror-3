"""some non regression tests"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import CubicWebTC


class JPLNonRegressionTC(CubicWebTC):

    def setup_database(self):
	self.request().create_entity('Project', name=u'cubicweb', description=u"cubicweb c'est beau")

    def test_js_filter_generated_query(self):
        peid, seid = self.execute('Any P, S WHERE P is Project, S name "open"')[0]
        self.execute('''
Any B,(NOW - CD),PR,S,C,V,GROUP_CONCAT(TN)
GROUPBY B, CD, PR, S, C, V, VN ORDERBY S, VN, PR
WHERE B is Ticket, B creation_date CD, B load C, B done_in V?, V num VN,
B concerns P, P eid %s, T name TN,B priority PR, S eid IN(%s),B in_state S,T? tags B
''' % (peid, seid))

if __name__ == '__main__':
    unittest_main()
