import unittest
import transaction

from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from zope.component import queryMultiAdapter, getUtility

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import setup as ptc_setup
from Products.PloneTestCase.layer import PloneSite
from plone.portlets.interfaces import IPortletType
try:
    from Products.PloneTestCase.version import PLONE40
    PLONE40 = PLONE40
except ImportError:
    PLONE40 = False

import quintagroup.analytics

ptc.setupPloneSite()


class Installed(PloneSite):

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml',
                         quintagroup.analytics)
        fiveconfigure.debug_mode = False
        ztc.installPackage('quintagroup.analytics')
        app = ztc.app()
        portal = app[ptc_setup.portal_name]

        # Sets the local site/manager
        ptc_setup._placefulSetUp(portal)

        qi = getattr(portal, 'portal_quickinstaller', None)
        qi.installProduct('quintagroup.analytics')
        transaction.commit()

    @classmethod
    def tearDown(cls):
        pass


class SetUpContent(Installed):

    max = 10
    types_ = ['Document', 'Event', 'Folder']
    users = [('user%s' % i, 'user%s' % i, 'Member', None)
             for i in xrange(max)]

    @classmethod
    def setupUsers(cls, portal):
        """ Creates users."""
        acl_users = portal.acl_users
        mp = portal.portal_membership
        map(acl_users._doAddUser, *zip(*cls.users))
        if not mp.memberareaCreationFlag:
            mp.setMemberareaCreationFlag()
        map(mp.createMemberArea, [u[0] for u in cls.users])

    @classmethod
    def setupContent(cls, portal):
        """ Creates test content."""
        uf = portal.acl_users
        pm = portal.portal_membership
        #portal.portal_catalog
        users = [u[0] for u in cls.users]
        for u in users:
            folder = pm.getHomeFolder(u)
            user = uf.getUserById(u)
            if not hasattr(user, 'aq_base'):
                user = user.__of__(uf)
            newSecurityManager(None, user)
            for i in xrange(users.index(u) + cls.max):
                map(folder.invokeFactory, cls.types_,
                    [t + str(i) for t in cls.types_])
        transaction.commit()

    @classmethod
    def setUp(cls):
        app = ztc.app()
        portal = app[ptc_setup.portal_name]
        cls.setupUsers(portal)
        cls.setupContent(portal)

    @classmethod
    def tearDown(cls):
        pass


class TestCase(ptc.PloneTestCase):
    layer = Installed


class TestQAInstallation(TestCase):
    """ This class veryfies registrations of all needed views and
        actions.
    """

    def test_cp_action_installation(self):
        """This test validates control panel action. """
        control_panel = self.portal.portal_controlpanel
        self.assert_(
                'QAnalytics' in [a.id for a in control_panel.listActions()],
                "Configlet for quintagroup.analitycs isn't registered.")

    def test_OwnershipByType(self):
        """ This test validates registration of
            ownership_by_type view.
        """
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="ownership_by_type")

        self.assert_(view, "Ownership by type view isn't registered")

    def test_OwnershipByState(self):
        """ This test validates registration of
            ownership_by_state view.
        """
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="ownership_by_state")

        self.assert_(view, "Ownership by state view isn't registered")

    def test_TypeByState(self):
        """ This test validates registration of
            type_by_state view.
        """
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="type_by_state")

        self.assert_(view, "Type by state view isn't registered")

    def test_LegacyPortlets(self):
        """ This test validates registration of
            legacy_portlets view.
        """
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="legacy_portlets")

        self.assert_(view, "Legacy Portlets view isn't registered")

    def test_PropertiesStats(self):
        """ This test validates registration of
            properties_stats view.
        """
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="properties_stats")

        self.assert_(view, "Properties Stats view isn't registered")

    def test_PortletsStats(self):
        """ This test validates registration of
            portlets_stats view.
        """
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="portlets_stats")

        self.assert_(view, "Portlets Stats view isn't registered")


