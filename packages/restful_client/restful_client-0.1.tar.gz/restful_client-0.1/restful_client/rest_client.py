# -*- coding: utf-8 -*-
import urllib2
import futures

class RESTClient(urllib2.Request):
    """
    A RESTClient is an extension of a urllib2.Request class that also contains its own HTTP opener
    so the request can be executed and results passed through an (optional) call back mechanism.
    
    The default_callback function in __init__ demonstrates the protocol that should be supported by
    the callback function.
    
    See http://docs.python.org/library/urllib2.html#request-objects for urllib2 Request documentation
    and http://www.voidspace.org.uk/python/articles/urllib2.shtml
    and http://www.doughellmann.com/PyMOTW/urllib2/ for useful usage notes.
    
    TODO: Add support for timeouts at per client instance level (via opener).
    TODO: May need to implement smart exception handling. When YOU start encountering reproducable
                HTTP exceptions (or others) please contact Ben so he can see what exception handling strategy
                would work best for this library.
    """
    
    def __init__(self, uri, callback = None, data=None, headers={}, origin_req_host=None, unverifiable=False, opener=None):                
        
        def default_callback( response ):
            """
            Standard call back takes a RESTClient.Reponse instance which contains the following attributes:
            code = HTTP result code (integer)
            data = RAW results in string format
            uri = The actual URI that was resolved (after any possible redirects)
            headers = A string containing all the result headers
            
            Typically we want to just return a tuple containing the result code & data. Custom callbacks are allowed
            to return whatever they see fit, however.
            """
            return (response.code, response.data)
        
        urllib2.Request.__init__(self,uri,data,headers,origin_req_host,unverifiable) # super() wasn't working for me here?!!??
        
        self.opener = opener or urllib2.build_opener()
        self.callback = callback or default_callback
        
    class Response(object):
        def __init__(self, code, data, uri, headers):
            self.code = code
            self.data = data
            self.uri = uri
            self.headers = headers
        
    def __call__(self):        
        response = self.opener.open(self)
        result =  RESTClient.Response(  response.getcode(),
                                                            response.read(),
                                                            response.geturl(),
                                                            unicode(response.info()) )        
        return self.callback( result )

    # Have to refactor to support multiprocessing because of complaints about not being able to pickle the function.
    # Stick with multi-threaded for now.
    #@staticmethod
    #def async_mutiprocess(request_list, max_workers=None):
    #    return RESTClient.async_execute(request_list,futures.ProcessPoolExecutor,max_workers)
    
    @staticmethod
    def async_multithread(request_list, max_workers=16):    # Not sure what ThreadPoolExecutor defaults to so I made this up.
        return RESTClient.async_execute(request_list,futures.ThreadPoolExecutor,max_workers)
    
    @staticmethod
    def async_execute(request_list,exec_type=None,max_workers=None):
        """
        Asynchronously calls all the requests in request_list.
        Generator which yields each future instance as it is completed.
        
        See http://docs.python.org/dev/library/concurrent.futures.html#future-objects for information on what data/methods
        are available from the Future class.
        
        You'll be primarily interested in .result(), done(), and exception().
        
        TODO: Is it possible to offer a method to this generator allowing appends of new requests during processing?
        """
        exec_type = exec_type or futures.ThreadPoolExecutor  # should be futures.ProcessPoolExecutor but we're in a pickle! :-(
        with exec_type(max_workers=max_workers) as processor:
            future_requests = dict((processor.submit(request), request) for request in request_list)
            
            for future in futures.as_completed(future_requests):
                (yield future)

class GET(RESTClient):
    def get_method(self): return u'GET'

class POST(RESTClient):
    def get_method(self): return u'POST'
   
class PUT(RESTClient):
    def get_method(self): return u'PUT' 
    
class HEAD(RESTClient):
    def get_method(self): return u'HEAD'    

class DELETE(RESTClient):
    def get_method(self): return u'DELETE'
    
class OPTIONS(RESTClient):
    def get_method(self): return u'OPTIONS'    
        
class TRACE(RESTClient):
    def get_method(self): return u'TRACE'
    
class CONNECT(RESTClient):
    def get_method(self): return u'CONNECT'
    
# someday our PATCH will come!     http://tools.ietf.org/html/rfc5789


    