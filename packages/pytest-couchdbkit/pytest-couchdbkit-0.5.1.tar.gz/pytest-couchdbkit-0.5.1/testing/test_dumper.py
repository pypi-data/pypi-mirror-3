
from pytest_couchdbkit.dumper import items, dump_db, load_dump
from io import BytesIO

def test_items_simple(couchdb):
    
    empty = list(items(couchdb))
    assert empty == []

    doc = {'_id': 'test'}
    couchdb.save_doc(doc)

    first = list(items(couchdb))
    assert len(first) == 1
    assert first[0] == doc


    couchdb.put_attachment(doc, 'data', name='foo.py')

    first_attach = list(items(couchdb))
    adoc, data = first_attach
    assert adoc == doc
    assert data == 'data'


def test_ddoc(couchdb):
    ddoc = {'_id': '_design/test'}
    couchdb.save_doc(ddoc)
    ddocs = list(items(couchdb))
    assert ddocs == [ddoc]

def test_dump_load(couchdb):
    assert couchdb.info()['doc_count'] == 0
    doc = {'_id': 'test'}
    couchdb.save_doc(doc)
    assert couchdb.info()['doc_count'] == 1
    couchdb.put_attachment(doc, 'test a', name='a.py')
    couchdb.put_attachment(doc, 'test b', name='b.py')
    io = BytesIO()
    dump_db(couchdb, io)
    couchdb.server.delete_db(couchdb.dbname)
    couchdb.server.create_db(couchdb.dbname)
    assert couchdb.info()['doc_count'] == 0
    io.seek(0)
    load_dump(io, couchdb)

    assert couchdb.info()['doc_count'] == 1
    assert couchdb.fetch_attachment('test', 'a.py') == 'test a'
    assert couchdb.fetch_attachment('test', 'b.py') == 'test b'
