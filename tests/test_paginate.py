""""Test paginate module."""
import sys
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import eq_, raises

import paginate

# TODO: test Page(dict(one=1)) -> TypeError: Your collection of type <class 'dict'> cannot be handled by paginate.

# pager()        link_attr={'class':'pager_link'}, curpage_attr={'class':'pager_curpage'},
#   dotdot_attr={'class':'pager_dotdot'},


def test_make_html_tag1():
    """Test the HTML tag generator with a SPAN tag."""
    tag = paginate.make_html_tag('span',style='green')
    assert tag == '<span style="green">'

def test_make_html_tag2():
    """Test the HTML tag generator with an A tag."""
    tag = paginate.make_html_tag('a',href='http://example.org/')
    assert tag == '<a href="http://example.org/">'

def test_make_html_tag3():
    """Test the HTML tag generator with a CSS-classed DIV tag."""
    tag = paginate.make_html_tag('div', _class='red', id='maindiv')
    assert tag == '<div class="red" id="maindiv">'



def test_empty_list():
    """Test whether an empty list is handled correctly."""
    items = []
    page = paginate.Page(items, page=0)
    eq_(page.page, 0)
    eq_(page.first_item, None)
    eq_(page.last_item, None)
    eq_(page.first_page, None)
    eq_(page.last_page, None)
    eq_(page.previous_page, None)
    eq_(page.next_page, None)
    eq_(page.items_per_page, 20)
    eq_(page.item_count, 0)
    eq_(page.page_count, 0)
    eq_(page.pager(url="http://example.org/page=$page"), '')
    eq_(page.pager(url="http://example.org/page=$page", show_if_single_page=True), '')

def test_one_page():
    """Test that fits 10 items on a single 10-item page."""
    items = range(10)
    page = paginate.Page(items, page=0, items_per_page=10)
    url = "http://example.org/foo/page=$page"
    eq_(page.page, 1)
    eq_(page.first_item, 1)
    eq_(page.last_item, 10)
    eq_(page.first_page, 1)
    eq_(page.last_page, 1)
    eq_(page.previous_page, None)
    eq_(page.next_page, None)
    eq_(page.items_per_page, 10)
    eq_(page.item_count, 10)
    eq_(page.page_count, 1)
    eq_(page.pager(url=url), '')
    eq_(page.pager(url=url, show_if_single_page=True), '1')

def test_many_pages():
    """Test that fits 100 items on seven pages consisting of 15 items."""
    items = range(100)
    page = paginate.Page(items, page=0, items_per_page=15)
    url = "http://example.org/foo/page=$page"
    eq_(page.collection_type, range)
    eq_(page.page, 1)
    eq_(page.first_item, 1)
    eq_(page.last_item, 15)
    eq_(page.first_page, 1)
    eq_(page.last_page, 7)
    eq_(page.previous_page, None)
    eq_(page.next_page, 2)
    eq_(page.items_per_page, 15)
    eq_(page.item_count, 100)
    eq_(page.page_count, 7)
    eq_(page.pager(url=url), '1 <a href="http://example.org/foo/page=2">2</a> <a href="http://example.org/foo/page=3">3</a> .. <a href="http://example.org/foo/page=7">7</a>')
    eq_(page.pager(url=url, separator='_'), '1_<a href="http://example.org/foo/page=2">2</a>_<a href="http://example.org/foo/page=3">3</a>_.._<a href="http://example.org/foo/page=7">7</a>')
    eq_(page.pager(url=url, link_attr={'style':'linkstyle'}, curpage_attr={'style':'curpagestyle'}, dotdot_attr={'style':'dotdotstyle'}),
        '<span style="curpagestyle">1</span> <a style="linkstyle" href="http://example.org/foo/page=2">2</a> <a style="linkstyle" href="http://example.org/foo/page=3">3</a> <span style="dotdotstyle">..</span> <a style="linkstyle" href="http://example.org/foo/page=7">7</a>')

def test_make_html_tag():
    """Test the make_html_tag() function"""
    eq_(paginate.make_html_tag('div'), '<div>')
    eq_(paginate.make_html_tag('a',href="/another/page"), '<a href="/another/page">')
    eq_(paginate.make_html_tag('a',href="/another/page",text="foo"), '<a href="/another/page">foo</a>')
    eq_(paginate.make_html_tag('a',href="/another/page",text="foo",onclick="$('#mydiv').focus();"), """<a href="/another/page" onclick="$('#mydiv').focus();">foo</a>""")

#def test_make_page_url():
#    purl = paginate.make_page_url("/articles", {}, 2)
#    eq_(purl, "/articles?page=2")
#    purl = paginate.make_page_url("/articles", {"foo": "bar"}, 2)
#    eq_(purl, "/articles?foo=bar&page=2")
#    params = {"foo": "bar", "page": "1"}
#    purl = paginate.make_page_url("/articles", params, 2)
#    eq_(purl, "/articles?foo=bar&page=2")

#def test_pageurl():
#    purl = paginate.PageURL("/articles", {})
#    eq_(purl(2), "/articles?page=2")
#    purl = paginate.PageURL("/articles", {"foo": "bar"})
#    eq_(purl(2), "/articles?foo=bar&page=2")
#    params = {"foo": "bar", "page": "1"}
#    purl = paginate.PageURL("/articles", params)
#    eq_(purl(2), "/articles?foo=bar&page=2")
#
#class DummyRequest(object):
#    """A fake ``webob.Request`` for test_pageurl_webob``."""
#    def __init__(self, application_url, path, GET):
#        self.application_url = application_url
#        self.path = path
#        self.GET = GET
#
#def test_pageurl_webob():
#    pass
    #path = "/articles"
    #application_url = "http://localhost:5000" + path
    #params = MultiDict({"blah": "boo"})
    #request = DummyRequest(application_url, path, params)
    #purl = paginate.PageURL_WebOb(request)
    #eq_(purl(2), "/articles?blah=boo&page=2")
    #purl = paginate.PageURL_WebOb(request, qualified=True)
    #eq_(purl(2), "http://localhost:5000/articles?blah=boo&page=2")


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

