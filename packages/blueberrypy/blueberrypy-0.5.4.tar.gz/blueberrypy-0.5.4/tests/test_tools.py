import unittest

if not hasattr(unittest.TestCase, "assertIn"):
    import unittest2 as unittest

try:
    import simplejson as json
except ImportError:
    import json

import cherrypy
from cherrypy import HTTPError, HTTPRedirect, InternalRedirect
from cherrypy.test import helper

from sqlalchemy import Column, Integer, Unicode, engine_from_config
from sqlalchemy.ext.declarative import declarative_base

from testconfig import config as testconfig

from blueberrypy.plugins import SQLAlchemyPlugin
from blueberrypy.tools import MultiHookPointTool, SQLAlchemySessionTool


def get_config(section_name):
    return dict([(str(k), v) for k, v in testconfig[section_name].iteritems()])

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(128), nullable=False, unique=True)


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, autoincrement=True, primary_key=True)
    address = Column(Unicode(128), nullable=False, unique=True)


class MultiHookPointToolTest(helper.CPWebCase, unittest.TestCase):

    @staticmethod
    def setup_server():

        class TestMultiHookPointTool(MultiHookPointTool):

            def on_start_resource(self, param=None):
                req = cherrypy.request
                req.on_start_resource_param = param

            def before_request_body(self, param=None):
                req = cherrypy.request
                req.before_request_body_param = param

            def before_handler(self, param=None):
                req = cherrypy.request
                req.before_handler_param = param

            def before_finalize(self, param=None):
                resp = cherrypy.response
                resp.headers['x-before-finalize'] = param

            def on_end_resource(self, param=None):
                resp = cherrypy.response
                resp.header_list += ('x-on-end-resource', str(param)),

            def before_error_response(self, param=None):
                resp = cherrypy.response
                resp.headers['x-before-error-response'] = param

            def after_error_response(self, param=None):
                resp = cherrypy.response
                resp.headers['x-after-error-response'] = param

            def on_end_request(self, param=None):
                MultiHookPointToolTest.on_end_request_param = param

        class Root(object):

            _cp_config = {"tools.test_multi_hook_point.on": True}

            @cherrypy.expose
            def success(self):
                req = cherrypy.request
                return str(req.on_start_resource_param | req.before_request_body_param | req.before_handler_param)
            success._cp_config = {"tools.test_multi_hook_point.on_start_resource.param": 1,
                                  "tools.test_multi_hook_point.before_request_body.param": 2,
                                  "tools.test_multi_hook_point.before_handler.param": 4,
                                  "tools.test_multi_hook_point.before_finalize.param": 11,
                                  "tools.test_multi_hook_point.on_end_resource.param": 13,
                                  "tools.test_multi_hook_point.on_end_request.param": 19}

            @cherrypy.expose
            def failure(self):
                return 1 / 0
            failure._cp_config = {"tools.test_multi_hook_point.before_error_response.param": 7,
                                  "tools.test_multi_hook_point.after_error_response.param": 8}

        cherrypy.tools.test_multi_hook_point = TestMultiHookPointTool()
        cherrypy.tree.mount(Root())

    def test_success(self):
        self.getPage("/success")
        self.assertInBody(str(7))
        self.assertHeader("x-before-finalize", 11)
        self.assertHeader("x-on-end-resource", 13)
        self.assertEqual(MultiHookPointToolTest.on_end_request_param, 19)

    def test_failure(self):
        self.getPage("/failure")
        self.assertHeader("x-before-error-response", 7)
        self.assertHeader("x-after-error-response", 8)


