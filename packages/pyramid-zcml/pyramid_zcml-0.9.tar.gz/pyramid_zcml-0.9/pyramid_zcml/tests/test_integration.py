import os
import unittest

class IntegrationBase(unittest.TestCase):
    root_factory = None
    def setUp(self):
        from pyramid_zcml import includeme
        from pyramid.config import Configurator
        config = Configurator(root_factory=self.root_factory)
        config.include(includeme)
        config.begin()
        config.load_zcml(self.config)
        config.commit()
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

class TestFixtureApp(IntegrationBase):
    config = 'pyramid_zcml.tests.fixtureapp:configure.zcml'
    def test_another(self):
        res = self.testapp.get('/another.html', status=200)
        self.assertEqual(res.body, 'fixture')

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.body, 'fixture')

    def test_dummyskin(self):
        self.testapp.get('/dummyskin.html', status=404)

    def test_error(self):
        res = self.testapp.get('/error.html', status=200)
        self.assertEqual(res.body, 'supressed')

    def test_protected(self):
        self.testapp.get('/protected.html', status=403)

class TestCCBug(IntegrationBase):
    # "unordered" as reported in IRC by author of
    # http://labs.creativecommons.org/2010/01/13/cc-engine-and-web-non-frameworks/
    config = 'pyramid_zcml.tests.ccbugapp:configure.zcml'
    def test_rdf(self):
        res = self.testapp.get('/licenses/1/v1/rdf', status=200)
        self.assertEqual(res.body, 'rdf')

    def test_juri(self):
        res = self.testapp.get('/licenses/1/v1/juri', status=200)
        self.assertEqual(res.body, 'juri')

class TestHybridApp(IntegrationBase):
    # make sure views registered for a route "win" over views registered
    # without one, even though the context of the non-route view may
    # be more specific than the route view.
    config = 'pyramid_zcml.tests.hybridapp:configure.zcml'
    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.body, 'global')

    def test_abc(self):
        res = self.testapp.get('/abc', status=200)
        self.assertEqual(res.body, 'route')

    def test_def(self):
        res = self.testapp.get('/def', status=200)
        self.assertEqual(res.body, 'route2')

    def test_ghi(self):
        res = self.testapp.get('/ghi', status=200)
        self.assertEqual(res.body, 'global')

    def test_jkl(self):
        self.testapp.get('/jkl', status=404)

    def test_mno(self):
        self.testapp.get('/mno', status=404)

    def test_pqr_global2(self):
        res = self.testapp.get('/pqr/global2', status=200)
        self.assertEqual(res.body, 'global2')

    def test_error(self):
        res = self.testapp.get('/error', status=200)
        self.assertEqual(res.body, 'supressed')

    def test_error2(self):
        res = self.testapp.get('/error2', status=200)
        self.assertEqual(res.body, 'supressed2')

    def test_error_sub(self):
        res = self.testapp.get('/error_sub', status=200)
        self.assertEqual(res.body, 'supressed2')

class TestRestBugApp(IntegrationBase):
    # test bug reported by delijati 2010/2/3 (http://pastebin.com/d4cc15515)
    config = 'pyramid_zcml.tests.restbugapp:configure.zcml'
    def test_it(self):
        res = self.testapp.get('/pet', status=200)
        self.assertEqual(res.body, 'gotten')

class TestViewDecoratorApp(IntegrationBase):
    config = 'pyramid_zcml.tests.viewdecoratorapp:configure.zcml'
    def _configure_mako(self):
        tmpldir = os.path.join(os.path.dirname(__file__), 'viewdecoratorapp',
                               'views')
        self.config.registry.settings['mako.directories'] = tmpldir

    def test_first(self):
        # we use mako here instead of chameleon because it works on Jython
        self._configure_mako()
        res = self.testapp.get('/first', status=200)
        self.failUnless('OK' in res.body)

    def test_second(self):
        # we use mako here instead of chameleon because it works on Jython
        self._configure_mako()
        res = self.testapp.get('/second', status=200)
        self.failUnless('OK2' in res.body)

class TestViewPermissionBug(IntegrationBase):
    # view_execution_permitted bug as reported by Shane at http://lists.repoze.org/pipermail/repoze-dev/2010-October/003603.html
    config = 'pyramid_zcml.tests.permbugapp:configure.zcml'
    def test_test(self):
        res = self.testapp.get('/test', status=200)
        self.failUnless('ACLDenied' in res.body)

    def test_x(self):
        self.testapp.get('/x', status=403)

class TestDefaultViewPermissionBug(IntegrationBase):
    # default_view_permission bug as reported by Wiggy at http://lists.repoze.org/pipermail/repoze-dev/2010-October/003602.html
    config = 'pyramid_zcml.tests.defpermbugapp:configure.zcml'
    def test_x(self):
        res = self.testapp.get('/x', status=403)
        self.failUnless('failed permission check' in res.body)

    def test_y(self):
        res = self.testapp.get('/y', status=403)
        self.failUnless('failed permission check' in res.body)

    def test_z(self):
        res = self.testapp.get('/z', status=200)
        self.failUnless('public' in res.body)

from pyramid_zcml.tests.exceptionviewapp.models import AnException
from pyramid_zcml.tests.exceptionviewapp.models import NotAnException

excroot = {'anexception':AnException(),
           'notanexception':NotAnException()}

class TestExceptionViewsApp(IntegrationBase):
    config = 'pyramid_zcml.tests.exceptionviewapp:configure.zcml'
    root_factory = lambda *arg: excroot
    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('maybe' in res.body)

    def test_notanexception(self):
        res = self.testapp.get('/notanexception', status=200)
        self.failUnless('no' in res.body)

    def test_anexception(self):
        res = self.testapp.get('/anexception', status=200)
        self.failUnless('yes' in res.body)

    def test_route_raise_exception(self):
        res = self.testapp.get('/route_raise_exception', status=200)
        self.failUnless('yes' in res.body)

    def test_route_raise_exception2(self):
        res = self.testapp.get('/route_raise_exception2', status=200)
        self.failUnless('yes' in res.body)

    def test_route_raise_exception3(self):
        res = self.testapp.get('/route_raise_exception3', status=200)
        self.failUnless('whoa' in res.body)

    def test_route_raise_exception4(self):
        res = self.testapp.get('/route_raise_exception4', status=200)
        self.failUnless('whoa' in res.body)

class TestIncludeOverrideApp(unittest.TestCase):
    config = 'pyramid_zcml.tests.includeoverrideapp:configure.zcml'
    def test_it(self):
        # see http://www.mail-archive.com/zope-dev@zope.org/msg35171.html
        # for an explanation of why load_zcml of includeoverrideapp's
        # configure.zcml should raise a ConfigurationConflictError
        try: # pragma: no cover
            from pyramid.exceptions import ConfigurationConflictError
        except ImportError: # pragma: no cover
            from zope.configuration.config import ConfigurationConflictError
        from pyramid_zcml import includeme
        from pyramid.config import Configurator
        config = Configurator()
        config.include(includeme)
        config.load_zcml(self.config)
        self.assertRaises(ConfigurationConflictError, config.make_wsgi_app)
