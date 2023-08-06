"""
Author: I (iroiso@live.com)
Copyright 2012, June Inc.
"""
import webob
import inspect
import logging
import urlparse
import threading
from traceback import print_exc

from routes import route
from routes.mapper import Mapper

from .exceptions import status_map, HTTPInternalServerError, HTTPException, HTTPNotFound

__version__ = "v1.0.0.beta"
__all__ = ["Application", "Resource", "Path", "Route", "abort", "run", ]
HTTP_METHODS = ["HEAD", "GET", "PUT", "DELETE", "POST",]
__all__.extend(HTTP_METHODS)

logger = logging.getLogger('gates.logger')

###############################################################################
# Exceptions ##################################################################
###############################################################################

class DuplicatePathError(Exception):
    '''Another Request handler is already bound to this path'''
    pass
    
###############################################################################
# HTTP Routing Tools ##########################################################
###############################################################################
'''
RouteBuilder:
This class uses the builder pattern to configure and create
routes.Route objects which will be added to the global mapper.

This is necessary because Gates' decorators configure routes
on many different levels, so we need a consistent interface
for creating routes.Route objects.

Sample code:
builder = RouteBuilder()
builder = builder.route("/{home}/edit/{action: save|discard}")          #Add this route to this builder.
builder = builder.controller("DocumentController").httpverb("PUT")
builder = builder.action("do")
route = builder.build()                                                 #Create the route object finally.

'''
class RouteBuilder(object):
    '''Make an instance routes.Route using the builder pattern'''
 
    def __init__(self):
        '''An empty constructor'''
        self.__method = set()
        self.__route = None
        
    def route(self, route):
        '''Create a new RouteBuilder'''
        assert route is not None, "Routes cannot be None"
        assert route.startswith('/'), "Routes must begin with a '/'"
        self.__route = route
        return self

    def controller(self, name):
        '''Set the controller for the current route'''
        self.__controller = name
        return self
    
    def hasHTTPVerb(self):
        '''Checks if there is HTTP verb set on this route'''
        return bool(self.__method)
    
    def hasRoute(self):
        '''Checks if there is a route set on this ``RouteBuilder``'''
        return bool(self.__route)
          
    def action(self, action):
        '''Set the action for the current controller'''
        self.__action = action
        return self

    def httpverb(self, method):
        '''Set the HTTP method for the ``RouteBuilder``'''
        assert method in HTTP_METHODS, "Invalid HTTP Method please use one of: %s" % HTTP_METHODS
        self.__method.add(method)
        return self
        
    def build(self):
        '''Create a route.Route object from this ``RouteBuilder`` and return it'''
        return route.Route(None, routepath=self.__route, controller=self.__controller, 
            action=self.__action, conditions=dict(method=list(self.__method)))    
            
###############################################################################
# Decorators ##################################################################
###############################################################################
'''
Path:
A Decorator that hooks a ``Resource`` with the internal
HTTP Routing mechanism.

Sample use:

@Path('/home')
class HomeHandler(Resource):
    pass
    
Implementation Notes:
What we want here is for the @Path decorator to register the handler
with the framework's ``Registry``. It makes sure that every handler 
is mapped to a unique path within the registry.
'''
def Path(base):
    '''The @Path Decorator'''
    #Create and Register the route if it doesn't exist
    def inner(clasz):
        '''Wrapper for the function '''
        assert issubclass(clasz, Resource), "@Path can only be used on Resources"
        assert base.startswith("/"), "URLs used in route should start with /"
        logger.info('Wrapping Class: %s' % clasz.__name__)
        Registry.addHandler(base, clasz)
        return clasz
    return inner

'''
Route:
Used to bind a method in a ``Resource`` to a URL Route;
'''
def Route(route):
    '''The @Route Decorator'''
    def inner(action):
        '''Wrapper for the action '''
        assert route.startswith("/"), "All routes must start with '/'"
        logger.info('Configuring Routes and Action for method: %s' % action.__name__)
        builder = Registry.builderFor(action)
        builder.route(route).action(action)
        if not builder.hasHTTPVerb():
            GET(action)
        return action
    return inner



