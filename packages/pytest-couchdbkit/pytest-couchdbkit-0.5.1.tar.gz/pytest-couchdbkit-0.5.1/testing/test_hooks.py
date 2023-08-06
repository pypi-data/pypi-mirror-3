import pytest_couchdbkit
from pytest_couchdbkit.utils import maybe_destroy_and_create
import couchdbkit
import mock

settings = {'couchdbkit_suffix': 'test', 'couchdbkit_backend': 'thread'}

def funcargs(name, request):
    if name == 'couchdb_server':
        return couchdbkit.Server()
    print 'get funcarg', name
    return getattr(request, name)

def pytest_funcarg__request(request):
    tmpdir = request.getfuncargvalue('tmpdir')
    request = mock.MagicMock()
    request.config.getini.side_effect = settings.get
    request.getfuncargvalue.side_effect = lambda name: funcargs(name, request)
    request.tmpdir = tmpdir
    request.config.slaveinput = None
    return request


def test_server_funcarg(request):
    server = pytest_couchdbkit.pytest_funcarg__couchdb_server(request)
    print server.info()

def test_database_dumping(request, tmpdir):
    db = pytest_couchdbkit.pytest_funcarg__couchdb(request)
    assert db.dbname == 'pytest_test'
    print db.info()
    db.save_doc({'_id': 'test'}, force_update=True)
    finalizer = request.addfinalizer.call_args[0][0]
    assert not tmpdir.join('couchdb.dump').check()
    finalizer()
    assert tmpdir.join('couchdb.dump').check()

def test_database_on_slavenode(request):
    request.config.slaveinput = {'slaveid': 'gw1'}
    db = pytest_couchdbkit.pytest_funcarg__couchdb(request)
    assert 'gw1' in db.dbname


def test_sessionstart_handles_missing_dbconfig_gracefull():
    session = mock.Mock()
    session.config.getini.side_effect = {}.get
    pytest_couchdbkit.pytest_sessionstart(session)


def test_sessionstart_with_config_calls_hook():
    settings = {'couchdbkit_suffix': 'test'}
    session = mock.Mock()
    session.config.getini.side_effect = settings.get
    session.config.slaveinput = None
    pytest_couchdbkit.pytest_sessionstart(session)
    call_args = session.config.hook.pytest_couchdbkit_push_app.call_args
    assert call_args[1]['dbname'] == 'pytest_test_couchapp_source'


def test_sessionstart_on_slave_does_nothing():
    settings = {'couchdbkit_suffix':'test'}
    session = mock.Mock()
    session.config.getini.side_effect = settings.get
    session.config.slaveinput = {'slaveid': 'gw1'}
    
    pytest_couchdbkit.pytest_sessionstart(session)
    hook = session.config.hook.pytest_couchdbkit_push_app
    assert not hook.called



def test_replication(request, tmpdir):
    server = pytest_couchdbkit.pytest_funcarg__couchdb_server(request)
    db_source = maybe_destroy_and_create(server, 'pytest_test_couchapp_source')
    db_source.save_doc({'_id': 'test'})


    db = pytest_couchdbkit.pytest_funcarg__couchdb(request)
    assert 'test' in db