class TestOwnershipByType(TestCase):
    """Tests all ownership by type view methods."""

    layer = SetUpContent

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="ownership_by_type")
        self.pc = self.portal.portal_catalog

    def test_getUsers(self):
        """ Tests method that returns ordered list of users."""
        users = [u[0] for u in self.layer.users]
        users.reverse()
        self.assert_(False not in map(lambda u1, u2: u1 == u2,
                     users, self.view.getUsers()))

    def test_getTypes(self):
        """ Tests method that returns ordered list of types."""
        data = {}
        index = self.pc._catalog.getIndex('portal_type')
        for k in index._index.keys():
            if not k:
                continue
            haslen = hasattr(index._index[k], '__len__')

            if haslen:
                data[k] = len(index._index[k])
            else:
                data[k] = 1

        data = data.items()
        data.sort(lambda a, b: a[1] - b[1])
        data.reverse()
        types = [i[0] for i in data]
        self.assert_(False not in map(lambda t1, t2: t1 == t2,
                     self.view.getTypes(), types))

    def test_getContent(self):
        """ This test verifies method that returns list of numbers.
            Each number is amount of specified content type objects
            that owned  by particular user.
        """
        # we need to login in to the site as Manager to be able to
        # see catalog results
        self.loginAsPortalOwner()

        for type_ in self.layer.types_:
            self.assert_(False not in \
            map(lambda i, j: i == j, [len(self.pc(portal_type=type_,
                                               Creator=user))
                                   for user in self.view.getUsers()],
                                  self.view.getContent(type_)))

    def test_getChart(self):
        """ This test verifies creation of chart image tag."""
        plone33chart_tag = \
            '<imgsrc="http://chart.apis.google.com/chart?chxt=y&amp;chds=0,'\
            '57&amp;chd=t:19.0,18.0,17.0,16.0,15.0,14.0,13.0,12.0,11.0,'\
            '10.0|19.0,18.0,17.0,16.0,15.0,14.0,13.0,12.0,11.0,10.0|'\
            '19.0,18.0,17.0,16.0,15.0,14.0,13.0,12.0,11.0,10.0|0.0,'\
            '0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0|0.0,0.0,0.0,0.0,'\
            '0.0,0.0,0.0,0.0,0.0,0.0&amp;chxr=0,0,57&amp;'\
            'chco=669933,cc9966,993300,ff6633,e8e4e3,a9a486,'\
            'dcb57e,ffcc99,996633,333300,00ff00&amp;'\
            'chl=user9|user8|user7|user6|user5|user4|user3|user2|user1|'\
            'user0&amp;chbh=a,10,0&amp;chs=800x375&amp;cht=bvs&amp;'\
            'chtt=Content+ownership+by+type&amp;chdl=Folder|Document|Event'\
            '|Large+Plone+Folder|Topic&amp;chdlp=b"/>'
        plone4chart_tag = \
            '<img src="http://chart.apis.google.com/chart?chxt=y&amp;'\
            'chds=0,57&amp;chd=t:19.0,18.0,17.0,16.0,15.0,14.0,'\
            '13.0,12.0,11.0,10.0|19.0,18.0,17.0,16.0,15.0,14.0,13.0,'\
            '12.0,11.0,10.0|19.0,18.0,17.0,16.0,15.0,14.0,13.0,12.0,'\
            '11.0,10.0|0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0&amp;'\
            'chxr=0,0,57&amp;chco=669933,cc9966,993300,ff6633,e8e4e3,'\
            'a9a486,dcb57e,ffcc99,996633,333300,00ff00&amp;chl=user9|'\
            'user8|user7|user6|user5|user4|user3|user2|user1|user0&amp;'\
            'chbh=a,10,0&amp;chs=800x375&amp;cht=bvs&amp;'\
            'chtt=Content+ownership+by+type&amp;chdl=Folder|Document|'\
            'Event|Topic&amp;chdlp=b" />'
        chart_tag = plone4chart_tag
        if not PLONE40:
            chart_tag = plone33chart_tag

        self.loginAsPortalOwner()
        self.assertEqual(*map(lambda s: ''.join(s.split()),
                              [chart_tag, self.view.getChart()]))