###############################################################################
# HTTP Verbs ##################################################################
###############################################################################
'''
GET:
Binds a method to the HTTP GET Verb;
'''
def GET(action):
    '''Binds a method and route to the HTTP Verb "GET"'''
    logger.info("Configuring HTTP GET Verb for method: %s" % action.__name__)
    HEAD(action)
    builder = Registry.builderFor(action)
    builder.httpverb("GET")
    return action

'''
POST:
Binds a method to the HTTP POST Verb;
'''
def POST(action):
    '''Binds a method and route to the HTTP Verb "POST"'''
    logger.info("Configuring HTTP POST Verb for method: %s" % action.__name__)
    HEAD(action)
    builder = Registry.builderFor(action)
    builder.httpverb("POST")
    return action

'''
PUT:
Binds a method to the HTTP PUT Verb;
'''
def PUT(action):
    '''Binds a method and route to the HTTP Verb "PUT"'''
    logger.info("Configuring HTTP PUT Verb for method: %s" % action.__name__)
    HEAD(action)
    builder = Registry.builderFor(action)
    builder.httpverb("PUT")
    return action

'''
DELETE:
Binds a method to the HTTP DELETE Verb;
'''
def DELETE(action):
    '''Binds a method and route to the HTTP Verb "DELETE"'''
    logger.info("Configuring HTTP PUT Verb for method: %s" % action.__name__)
    HEAD(action)
    builder = Registry.builderFor(action)
    builder.httpverb("DELETE")
    return action

'''
HEAD:
Binds a method to the HTTP HEAD Verb;
'''
def HEAD(action):
    '''Binds a method and route to the HTTP Verb "HEAD"'''
    logger.info("Configuring HTTP HEAD Verb for method: %s" % action.__name__)
    builder = Registry.builderFor(action)
    builder.httpverb("HEAD")
    if not builder.hasRoute():
        do = Route("/")
        do(action) # Make every method marked with @HEAD have a default route '/'
    return action

###############################################################################
# HTTP Core Tools #############################################################
###############################################################################
'''
Application:
Primary used for grouping and running``Resource`` objects, it dispatches 
HTTP requests to the appropriate handler at run time.
'''
class Application(object):
    '''Used for grouping request handlers and running them'''
    
    def __init__(self, base="/", resources=[]):
        '''Initialize this application'''
        self.router = Registry.mapperFor(base, *resources) # Create a Matcher.
    
    def before(self, request):
        '''Override this to customize all requests'''
        return request
    
    def after(self, response):
        '''Override this to customize all responses'''
        return response  
        
    def __call__(self, environ, start_response):
        '''WSGI entry point'''
        request = Request(environ)                            
        response = Response(conditional=True)
        
        try:
            result = self.router.match(environ=environ, url=request.path)     
            if result is None:
                raise HTTPNotFound("The requested Resource [%s] was not found this server; " % request.path)
                
            request = self.before(request)                        #Invoke the global request pre-processor
            clasz, method = result.pop('controller'), result.pop('action') 
            instance = clasz(self, request, response)                                                                 
            instance.before()                                     #Invoke the local request pre-processor         
            method(instance, **result)                           
            instance.after()                                      #Invoke the local response post-processor
            response = self.after(response)                       #Invoke the global response post-processor
            
        except HTTPException as e:
            response = Response(impl=e)
            response.contenttype = "text/plain"
        
        except Exception as e:
            e = HTTPInternalServerError("Internal Server Error, We'll check this out in a few hours")
            response = Response(impl=e)
            response.contenttype = "text/plain"
            
        return response(environ, start_response)


