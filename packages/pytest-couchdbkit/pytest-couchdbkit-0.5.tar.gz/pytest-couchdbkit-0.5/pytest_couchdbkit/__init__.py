import pytest
from .dumper import dump_db
from .utils import server_from_config, dbname_from_config, \
        maybe_destroy_and_create

def pytest_addoption(parser):
    parser.addini('couchdbkit_backend', 'socketpool backend we should use', default='thread')
    parser.addini('couchdbkit_suffix', 'database name suffix')


def pytest_addhooks(pluginmanager):
    from . import hookspec
    pluginmanager.addhooks(hookspec)

def pytest_sessionstart(session):
    slaveinput = getattr(session.config, 'slaveinput', None)
    if slaveinput is not None:
        return
    try:
        dbname = dbname_from_config(session.config, 'pytest_%s_couchapp_source')
    except pytest.xfail.Exception:
        pass # we are not configured
    else:
        server = server_from_config(session.config)
        session.config.hook.pytest_couchdbkit_push_app(
                server=server,
                dbname=dbname)

def pytest_funcarg__couchdb_server(request):
    return server_from_config(request.config)


def pytest_funcarg__couchdb(request):
    server = request.getfuncargvalue('couchdb_server')
    tmpdir = request.getfuncargvalue('tmpdir')

    dbname = dbname_from_config(request.config, 'pytest_%s')
    db_source = dbname_from_config(request.config, 'pytest_%s_couchapp_source')
    slaveinput = getattr(request.config, 'slaveinput', None)
    if slaveinput is not None:
        dbname = '%s_%s' % (dbname, slaveinput['slaveid'])
    db = maybe_destroy_and_create(server, dbname)
    if db_source in server.all_dbs():
        server.replicate(db_source, dbname)
    
    def finalize_db():
        with tmpdir.join('couchdb.dump').open('w') as fp:
            dump_db(db, fp)
    request.addfinalizer(finalize_db)
    return db