class TestOwnershipByState(TestCase):
    """Tests all ownership by state view methods."""

    layer = SetUpContent

    states = ['private', 'published', 'pending']

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="ownership_by_state")
        self.pc = self.portal.portal_catalog

    def test_getUsers(self):
        """ Tests method that returns ordered list of users."""
        users = [u[0] for u in self.layer.users]
        users.reverse()
        self.assert_(False not in map(lambda u1, u2: u1 == u2,
                     users, self.view.getUsers()))

    def test_getStates(self):
        """ Tests method that returns ordered list of states."""
        self.assert_(False not in map(lambda s1, s2: s1 == s2,
                     ['private', 'published'], self.view.getStates()))

    def test_getContent(self):
        """ This test verifies method that returns list of numbers.
            Each number is amount of specified content type objects
            that are in particular workflow state.
        """
        # we need to login in to the site as Manager to be able to
        # see catalog results
        self.loginAsPortalOwner()

        for state in self.states:
            self.assert_(False not in \
            map(lambda i, j: i == j, [len(self.pc(review_state=state,
                                              Creator=user))
                                  for user in self.view.getUsers()],
                                 self.view.getContent(state)))

    def test_getChart(self):
        """ This test verifies creation of chart image tag."""
        chart_tag = """<imgsrc="http://chart.apis.google.com/chart?chxt=y&amp;
                       chds=0,57&amp;chd=t:57.0,54.0,51.0,48.0,45.0,42.0,39.0,
                       36.0,33.0,30.0|0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                       0.0|0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0&amp;chxr=0,
                       0,57&amp;chco=669933,cc9966,993300,ff6633,e8e4e3,a9a486,
                       dcb57e,ffcc99,996633,333300,00ff00&amp;chl=user9|user8|
                       user7|user6|user5|user4|user3|user2|user1|user0&amp;
                       chbh=a,10,0&amp;chs=800x375&amp;cht=bvs&amp;
                       chtt=Content+ownership+by+state&amp;chdl=private|
                       published|No+workflow&amp;chdlp=b"/>"""
        self.loginAsPortalOwner()
        self.assertEqual(*map(lambda s: ''.join(s.split()),
                              [chart_tag, self.view.getChart()]))


class TestTypeByState(TestCase):
    """Tests all type_by_state view methods."""
    layer = SetUpContent
    states = ['private', 'published', 'pending']

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                 name="type_by_state")
        self.pc = self.portal.portal_catalog
        portal_migration = self.portal.portal_migration
        version = portal_migration.getFileSystemVersion()
        self.plone_version = version.replace(".", "")

    def test_getTypes(self):
        """ Tests method that returns ordered list of types."""
        index = self.pc._catalog.getIndex('portal_type')
        data = {}

        for k in index._index.keys():
            if not k:
                continue
            haslen = hasattr(index._index[k], '__len__')

            if haslen:
                data[k] = len(index._index[k])

            else:
                data[k] = 1
        data = data.items()
        data.sort(lambda a, b: a[1] - b[1])
        data.reverse()

        types = [i[0] for i in data]
        self.assert_(False not in map(lambda t1, t2: t1 == t2, types,
                                      self.view.getTypes()))

    def test_getStates(self):
        """ Tests method that returns ordered list of states."""
        self.assert_(False not in map(lambda s1, s2: s1 == s2,
                     ['private', 'published'], self.view.getStates()))

    def test_getContent(self):
        """ This test verifies method that returns list of numbers.
            Each number is amount of specified content type objects
            that owned  by particular user.
        """
        # we need to login in to the site as Manager to be able to
        # see catalog results
        self.loginAsPortalOwner()

        for state in self.states:
            self.assert_(False not in \
            map(lambda i, j: i == j, [len(self.pc(portal_type=type_,
                                               review_state=state))
                                   for type_ in self.view.getTypes()],
                                  self.view.getContent(state)))

    def test_getChart(self):
        """ This test verifies creation of chart image tag."""
        plone33chart_tag = \
            '<imgsrc="http://chart.apis.google.com/chart?chxt=y&amp;chds=0,'\
            '156&amp;chd=t:156.0,145.0,145.0,0.0,0.0|0.0,1.0,0.0,3.0,3.0|'\
            '0.0,0.0,0.0,0.0,0.0&amp;chxr=0,0,156&amp;chco=669933,cc9966,'\
            '993300,ff6633,e8e4e3,a9a486,dcb57e,ffcc99,996633,333300,'\
            '00ff00&amp;chl=Folder|Document|Event|Large+Plone+Folder|'\
            'Topic&amp;chbh=a,10,0&amp;chs=800x375&amp;cht=bvs&amp;'\
            'chtt=Content+type+by+state&amp;chdl=private|published|'\
            'No+workflow&amp;chdlp=b"/>'
        plone4chart_tag = \
            '<imgsrc="http://chart.apis.google.com/chart?chxt=y&amp;chds=0,'\
            '159&amp;chd=t:156.0,145.0,145.0,0.0|3.0,1.0,0.0,3.0|0.0,0.0,0.'\
            '0,0.0&amp;chxr=0,0,159&amp;chco=669933,cc9966,993300,ff6633,e8'\
            'e4e3,a9a486,dcb57e,ffcc99,996633,333300,00ff00&amp;chl=Folder|'\
            'Document|Event|Topic&amp;chbh=a,10,0&amp;chs=800x375&amp;cht=b'\
            'vs&amp;chtt=Content+type+by+state&amp;chdl=private|published|N'\
            'o+workflow&amp;chdlp=b"/>'
        plone41chart_tag = \
            '<imgsrc="http://chart.apis.google.com/chart?chxt=y&amp;chds=0,'\
            '159&amp;chd=t:156.0,145.0,145.0,0.0|3.0,1.0,0.0,2.0|0.0,0.0,0.'\
            '0,0.0&amp;chxr=0,0,159&amp;chco=669933,cc9966,993300,ff6633,e8'\
            'e4e3,a9a486,dcb57e,ffcc99,996633,333300,00ff00&amp;chl=Folder|'\
            'Document|Event|Topic&amp;chbh=a,10,0&amp;chs=800x375&amp;cht=b'\
            'vs&amp;chtt=Content+type+by+state&amp;chdl=private|published|N'\
            'o+workflow&amp;chdlp=b"/>'

        if self.plone_version < "40":
            chart_tag = plone33chart_tag
        elif self.plone_version > "41":
            chart_tag = plone41chart_tag
        else:
            chart_tag = plone4chart_tag

        self.loginAsPortalOwner()
        self.assertEqual(*map(lambda s: ''.join(s.split()),
                              [chart_tag, self.view.getChart()]))