'''
Registry:
Global storage for tracking ``Resource`` objects and Routes.
'''
class Registry(threading.local):
    '''Global Configuration object'''
    paths = {}     #Maps {'/path': Resource} 
    handlers = {}  #Maps {Resource : '/path'}
    builders = {}  #Cached RouteBuilders' { function : RouteBuilder} }
    
    @classmethod
    def clear(cls):
        '''Clears all the entries from the Registry'''
        cls.paths.clear()
        cls.handlers.clear()
        cls.builders.clear()
        
    @classmethod
    def addHandler(cls, base, handler):
        '''Add particular handler to this base url'''
        assert base.startswith("/") and handler is not None, "Bad Arguments to addHandler"
        assert issubclass(handler, Resource), "@handler must be a Resource"
        if base in cls.paths:
            raise DuplicatePathError("Another Handler is already bound to Path: %s" % base)
        logger.info("Adding %s to route => %s" % (handler.__name__, base))   
        cls.paths[base] = handler
        cls.handlers[handler] = base
    
    @classmethod
    def handlerFor(cls, base):
        '''Returns the handler for a particular path'''
        return cls.paths[base]
    
    @classmethod
    def pathFor(cls, handler):
        '''Returns the path for a particular Resource'''
        return cls.handlers[handler]
    
    @classmethod
    def routesFor(cls, handler):
        '''Returns all the ``routes.Route`` objects for a particular handler, building them on the fly'''
        assert handler in cls.handlers, "Unregistered Handler Error"
        for func in handler.__dict__.values():
            if inspect.isfunction(func) and func in cls.builders:
                builder = cls.builders[func]
                yield builder.build()
    
    @classmethod
    def mapperFor(cls, base, *handlers):
        '''Returns a new mapper that will match all the methods in @handlers'''
        base = base.rstrip(" /")
        mapper = Mapper()
        for handler in handlers:
            path = cls.pathFor(handler)
            if base:
                path = base + path
            created = list(cls.routesFor(handler))
            mapper.extend(created, path)
        return mapper
                 
    @classmethod
    def builderFor(cls, function):
        '''
        Returns the RouteBuilder for a particular bound method, 
        if no builder exists it creates one and returns it, every RouteBuilder 
        returned always has a Controller that is a Resource
        '''
        assert inspect.isfunction(function), "you can only create builder for a function"
        builder = cls.builders.setdefault(function, RouteBuilder())
        return builder

"""
__scan__:
searches the class for any unbound methods and creates a route builder for 
each of those methods, effectively pre-registring them with ``Registry`` 
and setting their controllers, which will eventually allow all http bound
methods (Methods decorated with a http verb e.g. POST) to discover their
controllers (Their parent Resources).

This is useful because, at the point when function decorators on classes are
evaluated the callables they decorate are not 'class bound methods yet', so 
its not possible to know the class which a decorated method is bound to at
class creation time.

"""
class __scan__(type):
    def __new__(cls, name, bases, dict):
        '''A meta-callable that is used to do basic registration of http bound methods in a Resource.'''
        clasz = type.__new__(cls, name, bases, dict)
        for v in dict.values():
            if inspect.isfunction(v):
                builder = Registry.builderFor(v)
                builder.controller(clasz)
        return clasz
    
'''
Resource:
The threadsafe base class for all classes that will handle HTTP requests.
'''
class Resource(threading.local):
    '''The Base class for all HTTP Request Handlers'''
    __metaclass__ = __scan__
    
    def __init__(self, application, request, response):
        '''Initialize the Request Handler'''
        self.request = request
        self.response = response
        self.application = application
    
    def redirect(self, location, code=None, permanent=True, stop=True):
        '''Redirect to @location, if stop is true it breaks execution'''
        if location.startswith(('.', '/')):
            location = str(urlparse.urljoin(self.request.url, location))
        if code is None:
            code = 301 if permanent else 302
        assert code in (301, 302, 303, 305, 307),'Invalid redirect status code.'  
        
        if stop: 
            abort(code, headers=[('Location', location)]) 
        self.response.headers['Location'] = location
        self.response.statuscode = code
            
    def before(self):
        '''Request pre-processor'''
        pass
    
    def after(self):
        '''Response post-processor'''
        pass
        
   