class SQLAlchemySessionToolSingleEngineTest(helper.CPWebCase, unittest.TestCase):

    engine = engine_from_config(get_config('sqlalchemy_engine'), '')

    @classmethod
    def setup_class(cls):

        super(SQLAlchemySessionToolSingleEngineTest, cls).setup_class()

        Base.metadata.create_all(cls.engine)
    setUpClass = setup_class

    @classmethod
    def teardown_class(cls):

        super(SQLAlchemySessionToolSingleEngineTest, cls).teardown_class()

        Base.metadata.drop_all(cls.engine)
    tearDownClass = teardown_class

    @staticmethod
    def setup_server():
        class SingleEngine(object):

            _cp_config = {'tools.orm_session.on': True}

            def save_user_and_address(self):
                session = cherrypy.request.orm_session
                bob = User(name=u"joey")
                session.add(bob)
                hk = Address(address=u"United States")
                session.add(hk)
                session.commit()
            save_user_and_address.exposed = True

            def query_user(self):
                session = cherrypy.request.orm_session
                joey = session.query(User).filter_by(name=u'joey').one()
                assert isinstance(joey.name, unicode)
                return json.dumps({'id': joey.id, 'name': joey.name})
            query_user.exposed = True

            def query_addresss(self):
                session = cherrypy.request.orm_session
                us = session.query(Address).filter_by(address=u'United States').one()
                assert isinstance(us.address, unicode)
                return json.dumps({'id': us.id, 'address': us.address})
            query_addresss.exposed = True

            def raise_not_passable_exception_save(self):
                session = cherrypy.request.orm_session
                bob = User(name=u"bob")
                session.add(bob)
                raise ValueError
            raise_not_passable_exception_save.exposed = True

            def raise_not_passable_exception_query(self):
                session = cherrypy.request.orm_session
                bob = session.query(User).filter_by(name=u'bob').first()
                return json.dumps(None)
            raise_not_passable_exception_query.exposed = True

            def raise_passable_exception_save(self):
                session = cherrypy.request.orm_session
                bob = User(name=u"bob")
                session.add(bob)
                session.commit()
                raise HTTPRedirect('/')
            raise_passable_exception_save.exposed = True

            def raise_passable_exception_query(self):
                session = cherrypy.request.orm_session
                bob = session.query(User).filter_by(name=u'bob').first()
                return json.dumps({'id': bob.id, 'name': bob.name})
            raise_passable_exception_query.exposed = True

        cherrypy.engine.sqlalchemy = SQLAlchemyPlugin(cherrypy.engine, testconfig)
        cherrypy.tools.orm_session = SQLAlchemySessionTool()
        cherrypy.config.update({'engine.sqlalchemy.on': True})
        cherrypy.tree.mount(SingleEngine())

    def test_orm_session_tool_commit(self):
        self.getPage('/save_user_and_address')
        self.assertStatus(200)

    def test_orm_session_tool_query_user(self):
        self.getPage('/query_user')
        json_resp = json.loads(self.body)
        self.assertIn('id', json_resp)
        self.assertIn('name', json_resp)
        self.assertEqual(u'joey', json_resp['name'])
        self.assertStatus(200)

    def test_orm_session_tool_query_address(self):
        self.getPage('/query_addresss')
        json_body = json.loads(self.body)
        self.assertIn('id', json_body)
        self.assertIn('address', json_body)
        self.assertEqual(u'United States', json_body['address'])
        self.assertStatus(200)

    def test_raise_not_passable_exception(self):
        self.getPage('/raise_not_passable_exception_save')
        self.assertStatus(500)
        self.getPage('/raise_not_passable_exception_query')
        self.assertBody(json.dumps(None))
        self.assertStatus(200)

    def test_raise_passable_exception(self):
        self.getPage('/raise_passable_exception_save')
        self.assertStatus(303)
        self.getPage('/raise_passable_exception_query')
        json_resp = json.loads(self.body)
        self.assertIn('id', json_resp)
        self.assertIn('name', json_resp)
        self.assertEqual(u'bob', json_resp['name'])
        self.assertStatus(200)


