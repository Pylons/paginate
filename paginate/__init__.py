"""
paginate: helps split up large collections into individual pages
================================================================

What is pagination?
---------------------

This module helps split large lists of items into pages. The user is shown one page at a time and
can navigate to other pages. Imagine you are offering a company phonebook and let the user search
the entries. The search result may contains 23 entries but you want to display no more than 10
entries at once. The first page contains entries 1-10, the second 11-20 and the third 21-23. See the
documentation of the "Page" class for more information.

How do I use it?
------------------

A page of items is represented by the *Page* object. A *Page* gets initialized with these arguments:

- The collection of items to pick a range from. Usually just a list.
- The page number we want to display. Default is 1: the first page.
- Optional: A URL generator callback. If you are using this module for a web application
  you will want to offer your user a list of pages with links that lead to other pages.
  This link list can be created using the Page.pager() method.
  This module comes with a little logic that tries to create or alter a *page* parameter
  if you pass a URL. For example if you provide the URL "http://yourapplication/phonebook/$page"
  then for the third page it will create "http://yourapplication/phonebook/3".

Now we can create a collection and instantiate the Page::

    # Create a sample collection of 1000 items
    >>> my_collection = range(1000)

    # Create a Page object for the 3rd page (20 items per page is the default)
    >>> my_page = Page(my_collection, page=3, url=url_for_page)

    # The page object can be printed directly to get its details
    >>> my_page
    Page:
    Collection type:  <type 'list'>
    Current page:     3
    First item:       41
    Last item:        60
    First page:       1
    Last page:        50
    Previous page:    2
    Next page:        4
    Items per page:   20
    Number of items:  1000
    Number of pages:  50
    <BLANKLINE>

    # Print a list of items on the current page
    >>> my_page.items
    [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]

    # The *Page* object can be used as an iterator:
    >>> for my_item in my_page: print my_item,
    40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59

    # The .pager() method returns an HTML fragment with links to surrounding
    # pages.
    # [The ">>" prompt is to hide untestable examples from doctest.]
    >> my_page.pager()
    1 2 [3] 4 5 .. 50       (this is actually HTML)

    # The pager can be customized:
    >> my_page.pager('$link_previous ~3~ $link_next (Page $page of $page_count)')
    1 2 [3] 4 5 6 .. 50 > (Page 3 of 50)

There are many parameters that customize the Page's behavor. See the
documentation on ``Page`` and ``Page.pager()``.

URL generator
-------------

The constructor's ``url`` argument is a callback that returns URLs to other pages. It's required
when using the ``Page.pager()`` method except under Pylons, where it will fall back to
``pylons.url.current`` (Pylons 1) and then ``routes.url_for`` (Pylons 0.9.7). If none of these are
available, you'll get an exception "NotImplementedError: no URL generator available".

WebHelpers 1.3 introduces a few URL generators for convenience. **PageURL** is described above.
**PageURL_WebOb** takes a ``webobb.Request`` object, and is suitable for Pyramid, Pylons,
TurboGears, and other frameworks that have a WebOb-compatible Request object. Both of these classes
assume that the page number is in the 'page' query parameter.

This overrides the 'page' path variable, while leaving the 'id' variable and the query string
intact.

The callback API is simple. 

1. It must accept an integer argument 'page', which will be passed by name.

2. It should return the URL for that page.  

3. If you're using AJAX 'partial' functionality described in the ``Page.pager``
   docstring, the callback should also accept a 'partial' argument and, if true, set a query
   parameter 'partial=1'.

4. If you use the 'page_param' or 'partial_param' argument to ``Page.pager``,
   the 'page' and 'partial' arguments will be renamed to whatever you specify. In this case, the
   callback would also have to expect these other argument names.

The supplied classes adhere to this API in their ``.__call__`` method, all except the fourth
condition. So you can use their instances as callbacks as long as you don't use 'page_param' or
'partial_param'.

For convenience in writing callbacks that update the 'page' query parameter, a ``make_page_url``
function is available that assembles the pieces into a complete URL. Other callbacks may find
``webhelpers.utl.update_params`` useful, which overrides query parameters on a more general basis.


Can I use AJAX / AJAH?
------------------------

Yes. See *partial_param* and *onclick* in ``Page.pager()``.

Notes
-------

Page numbers and item numbers start at 1. This concept has been used because users expect that the
first page has number 1 and the first item on a page also has number 1. So if you want to use the
page's items by their index number please note that you have to subtract 1.

This module is based on the code from http://workaround.org/cgi-bin/hg-paginate that is known at the
"Paginate" module on PyPI. It was written by Christoph Haas <email@christoph-haas.de>, and modified
by Christoph Haas and Mike Orr for WebHelpers. (c) 2007-2011. """