class LegacyPortlets(TestCase):
    """Test all legasy_portlets view methods."""

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                       name='legacy_portlets')

    def test_getPortlets(self):
        """Tests method that returns portlets info."""

        # this is true for Plone 4
        self.assert_(self.view.getPortlets() == [])

    def test_getAllPortletExpressions(self):
        """Tests method that returns portlets expressions."""

        # this is true for Plone 4
        self.assert_(self.view.getAllPortletExpressions() == [])


class TestPropertiesStats(TestCase):
    """Tests all properties_stats view methods."""

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                       name='properties_stats')

    def test_getPropsList(self):
        self.view.propname = 'title'
        result = [u'Plone site', u'Welcome to Plone',
                  u'News', u'Events', u'Users']

        for title in result:
            self.assert_(title in [prop_info['slots']
                     for prop_info in self.view.getPropsList()])


class TestPortletsStats(TestCase):
    """Tests all properties_stats view methods."""

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                       name='portlets_stats')

    def test_getPropsList(self):
        """Tests method that collects portlet information from site."""

        self.loginAsPortalOwner()
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        mapping = \
          self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        mapping.restrictedTraverse('+/' + portlet.addview)()

        plone_portlets_info = filter(lambda info: info['path'] == '/plone',
                                     self.view.getPropsList())
        lslots = plone_portlets_info[0]['left_slots']
        self.assert_(info for info in lslots if info['title'] == 'Calendar')


def test_suite():
    test_suite = unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='quintagroup.contentstats',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='quintagroup.contentstats.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='quintagroup.contentstats',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='quintagroup.contentstats',
        #    test_class=TestCase),

        ])

    test_suite.addTest(unittest.makeSuite(TestQAInstallation))
    test_suite.addTest(unittest.makeSuite(TestOwnershipByType))
    test_suite.addTest(unittest.makeSuite(TestOwnershipByState))
    test_suite.addTest(unittest.makeSuite(TestTypeByState))
    test_suite.addTest(unittest.makeSuite(LegacyPortlets))
    test_suite.addTest(unittest.makeSuite(TestPropertiesStats))
    test_suite.addTest(unittest.makeSuite(TestPortletsStats))
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