'''
Request:
An object that encapsulates incoming HTTP requests, It provides
convenient methods methods that can be used to access the properties
of the Request.
'''
class Request(object):
    '''Abstracts the WSGI environ into a Request object'''
    def __init__(self, environ):
        '''Initialize the Environ'''
        assert environ != None, "You must provide a non-null WSGI environ dict"
        self.impl = impl = webob.Request(environ)
        
        ## REMAKE PROPERTIES AND RE-ASSIGN THEM TO SELF ##
        makeProperty(self, "body", "impl", "body")
        makeProperty(self, "host", "impl", "host")
        makeProperty(self, "pathinfo", "impl", "path_info")
        makeProperty(self, "scheme", "impl", "scheme")
        makeProperty(self, "scriptname", "impl", "script_name")
        makeProperty(self, "accept", "impl", "accept")
        makeProperty(self, "headers", "impl", "headers")
        makeProperty(self, "method", "impl", "method")
        makeProperty(self, "charset", "impl", "charset")
        makeProperty(self, "query", "impl", "query_string")
        makeProperty(self, "url", "impl", "url")
        makeProperty(self, "cookies", "impl", "cookies")
        makeProperty(self, "accept", "impl", "accept")
        makeProperty(self, "params", "impl", "params")
        makeProperty(self, "path", "impl", "path")
        makeProperty(self, "contenttype","impl", "content_type")
        makeProperty(self, "contentlength", "impl", "content_length")
    
    def get(self, name, default=None):
        '''Returns the query or POST argument with the given name'''
        params = self.getall(name)
        if len(params) > 0:
            return params[0]
        else:
            return default
        
    def getall(self, name, default=None):
        '''Returns the query or POST argument with the given name'''
        if self.charset:
            name = name.encode(self.charset)
            
        params = self.params.getall(name)
        if params is None or len(params) == 0:
            return default
        for i in xrange(len(params)):
            if isinstance(params[i], cgi.FieldStorage):
                params[i] = params[i].value
        return params
    
    def arguments(self):
        """Returns a list of the arguments provided in the query and/or POST."""
        return list(set(self.params.keys()))
    
    def getResponse(self, application, catchExceptions=False):
        '''Return a `Response` after invoking @application'''
        impl = self.impl.get_response(application=application, catch_exc_info=catchExceptions)
        return Response(impl=impl)
          
    @classmethod
    def blank(cls, path):
        '''Useful for creating empty requests that are useful for testing.'''
        impl = webob.Request.blank(path)
        request = Request(impl.environ.copy())
        return request
        
        
    
'''
Response:
Abstracts a HTTP Response, Basically what I did here
is to make the webob API conform to our coding style
after removing deprecated components. 
'''
class Response(object):
    '''Represents a Response object'''
    def __init__(self, body=None, status=None, conditional=None, impl=None):
        '''Creates a new Response object'''
        if not impl:
            new = webob.Response(body=body, status=status,conditional_response=conditional)
            self.impl = impl = new
        else:
            self.impl = impl 
            
        ## REMAKE PROPERTIES AND RE-ASSIGN THEM TO SELF##
        makeProperty(self, "body", "impl", "body")
        makeProperty(self, "text", "impl", "text")
        makeProperty(self, "status", "impl", "status")
        makeProperty(self, "headers", "impl", "headers")
        makeProperty(self, "bodyfile", "impl", "body_file")
        makeProperty(self, "charset", "impl", "charset")
        makeProperty(self, "expires","impl", "expires")
        makeProperty(self, "headerlist","impl", "headerlist")
        makeProperty(self, "contenttype","impl", "content_type")
        makeProperty(self, "statuscode", "impl", "status_int")
        makeProperty(self, "contentlength", "impl", "content_length")
        makeProperty(self, "vary", "impl", "vary")
        makeProperty(self, "lastmodified", "impl", "last_modified")
        makeProperty(self, "date", "impl", "date")
        makeProperty(self, "retryafter", "impl", "retry_after")
        makeProperty(self, "location", "impl", "location")
        makeProperty(self, "age", "impl", "age")
        
        ## RENAME AND REWIRE OK METHODS ##
        self.write = impl.write
        self.addCookie = impl.set_cookie
        self.removeCookie = impl.unset_cookie  
        self.encodeContent = impl.encode_content
        self.decodeContent = impl.decode_content 
        self.deleteCookieFromClient = impl.delete_cookie
        
    def __call__(self, environ, function):
        '''Every response is a WSGI compliant app also'''
        return self.impl(environ, function)
            
    def clear(self):
        '''Clears the body of the Response'''
        self.body = ''
            
    def md5ETag(self):
        '''Generates an Md5 E-Tag for the response object'''
        self.impl.md5_etag(self, set_content_md5=True)