import re
from string import Template
import urllib
import cgi
import warnings

def get_wrapper(obj):
    """
    Auto-detect the kind of object and return a list/tuple
    to access items from the collection.
    """
    # If object is iterable we can use it.  (This is not true if it's
    # non-sliceable but there doesn't appear to be a way to test for that. We'd
    # have to call .__getitem__ with a slice and guess what the exception
    # means, and calling it may cause side effects.)
    required_methods = ["__iter__", "__len__", "__getitem__"]
    for meth in required_methods:
        if not hasattr(obj, meth):
            raise TypeError(INCOMPATIBLE_COLLECTION_TYPE)

    return obj


# Since the items on a page are mainly a list we subclass the "list" type
class Page(list):
    """A list/iterator of items representing one page in a larger collection.

    An instance of the "Page" class is created from a _collection_ which is any
    list-like object that allows random access to its elements. You can just use a list.
    
    The instance works as an iterator running from the first item to the 
    last item on the given page. The collection can be:

    A "Page" instance maintains pagination logic associated with each 
    page, where it begins, what the first/last item on the page is, etc. 
    The pager() method creates a link list allowing the user to go to
    other pages.

    **WARNING:** Unless you pass in an item_count, a count will be 
    performed on the collection every time a Page instance is created. 

    Instance attributes:

    original_collection
        Points to the collection object being paged through

    item_count
        Number of items in the collection

    page
        Number of the current page

    items_per_page
        Maximal number of items displayed on a page

    first_page
        Number of the first page - starts with 1

    last_page
        Number of the last page

    page_count
        Number of pages

    items
        Sequence/iterator of items on the current page

    first_item
        Index of first item on the current page - starts with 1

    last_item
        Index of last item on the current page
        
    """
    def __init__(self, collection, page=1, items_per_page=20, item_count=None, url=None, **kwargs):
        """Create a "Page" instance.

        Parameters:

        collection
            Sequence representing the collection of items to page through.

        page
            The requested page number - starts with 1. Default: 1.

        items_per_page
            The maximal number of items to be displayed per page.
            Default: 20.

        item_count (optional)
            The total number of items in the collection - if known.
            If this parameter is not given then the paginator will count
            the number of elements in the collection every time a "Page"
            is created. Giving this parameter will speed up things.
        
        url (optional)
            The URL of the page currently shown to the user.
            This is used only by ``.pager()``.

        Further keyword arguments are used as link arguments in the pager().
        """
        # URL generation is now done within this module. So tell the developer
        # that passing a URL generation function is deprecated. Instead a string
        # URL is expected.
        #if hasattr(url, '__call__'):
        #    warnings.warn("""Passing URL generators as the 'url' parameter is no longer
        #            supported. Please pass the current URL as a string instead.""")
        #    self.url = url()
        #else:
        #    self.url = url

        # Safe the kwargs class-wide so they can be used in the pager() method
        self.kwargs = kwargs

        # Save a reference to the collection
        self.original_collection = collection

        # Decorate the ORM/sequence object with __getitem__ and __len__
        # functions to be able to get slices.
        if collection is not None:
            # Determine the type of collection and use a wrapper for ORMs
            self.collection = collection
        else:
            self.collection = []

        self.collection_type = type(collection)

        # The self.page is the number of the current page.
        # The first page has the number 1!
        try:
            self.page = int(page) # make it int() if we get it as a string
        except (ValueError, TypeError):
            self.page = 1

        self.items_per_page = items_per_page

        # Unless the user tells us how many items the collections has
        # we calculate that ourselves.
        if item_count is not None:
            self.item_count = item_count
        else:
            self.item_count = len(self.collection)

        # Compute the number of the first and last available page
        if self.item_count > 0:
            self.first_page = 1
            self.page_count = ((self.item_count - 1) // self.items_per_page) + 1
            self.last_page = self.first_page + self.page_count - 1

            # Make sure that the requested page number is the range of valid pages
            if self.page > self.last_page:
                self.page = self.last_page
            elif self.page < self.first_page:
                self.page = self.first_page

            # Note: the number of items on this page can be less than
            #       items_per_page if the last page is not full
            self.first_item = (self.page - 1) * items_per_page + 1
            self.last_item = min(self.first_item + items_per_page - 1, self.item_count)

            # We subclassed "list" so we need to call its init() method
            # and fill the new list with the items to be displayed on the page.
            # We use list() so that the items on the current page are retrieved
            # only once. Otherwise it would run the actual SQL query everytime
            # .items would be accessed.
            try:
                first = self.first_item - 1
                last = self.last_item
                self.items = list(self.collection[first:last])
            except TypeError(e):
                raise TypeError("Your collection of type %s cannot be handled by paginate." ,
                                type(self.collection))

            # Links to previous and next page
            if self.page > self.first_page:
                self.previous_page = self.page-1
            else:
                self.previous_page = None

            if self.page < self.last_page:
                self.next_page = self.page+1
            else:
                self.next_page = None

        # No items available
        else:
            self.first_page = None
            self.page_count = 0
            self.last_page = None
            self.first_item = None
            self.last_item = None
            self.previous_page = None
            self.next_page = None
            self.items = []

        # This is a subclass of the 'list' type. Initialise the list now.
        list.__init__(self, self.items)


    def __repr__(self):
        return ("Page:\n"
            "Collection type:  %(type)s\n"
            "Current page:     %(page)s\n"
            "First item:       %(first_item)s\n"
            "Last item:        %(last_item)s\n"
            "First page:       %(first_page)s\n"
            "Last page:        %(last_page)s\n"
            "Previous page:    %(previous_page)s\n"
            "Next page:        %(next_page)s\n"
            "Items per page:   %(items_per_page)s\n"
            "Number of items:  %(item_count)s\n"
            "Number of pages:  %(page_count)s\n"
            % {
            'type':self.collection_type,
            'page':self.page,
            'first_item':self.first_item,
            'last_item':self.last_item,
            'first_page':self.first_page,
            'last_page':self.last_page,
            'previous_page':self.previous_page,
            'next_page':self.next_page,
            'items_per_page':self.items_per_page,
            'item_count':self.item_count,
            'page_count':self.page_count,
            })

    def pager(self, format='~2~', page_param='page', partial_param='partial',
        show_if_single_page=False, separator=' ', onclick=None,
        symbol_first='<<', symbol_last='>>',
        symbol_previous='<', symbol_next='>',
        link_attr={'class':'pager_link'}, curpage_attr={'class':'pager_curpage'},
        dotdot_attr={'class':'pager_dotdot'}, **kwargs):
        """
        Return string with links to other pages (e.g. "1 2 [3] 4 5 6 7").

        format:
            Format string that defines how the pager is rendered. The string
            can contain the following $-tokens that are substituted by the
            string.Template module:

            - $first_page: number of first reachable page
            - $last_page: number of last reachable page
            - $page: number of currently selected page
            - $page_count: number of reachable pages
            - $items_per_page: maximal number of items per page
            - $first_item: index of first item on the current page
            - $last_item: index of last item on the current page
            - $item_count: total number of items
            - $link_first: link to first page (unless this is first page)
            - $link_last: link to last page (unless this is last page)
            - $link_previous: link to previous page (unless this is first page)
            - $link_next: link to next page (unless this is last page)

            To render a range of pages the token '~3~' can be used. The 
            number sets the radius of pages around the current page.
            Example for a range with radius 3:

            '1 .. 5 6 7 [8] 9 10 11 .. 500'

            Default: '~2~'

        symbol_first
            String to be displayed as the text for the %(link_first)s 
            link above.

            Default: '<<'

        symbol_last
            String to be displayed as the text for the %(link_last)s 
            link above.

            Default: '>>'

        symbol_previous
            String to be displayed as the text for the %(link_previous)s 
            link above.

            Default: '<'

        symbol_next
            String to be displayed as the text for the %(link_next)s 
            link above.

            Default: '>'

        separator:
            String that is used to separate page links/numbers in the 
            above range of pages.

            Default: ' '

        page_param:
            The name of the parameter that will carry the number of the 
            page the user just clicked on. The parameter will be passed 
            to a url_for() call so if you stay with the default 
            ':controller/:action/:id' routing and set page_param='id' then 
            the :id part of the URL will be changed. If you set 
            page_param='page' then url_for() will make it an extra 
            parameters like ':controller/:action/:id?page=1'. 
            You need the page_param in your action to determine the page 
            number the user wants to see. If you do not specify anything 
            else the default will be a parameter called 'page'.

            Note: If you set this argument and are using a URL generator
            callback, the callback must accept this name as an argument instead
            of 'page'.
            callback, becaust the callback requires its argument to be 'page'.
            Instead the callback itself can return any URL necessary.

        partial_param:
            When using AJAX/AJAH to do partial updates of the page area the
            application has to know whether a partial update (only the
            area to be replaced) or a full update (reloading the whole
            page) is required. So this parameter is the name of the URL
            parameter that gets set to 1 if the 'onclick' parameter is
            used. So if the user requests a new page through a Javascript
            action (onclick) then this parameter gets set and the application
            is supposed to return a partial content. And without
            Javascript this parameter is not set. The application thus has
            to check for the existence of this parameter to determine
            whether only a partial or a full page needs to be returned.
            See also the examples in this modules docstring.

            Default: 'partial'

            Note: If you set this argument and are using a URL generator
            callback, the callback must accept this name as an argument instead
            of 'partial'.

        show_if_single_page:
            if True the navigator will be shown even if there is only 
            one page.
            
            Default: False

        link_attr (optional)
            A dictionary of attributes that get added to A-HREF links 
            pointing to other pages. Can be used to define a CSS style 
            or class to customize the look of links.

            Example: { 'style':'border: 1px solid green' }

            Default: { 'class':'pager_link' }

        curpage_attr (optional)
            A dictionary of attributes that get added to the current 
            page number in the pager (which is obviously not a link).
            If this dictionary is not empty then the elements
            will be wrapped in a SPAN tag with the given attributes.

            Example: { 'style':'border: 3px solid blue' }

            Default: { 'class':'pager_curpage' }

        dotdot_attr (optional)
            A dictionary of attributes that get added to the '..' string
            in the pager (which is obviously not a link). If this 
            dictionary is not empty then the elements will be wrapped in 
            a SPAN tag with the given attributes.

            Example: { 'style':'color: #808080' }

            Default: { 'class':'pager_dotdot' }

        onclick (optional)
            This paramter is a string containing optional Javascript code
            that will be used as the 'onclick' action of each pager link.
            It can be used to enhance your pager with AJAX actions loading another 
            page into a DOM object. 

            In this string the variable '$partial_url' will be replaced by
            the URL linking to the desired page with an added 'partial=1'
            parameter (or whatever you set 'partial_param' to).
            In addition the '$page' variable gets replaced by the
            respective page number.

            Note that the URL to the destination page contains a 'partial_param' 
            parameter so that you can distinguish between AJAX requests (just 
            refreshing the paginated area of your page) and full requests (loading 
            the whole new page).

            [Backward compatibility: you can use '%s' instead of '$partial_url']

            jQuery example:
                "$('#my-page-area').load('$partial_url'); return false;"

            Yahoo UI example:
                "YAHOO.util.Connect.asyncRequest('GET','$partial_url',{
                    success:function(o){YAHOO.util.Dom.get('#my-page-area').innerHTML=o.responseText;}
                    },null); return false;"

            scriptaculous example:
                "new Ajax.Updater('#my-page-area', '$partial_url',
                    {asynchronous:true, evalScripts:true}); return false;"

            ExtJS example:
                "Ext.get('#my-page-area').load({url:'$partial_url'}); return false;"
            
            Custom example:
                "my_load_page($page)"

        Additional keyword arguments are used as arguments in the links.
        Otherwise the link will be created with url_for() which points 
        to the page you are currently displaying.
        """
        self.curpage_attr = curpage_attr
        self.separator = separator
        self.pager_kwargs = kwargs
        self.page_param = page_param
        self.partial_param = partial_param
        self.onclick = onclick
        self.link_attr = link_attr
        self.dotdot_attr = dotdot_attr

        # Don't show navigator if there is no more than one page
        if self.page_count == 0 or (self.page_count == 1 and not show_if_single_page):
            return ''

        # Replace ~...~ in token format by range of pages
        result = re.sub(r'~(\d+)~', self._range, format)

        # Interpolate '%' variables
        result = Template(result).safe_substitute({
            'first_page': self.first_page,
            'last_page': self.last_page,
            'page': self.page,
            'page_count': self.page_count,
            'items_per_page': self.items_per_page,
            'first_item': self.first_item,
            'last_item': self.last_item,
            'item_count': self.item_count,
            'link_first': self.page>self.first_page and \
                    self._pagerlink(self.first_page, symbol_first) or '',
            'link_last': self.page<self.last_page and \
                    self._pagerlink(self.last_page, symbol_last) or '',
            'link_previous': self.previous_page and \
                    self._pagerlink(self.previous_page, symbol_previous) or '',
            'link_next': self.next_page and \
                    self._pagerlink(self.next_page, symbol_next) or ''
        })

        return result

    #### Private methods ####
    def _range(self, regexp_match):
        """
        Return range of linked pages (e.g. '1 2 [3] 4 5 6 7 8').

        Arguments:
            
        regexp_match
            A "re" (regular expressions) match object containing the
            radius of linked pages around the current page in
            regexp_match.group(1) as a string

        This function is supposed to be called as a callable in 
        re.sub to replace occurences of ~\d+~ by a sequence of page links.
        """
        radius = int(regexp_match.group(1))

        # Compute the first and last page number within the radius
        # e.g. '1 .. 5 6 [7] 8 9 .. 12'
        # -> leftmost_page  = 5
        # -> rightmost_page = 9
        leftmost_page = max(self.first_page, (self.page-radius))
        rightmost_page = min(self.last_page, (self.page+radius))

        nav_items = []

        # Create a link to the first page (unless we are on the first page
        # or there would be no need to insert '..' spacers)
        if self.page != self.first_page and self.first_page < leftmost_page:
            nav_items.append( self._pagerlink(self.first_page, self.first_page) )

        # Insert dots if there are pages between the first page
        # and the currently displayed page range
        if leftmost_page - self.first_page > 1:
            # Wrap in a SPAN tag if nolink_attr is set
            if self.dotdot_attr:
                text = make_html_tag('span', **self.dotdot_attr) + text + '</span>'
            else:
                text = '..'
            nav_items.append(text)

        for thispage in range(leftmost_page, rightmost_page+1):
            # Highlight the current page number and do not use a link
            if thispage == self.page:
                # Wrap in a SPAN tag if nolink_attr is set
                if self.curpage_attr:
                    text = make_html_tag('span', **self.curpage_attr) + text + '</span>'
                else:
                    text = '%s' % (thispage,)
                nav_items.append(text)
            # Otherwise create just a link to that page
            else:
                text = '%s' % (thispage,)
                nav_items.append( self._pagerlink(thispage, text) )

        # Insert dots if there are pages between the displayed
        # page numbers and the end of the page range
        if self.last_page - rightmost_page > 1:
            # Wrap in a SPAN tag if nolink_attr is set
            if self.dotdot_attr:
                text = make_html_tag('span', **self.dotdot_attr) + text + '</span>'
            else:
                text = '..'
            nav_items.append(text)

        # Create a link to the very last page (unless we are on the last
        # page or there would be no need to insert '..' spacers)
        if self.page != self.last_page and rightmost_page < self.last_page:
            nav_items.append( self._pagerlink(self.last_page, self.last_page) )

        return self.separator.join(nav_items)

    def _pagerlink(self, page, text):
        """
        Create a URL that links to another page using url_for().

        Parameters:
            
        page
            Number of the page that the link points to

        text
            Text to be printed in the A-HREF tag
        """
        # Let the url_for() from webhelpers create a new link and set
        # the variable called 'page_param'. Example:
        # You are in '/foo/bar' (controller='foo', action='bar')
        # and you want to add a parameter 'page'. Then you
        # call the navigator method with page_param='page' and
        # the url_for() call will create a link '/foo/bar?page=...'
        # with the respective page number added.
        link_params = {}
        # Use the instance kwargs from Page.__init__ as URL parameters
        link_params.update(self.kwargs)
        # Add keyword arguments from pager() to the link as parameters
        link_params.update(self.pager_kwargs)
        link_params[self.page_param] = page

        # Create the URL to load a certain page
        link_url = url_generator(self.url, **link_params)

        if self.onclick: # create link with onclick action for AJAX
            # Create the URL to load the page area part of a certain page (AJAX
            # updates)
            link_params[self.partial_param] = 1
            partial_url = url_generator(self.url, **link_params)
            try: # if '%s' is used in the 'onclick' parameter (backwards compatibility)
                onclick_action = self.onclick % (partial_url,)
            except TypeError:
                onclick_action = Template(self.onclick).safe_substitute({
                  "partial_url": partial_url,
                  "page": page
                })
            return HTML.a(text, href=link_url, onclick=onclick_action, **self.link_attr)
        else: # return static link
            return HTML.a(text, href=link_url, **self.link_attr)


#### URL GENERATOR CLASSES
def make_page_url(path, params, page, partial=False, sort=True):
    """A helper function for URL generators.

    I assemble a URL from its parts. I assume that a link to a certain page is
    done by overriding the 'page' query parameter.

    ``path`` is the current URL path, with or without a "scheme://host" prefix.

    ``params`` is the current query parameters as a dict or dict-like object.

    ``page`` is the target page number.

    If ``partial`` is true, set query param 'partial=1'. This is to for AJAX
    calls requesting a partial page.

    If ``sort`` is true (default), the parameters will be sorted. Otherwise
    they'll be in whatever order the dict iterates them.
    """
    params = params.copy()
    params["page"] = page
    if partial:
        params["partial"] = "1"
    if sort:
        params = params.items()
        params.sort()
    qs = urllib.urlencode(params, True)
    return "%s?%s" % (path, qs)
    
class PageURL(object):
    """A simple page URL generator for any framework."""

    def __init__(self, path, params):
        """
        ``path`` is the current URL path, with or without a "scheme://host"
         prefix.

        ``params`` is the current URL's query parameters as a dict or dict-like
        object.
        """
        self.path = path
        self.params = params

    def __call__(self, page, partial=False):
        """Generate a URL for the specified page."""
        return make_page_url(self.path, self.params, page, partial)


class PageURL_WebOb(object):
    """A page URL generator for WebOb-compatible Request objects.
    
    I derive new URLs based on the current URL but overriding the 'page'
    query parameter.

    I'm suitable for Pyramid, Pylons, and TurboGears, as well as any other
    framework whose Request object has 'application_url', 'path', and 'GET'
    attributes that behave the same way as ``webob.Request``'s.
    """
    
    def __init__(self, request, qualified=False):
        """
        ``request`` is a WebOb-compatible ``Request`` object.

        If ``qualified`` is false (default), generated URLs will have just the
        path and query string. If true, the "scheme://host" prefix will be
        included. The default is false to match traditional usage, and to avoid
        generating unuseable URLs behind reverse proxies (e.g., Apache's
        mod_proxy). 
        """
        self.request = request
        self.qualified = qualified

    def __call__(self, page, partial=False):
        """Generate a URL for the specified page."""
        if self.qualified:
            path = self.request.application_url
        else:
            path = self.request.path
        return make_page_url(path, self.request.GET, page, partial)

def make_html_tag(tag, **params):
    """Create an HTML tag string with properly escaped parameters."""
    params_string = ''

    # Parameters are passed. Turn the dict into a string like "a=1 b=2 c=3" string.
    for param in params.items():
        key, value = param

        # Strip off a leading underscore from the attribute's key to allow attributes like '_class'
        # to be used as a CSS class specification instead of the reserved Python keyword 'class'.
        key = key.lstrip('_')

        # Escape the attribute's value for security reasons.
        # Replace special characters '"', '&', '<' and '>' to HTML-safe sequences.
        # Imitates cgi.escape from the Python standard library.
        #value = value.replace("&", "&amp;") # Must be done first!
        #value = value.replace("<", "&lt;")
        #value = value.replace(">", "&gt;")
        #value = value.replace('"', "&quot;")
        # XXX: Values are expected to be properly escaped.
        # XXX: Otherwise this function cannot distinguish between illegale quotes
        # XXX: and legal ones used e.g. in alert("foo")

        params_string += ' %s="%s"' % (key, value)

    #if params:
    #    params_string = ' '+' '.join(['%s="%s"' % (item[0].lstrip('_'), item[1]) for item in params.items()])
    #else:
    #    params_string = ''

    # Create the tag string
    tag_string = '<%s%s>' % (tag, params_string)

    return tag_string

def url_generator(url, **params):
    """Parse the URL and replace the query parameters with the params passed to this function."""
    # TODO: tests missing

    # Split the given URL into the path and the query parameters
    url_path, query_params=urllib.splitquery(url)
    # Parse the query parameters and put them into a dictionary.
    query_dict = dict(cgi.parse_qsl(query_params))

    # Update the dictionary with the new parameters that should be changed.
    query_dict.update(params)

    # Create a new query parameter string.
    new_query_params = '&'.join(['%s=%s' % item for item in query_dict.items()])

    # Put together a new URL and return it
    return "%s?%s" % (url_path, new_query_params)

# TODO: add support for CouchDB databases (http://guide.couchdb.org/editions/1/de/recipes.html)
# TODO: find a better way to abstract the Page. e.g. subclass Page as PageSqlalchemy or PageCouchdb
