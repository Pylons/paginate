""""Test paginate module."""
import sys
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import eq_, raises
from webob.multidict import MultiDict

import paginate


def test_empty_list():
    """Test whether an empty list is handled correctly."""
    items = []
    page = paginate.Page(items, page=0)
    assert page.page == 0
    assert page.first_item is None
    assert page.last_item is None
    assert page.first_page is None
    assert page.last_page is None
    assert page.previous_page is None
    assert page.next_page is None
    assert page.items_per_page == 20
    assert page.item_count == 0
    assert page.page_count == 0
    assert page.pager() == ''
    assert page.pager(show_if_single_page=True) == ''

def test_one_page():
    """Test that we fit 10 items on a single 10-item page."""
    items = range(10)
    page = paginate.Page(items, page=0, items_per_page=10)
    assert page.page == 1
    assert page.first_item == 1
    assert page.last_item == 10
    assert page.first_page == 1
    assert page.last_page == 1
    assert page.previous_page is None
    assert page.next_page is None
    assert page.items_per_page == 10
    assert page.item_count == 10
    assert page.page_count == 1
    assert page.pager() == ''
    assert page.pager(show_if_single_page=True) == '<span class="pager_curpage">1</span>'

def url_generator(**kw):
    #return update_params("/content", **kw)
    # XXX
    return "foo"

def test_many_pages():
    """Test that 100 items fit on seven 15-item pages."""
    items = range(100)
    page = paginate.Page(items, page=0, items_per_page=15, url=url_generator)
    eq_(page.page, 1)
    eq_(page.first_item, 1)
    eq_(page.last_item, 15)
    eq_(page.first_page, 1)
    eq_(page.last_page, 7)
    assert page.previous_page is None
    eq_(page.next_page, 2)
    eq_(page.items_per_page, 15)
    eq_(page.item_count, 100)
    eq_(page.page_count, 7)
    eq_(page.pager(), '<span class="pager_curpage">1</span> <a class="pager_link" href="/content?page=2">2</a> <a class="pager_link" href="/content?page=3">3</a> <span class="pager_dotdot">..</span> <a class="pager_link" href="/content?page=7">7</a>')
    eq_(page.pager(separator='_'), '<span class="pager_curpage">1</span>_<a class="pager_link" href="/content?page=2">2</a>_<a class="pager_link" href="/content?page=3">3</a>_<span class="pager_dotdot">..</span>_<a class="pager_link" href="/content?page=7">7</a>')
    eq_(page.pager(page_param='xy'), '<span class="pager_curpage">1</span> <a class="pager_link" href="/content?xy=2">2</a> <a class="pager_link" href="/content?xy=3">3</a> <span class="pager_dotdot">..</span> <a class="pager_link" href="/content?xy=7">7</a>')
    eq_(page.pager(link_attr={'style':'s1'}, curpage_attr={'style':'s2'}, dotdot_attr={'style':'s3'}), '<span style="s2">1</span> <a href="/content?page=2" style="s1">2</a> <a href="/content?page=3" style="s1">3</a> <span style="s3">..</span> <a href="/content?page=7" style="s1">7</a>')
    eq_(page.pager(onclick="empty"), '<span class="pager_curpage">1</span> <a class="pager_link" href="/content?page=2" onclick="empty">2</a> <a class="pager_link" href="/content?page=3" onclick="empty">3</a> <span class="pager_dotdot">..</span> <a class="pager_link" href="/content?page=7" onclick="empty">7</a>')
    eq_(page.pager(onclick="load('$page')"), '<span class="pager_curpage">1</span> <a class="pager_link" href="/content?page=2" onclick="load(&#39;2&#39;)">2</a> <a class="pager_link" href="/content?page=3" onclick="load(&#39;3&#39;)">3</a> <span class="pager_dotdot">..</span> <a class="pager_link" href="/content?page=7" onclick="load(&#39;7&#39;)">7</a>')
    if not sys.platform.startswith('java'):
        # XXX: these assume dict ordering
        eq_(page.pager(onclick="load('%s')"), '<span class="pager_curpage">1</span> <a class="pager_link" href="/content?page=2" onclick="load(&#39;/content?partial=1&amp;page=2&#39;)">2</a> <a class="pager_link" href="/content?page=3" onclick="load(&#39;/content?partial=1&amp;page=3&#39;)">3</a> <span class="pager_dotdot">..</span> <a class="pager_link" href="/content?page=7" onclick="load(&#39;/content?partial=1&amp;page=7&#39;)">7</a>')
        eq_(page.pager(onclick="load('$partial_url')"), '<span class="pager_curpage">1</span> <a class="pager_link" href="/content?page=2" onclick="load(&#39;/content?partial=1&amp;page=2&#39;)">2</a> <a class="pager_link" href="/content?page=3" onclick="load(&#39;/content?partial=1&amp;page=3&#39;)">3</a> <span class="pager_dotdot">..</span> <a class="pager_link" href="/content?page=7" onclick="load(&#39;/content?partial=1&amp;page=7&#39;)">7</a>')