###############################################################################
# Runtime Tools. ####################################################
###############################################################################
'''
ServerAdapter:
Base class that all servers will have to conform to.
'''
class ServerAdapter(object):
    quiet = False
    def __init__(self, host='127.0.0.1', port=8080, **config):
        self.options = config
        self.host = host
        self.port = int(port)

    def run(self, handler): # pragma: no cover
        pass

    def __repr__(self):
        args = ', '.join(['%s=%s'%(k,repr(v)) for k, v in self.options.items()])
        return "%s(%s)" % (self.__class__.__name__, args)

'''
WSGIRefServer:
Uses the python inbuilt WSGI server to run Gates applications.
'''
class WSGIRefServer(ServerAdapter):
    '''Single threaded WSGI server that is useful for testing'''
    
    def run(self, handler): 
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.serve_forever()    


'''
MeinheldServer:
An adapter that uses Meinheld to run a Gates application
'''
class MeinheldServer(ServerAdapter):
    '''Server adapter for Meinheld'''
    
    def run(self, handler):
        '''Runs the Gates application in Meinheld'''
        from meinheld import server
        server.listen((self.host, self.port))
        server.run(handler)
                      
###############################################################################
# Public Helper Functions. ####################################################
###############################################################################
'''
abort:
Invoke abort to break execution and raise a valid HTTP Exception;

'''
def abort(code=500, detail="We're sorry you have to see this, we'll fix it soon", **arguments):
    '''A helper that is used to raise a valid HTTPException at any point'''
    cls = status_map.get(code)
    if not cls:
        raise KeyError('No exception is defined for code %r.' % code)
    raise cls(detail=detail, **arguments)

'''
run:
A helper method that is used to run a Gates application in a particular
server, This method blocks until the server terminates.

@app      : The Gates Application,
@server   : The Server you want to run the application in.
@arguments: A list of other arguments you may want to pass to the Server.
@port     : The port to run the application at.
@host     : The IP address to bind the application to.
quiet     : If true, print debug information to standard error.
'''
def run(application=None, server=WSGIRefServer, host="127.0.0.1", port=8080, quiet=False, **arguments):
    '''A helper method used to run the application'''
    try:
        server = server(host=host, port=port, **arguments)
        server.quiet = quiet
        print("\nBill Gates Invented the Web...")
        print("Gates %s server starting up (using %s)..." % (__version__, repr(server)))
        print("Listening on http://%s:%d/" % (server.host, server.port))
        print("Hit Ctrl-C to quit.")
        server.run(application)  
    except KeyboardInterrupt:
        print("\n")
        print("Closing Gates...")     
      
###############################################################################
# Internal Helper functions ###################################################
###############################################################################   
"""
makeProperty:
Creates a new property from an already defined property.
This used in the `Response` object to rewire defined properties
in webob.Response.

@owner:    The class or instance to set the property on
@member:   A str that represents the name of the new property
@instance: The member variable you want to copy the property from
@name:     The name of the property in @instance.
@doc:      The documentation for the new property.

Doesn't work with hidden variables.
"""
def makeProperty(owner, member, instance, name, doc=""):
    '''Creates a new property from an existing property'''
    for name in (member, instance, name): 
        if name.startswith("_"):
            raise AssertionError("No support for hidden variables")               
    if hasattr(owner, member): 
        logger.info("Property seems to exist already, skipping call")
        return    
    fget = lambda self: getattr(getattr(self, instance), name)
    fdel = lambda self: delattr(getattr(self, instance), name)
    fset = lambda self, value: setattr(getattr(self, instance), name, value)
    new = property(fget, fset, fdel, doc)
    cls = owner if isinstance(owner, type) else owner.__class__
    setattr(cls, member, new)
    
        
    