class SQLAlchemySessionToolTwoPhaseTest(helper.CPWebCase, unittest.TestCase):

    # only used for setup and teardown
    engine_bindings = {User: engine_from_config(get_config('sqlalchemy_engine_tests.test_tools.User'), ''),
                       Address: engine_from_config(get_config('sqlalchemy_engine_tests.test_tools.Address'), '')}

    @classmethod
    def setup_class(cls):

        super(SQLAlchemySessionToolTwoPhaseTest, cls).setup_class()

        User.metadata.create_all(cls.engine_bindings[User])
        Address.metadata.create_all(cls.engine_bindings[Address])
    setUpClass = setup_class

    @classmethod
    def teardown_class(cls):

        super(SQLAlchemySessionToolTwoPhaseTest, cls).teardown_class()

        User.metadata.create_all(cls.engine_bindings[User])
        Address.metadata.create_all(cls.engine_bindings[Address])
    tearDownClass = teardown_class

    @staticmethod
    def setup_server():

        class TwoPhase(object):

            _cp_config = {'tools.orm_session.on': True}

            def save_user_and_address(self):
                session = cherrypy.request.orm_session
                alice = User(name=u"alice")
                session.add(alice)
                hk = Address(address=u"Hong Kong")
                session.add(hk)
                session.commit()
            save_user_and_address.exposed = True
            save_user_and_address._cp_config = {'tools.orm_session.bindings': [User, Address]}

            def query_user(self):
                session = cherrypy.request.orm_session
                alice = session.query(User).filter_by(name=u'alice').one()
                assert isinstance(alice.name, unicode)
                return json.dumps({'id': alice.id, 'name': alice.name})
            query_user.exposed = True
            query_user._cp_config = {'tools.orm_session.bindings': [User]}

            def query_addresss(self):
                session = cherrypy.request.orm_session
                hk = session.query(Address).filter_by(address=u'Hong Kong').one()
                assert isinstance(hk.address, unicode)
                return json.dumps({'id': hk.id, 'address': hk.address})
            query_addresss.exposed = True
            query_addresss._cp_config = {'tools.orm_session.bindings': [Address]}

            def raise_not_passable_exception_save(self):
                session = cherrypy.request.orm_session
                katy = User(name=u"katy")
                session.add(katy)
                raise HTTPError(400)
            raise_not_passable_exception_save.exposed = True
            raise_not_passable_exception_save._cp_config = {'tools.orm_session.bindings': [User]}

            def raise_not_passable_exception_query(self):
                session = cherrypy.request.orm_session
                katy = session.query(User).filter_by(name=u'katy').first()
                if katy is not None:
                    return json.dumps({'id': katy.id, 'name': katy.name})
                else:
                    return json.dumps(None)
            raise_not_passable_exception_query.exposed = True
            raise_not_passable_exception_query._cp_config = {'tools.orm_session.bindings': [User]}

            def raise_passable_exception_save(self):
                session = cherrypy.request.orm_session
                david = User(name=u"david")
                session.add(david)
                session.commit()
                raise HTTPRedirect('/')
            raise_passable_exception_save.exposed = True
            raise_passable_exception_save._cp_config = {'tools.orm_session.bindings': [User]}

            def raise_passable_exception_query(self):
                session = cherrypy.request.orm_session
                david = session.query(User).filter_by(name=u'david').first()
                return json.dumps({'id': david.id, 'name': david.name})
            raise_passable_exception_query.exposed = True
            raise_passable_exception_query._cp_config = {'tools.orm_session.bindings': [User]}

        cherrypy.engine.sqlalchemy = SQLAlchemyPlugin(cherrypy.engine, testconfig)
        cherrypy.tools.orm_session = SQLAlchemySessionTool()
        cherrypy.config.update({'engine.sqlalchemy.on': True})
        cherrypy.tree.mount(TwoPhase())

    def test_orm_session_tool_commit(self):
        self.getPage('/save_user_and_address')
        self.assertStatus(200)

    def test_orm_session_tool_query_user(self):
        self.getPage('/query_user')
        json_resp = json.loads(self.body)
        self.assertIn('id', json_resp)
        self.assertIn('name', json_resp)
        self.assertEqual(u'alice', json_resp['name'])
        self.assertStatus(200)

    def test_orm_session_tool_query_address(self):
        self.getPage('/query_addresss')
        json_body = json.loads(self.body)
        self.assertIn('id', json_body)
        self.assertIn('address', json_body)
        self.assertEqual(u'Hong Kong', json_body['address'])
        self.assertStatus(200)

    def test_raise_not_passable_exception(self):
        self.getPage('/raise_not_passable_exception_save')
        self.assertStatus(400)
        self.getPage('/raise_not_passable_exception_query')
        self.assertBody(json.dumps(None))
        self.assertStatus(200)

    def test_raise_passable_exception(self):
        self.getPage('/raise_passable_exception_save')
        self.assertStatus(303)
        self.getPage('/raise_passable_exception_query')
        json_resp = json.loads(self.body)
        self.assertIn('id', json_resp)
        self.assertIn('name', json_resp)
        self.assertEqual(u'david', json_resp['name'])
        self.assertStatus(200)