def test_make_page_url():
    purl = paginate.make_page_url("/articles", {}, 2)
    eq_(purl, "/articles?page=2")
    purl = paginate.make_page_url("/articles", {"foo": "bar"}, 2)
    eq_(purl, "/articles?foo=bar&page=2")
    params = {"foo": "bar", "page": "1"}
    purl = paginate.make_page_url("/articles", params, 2)
    eq_(purl, "/articles?foo=bar&page=2")
    params = MultiDict({"foo": "bar", "page": "1"})
    params.add("foo", "bar2")
    purl = paginate.make_page_url("/articles", params, 2)
    eq_(purl, "/articles?foo=bar&foo=bar2&page=2")

def test_pageurl():
    purl = paginate.PageURL("/articles", {})
    eq_(purl(2), "/articles?page=2")
    purl = paginate.PageURL("/articles", {"foo": "bar"})
    eq_(purl(2), "/articles?foo=bar&page=2")
    params = {"foo": "bar", "page": "1"}
    purl = paginate.PageURL("/articles", params)
    eq_(purl(2), "/articles?foo=bar&page=2")

class DummyRequest(object):
    """A fake ``webob.Request`` for test_pageurl_webob``."""
    def __init__(self, application_url, path, GET):
        self.application_url = application_url
        self.path = path
        self.GET = GET

def test_pageurl_webob():
    path = "/articles"
    application_url = "http://localhost:5000" + path
    params = MultiDict({"blah": "boo"})
    request = DummyRequest(application_url, path, params)
    purl = paginate.PageURL_WebOb(request)
    eq_(purl(2), "/articles?blah=boo&page=2")
    purl = paginate.PageURL_WebOb(request, qualified=True)
    eq_(purl(2), "http://localhost:5000/articles?blah=boo&page=2")


class UnsliceableSequence(object):
   def __init__(self, seq):
      self.l = seq
   
   def __iter__(self):
       for i in self.l:
           yield i

   def __len__(self):
       return len(self.l)


class UnsliceableSequence2(UnsliceableSequence):
   def __getitem__(self, key):
        raise TypeError("unhashable type")

class TestCollectionTypes(unittest.TestCase):
    rng = list(range(10))   # A list in both Python 2 and 3.

    def test_list(self):
        paginate.Page(self.rng)

    def test_tuple(self):
        paginate.Page(tuple(self.rng))

    @raises(TypeError)
    def test_unsliceable_sequence(self):
        paginate.Page(UnsliceableSequence(self.rng))

    @raises(TypeError)
    def test_unsliceable_sequence2(self):
        paginate.Page(UnsliceableSequence2(self.rng))


class TestSQLAlchemyCollectionTypes(unittest.TestCase):
    def setUp(self):
        try:
            import sqlalchemy as sa
            import sqlalchemy.orm as orm
        except ImportError:
            raise SkipTest()
        self.engine = engine = sa.create_engine("sqlite://") # Memory database
        self.sessionmaker = orm.sessionmaker(bind=engine)
        self.metadata = metadata = sa.MetaData(bind=engine)
        self.notes = notes = sa.Table("Notes", metadata,
            sa.Column("id", sa.Integer, primary_key=True))
        class Note(object):
            pass
        self.Note = Note
        notes.create()
        orm.mapper(Note, notes)
        insert = notes.insert()
        records = [{"id": x} for x in range(1, 101)]
        engine.execute(insert, records)
            
    def tearDown(self):
        import sqlalchemy as sa
        import sqlalchemy.orm as orm
        orm.clear_mappers()
        self.notes.drop()

    def test_sqlalchemy_orm(self):
        session = self.sessionmaker()
        q = session.query(self.Note).order_by(self.Note.id)
        page = paginate.Page(q)
        records = list(page)
        eq_(records[0].id, 1)
        eq_(records[-1].id, 20)

