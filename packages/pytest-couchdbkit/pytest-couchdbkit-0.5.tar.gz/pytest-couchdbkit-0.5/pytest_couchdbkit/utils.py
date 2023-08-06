import pytest

def server_from_config(config):
    from couchdbkit import Server
    backend = config.getini('couchdbkit_backend') or 'thread'
    return Server(backend=backend)

def dbname_from_config(config, fmt):
    suffix = config.getini('couchdbkit_suffix')
    if not suffix:
        pytest.xfail('no couchdbkit_suffix set in ini')
    return fmt % (suffix,)


def maybe_destroy_and_create(server, dbname):
    if dbname in server.all_dbs():
        server.delete_db(dbname)
    return server.create_db(dbname)
