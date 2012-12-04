"""Extension to the paginate module to paginate through SQLAlchemy objects."""

SQLALCHEMY_MINIMAL_VERSION='0.4'

# Import the basic Page object. We will create a subclass of it.
import paginate

import sqlalchemy
from distutils.version import StrictVersion # for version comparison

# Ensure we are dealing with a supported version of SQLAlchemy
if StrictVersion(sqlalchemy.__version__)<StrictVersion(SQLALCHEMY_MINIMAL_VERSION):
    raise Exception('SQLAlchemy version %s or higher required' % SQLALCHEMY_MINIMAL_VERSION)

class SqlalchemyPage(paginate.Page):
    """Page class representing items from a SQLAlchemy Select or ORM query object.
    
    See the documentation for the paginate.Page object for more details on how to use it."""
    def __init__(self, collection, sqlalchemy_object, item_count=None,
        sqlalchemy_session=None, **kwargs):
        """Create a Page object
        
        sqlalchemy_object: An sqlalchemy.sql.expression.Select or ORM object.

        item_count
            Number of items in the collection
            
            **WARNING:** Unless you pass in an item_count, a count will be 
            performed on the collection every time a Page instance is created. 
            If using an ORM, it's advised to pass in the number of items in the 
            collection if that number is known.

        sqlalchemy_session (optional)
            If you want to use an SQLAlchemy (0.4) select object as a
            collection then you need to provide an SQLAlchemy session object.
            Select objects do not have a database connection attached so it
            would not be able to execute the SELECT query.

        See the documentation for the paginate.Page object for more details on how to use it.

        # TODO: fixit
        Here's an example for Pyramid and other WebOb-compatible frameworks::
        
            # Assume ``request`` is the current request.
            import webhelpers.paginate as paginate
            current_page = int(request.params["page"])
            q = SOME_SQLALCHEMY_QUERY
            page_url = paginate.PageURL_WebOb(request)
            records = paginate.Page(q, current_page, url=page_url)
        
        If the page number is in the URL path, you'll have to use a framework-specific URL generator. For
        instance, in Pyramid if the current route is "/articles/{id}/page/{page}" and the current URL is
        "/articles/ABC/page/3?print=1", you can use Pyramid's "current_route_url" function as follows::
        
            # Assume ``request`` is the current request.
            import webhelpers.paginate as paginate
            from pyramid.url import current_route_url
            def page_url(page):
                return current_route_url(request, page=page, _query=request.GET)
            q = SOME_SQLALCHEMY_QUERY
            current_page = int(request.matchdict["page"])
            records = Page(q, current_page, url=page_url)
        """
    
        # Is the collection a query?
        if isinstance(obj, sqlalchemy.orm.query.Query):
            return _SQLAlchemyQuery(obj)

        # Is the collection an SQLAlchemy select object?
        if isinstance(obj, sqlalchemy.sql.expression.CompoundSelect) \
            or isinstance(obj, sqlalchemy.sql.expression.Select):
                return _SQLAlchemySelect(obj, sqlalchemy_session)

        super(SqlalchemyPage, self).__init__()
        # Subclass-specific stuff follows

class _SQLAlchemySelect(object):
    """
    Iterable that allows to get slices from an SQLAlchemy Select object
    """
    def __init__(self, obj, sqlalchemy_session=None):
        session_types = (
            sqlalchemy.orm.scoping.ScopedSession,
            sqlalchemy.orm.Session)
        if not isinstance(sqlalchemy_session, session_types):
            raise TypeError("If you want to page an SQLAlchemy 'select' object then you "
                    "have to provide a 'sqlalchemy_session' argument. See also: "
                    "http://www.sqlalchemy.org/docs/04/session.html")

        self.sqlalchemy_session = sqlalchemy_session
        self.obj = obj

    def __getitem__(self, range):
        if not isinstance(range, slice):
            raise Exception, "__getitem__ without slicing not supported"
        offset = range.start
        limit = range.stop - range.start
        select = self.obj.offset(offset).limit(limit)
        return self.sqlalchemy_session.execute(select).fetchall()

    def __len__(self):
        return self.sqlalchemy_session.execute(self.obj).rowcount

class _SQLAlchemyQuery(object):
    """
    Iterable that allows to get slices from an SQLAlchemy Query object
    """
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, range):
        if not isinstance(range, slice):
            raise Exception, "__getitem__ without slicing not supported"
        return self.obj[range]

    def __len__(self):
        return self.obj.count()

class SqlOrmPage(p)