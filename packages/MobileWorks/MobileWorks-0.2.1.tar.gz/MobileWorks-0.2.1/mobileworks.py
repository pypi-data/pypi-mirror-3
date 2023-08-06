import urllib2, json, base64


class _API:
    """
    This is the base class for Task/Job.
    It contains the general methods for making API calls to MobileWorks
    """
    
    class Request( urllib2.Request ):
        """
        This class is an extension of urllib2.Request that allows requests other than GET/POST.
        """
        
        def __init__( self, url, data = None, headers = {},
                     origin_req_host = None, unverifiable = False, method = None ):
            """
            These parameters (except `method`) are the same as the parameters in the parent class `urllib2.Request`, which can be found here:
            http://docs.python.org/library/urllib2.html#urllib2.Request
            
            The `method` parameter was added to allow HTTP requests other than GET/POST.
            """
            self._method = method
            urllib2.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
        
        def get_method( self ):
            return self._method if self._method else urllib2.Request.get_method( self )
        
    @classmethod
    def _make_request( cls, url, method = None, post_data = None ):
        """
        Creates and sends an HTTP request.
        """
        if MobileWorks.credentials is None:
            raise Exception( 'You are not logged in.' )
        req = cls.Request( url, method = method, data = post_data )
        req.add_header( 'Authorization', 'Basic ' + MobileWorks.credentials )
        
        try:
            response = urllib2.urlopen( req )
            content = response.read()
            response.close()
            return json.loads( content )
        except urllib2.HTTPError, e:
            if e.code >= 500:
                raise Exception( 'HTTP %d: A server error occured' % e.code )
            else:
                raise Exception( 'HTTP %d: %s' % ( e.code, e.read() ) )
    
    PATH = ''
    
    def url( self ):
        return MobileWorks.DOMAIN + self.PATH
    
    def dict( self ):
        """
        This is used for json serialization.
        It should be overriden by subclasses.
        """
        return self.__dict__
    
    def to_json(self):
        return json.dumps( self.dict() )
    
    def post( self ):
        """
        Posts the object to MobileWorks API and returns the URL of the created object.
        """
        return self._make_request( self.url(), 'POST', self.to_json() )['Location']
    
    @classmethod
    def retrieve( cls, url ):
        """
        Gets the information of the object located at `url`.
        """
        return cls._make_request( url )
    
    @classmethod
    def delete( cls, url ):
        """
        Deletes the object located at `url`.
        """
        return cls._make_request( url, 'DELETE' )
    

class Task(_API):
    
    PATH = 'api/v2/task/'
    
    def __init__( self, **task_params ):
        self.params = task_params
        self.fields = None
        
    def set_params( self, **params ):
        """
        Sets parameters of this task.
        """
        self.params.update( params )
    
    def add_field( self, name, type, **kwargs ):
        """
        Adds a field to this task.
        """
        if self.fields is None:
            self.fields = []
            
        field = {name: type}
        if kwargs:
            field.update( kwargs )
        self.fields.append( field )
        
    def dict( self ):
        dic = self.params.copy()
        if self.fields is not None:
            dic.update( {'fields': self.fields} )
        return dic
        
    
class Job(_API):
    
    PATH = 'api/v2/job/'
    
    def __init__( self, **job_params ):
        self.params = job_params
        self.tasks = []
        
    def set_params( self, **params ):
        """
        Sets parameters of this job.
        """
        self.params.update( params )
        
    def add_task( self, task ):
        """
        Adds a task to this job.
        """
        if task.__class__ == Task:
            self.tasks.append( task )
        else:
            raise ValueError( "`task` must be an instance of the Task class" )
    
    def dict( self ):
        dic = self.params.copy()
        dic.update( {'tasks': [t.dict() for t in self.tasks]} )
        return dic
    

class MobileWorks:
    """
    This class is used to login to MobileWorks and keeps track of the user credentials and
    the DOMAIN used for the API. 
    """
    
    credentials = None
    DOMAIN = 'https://work.mobileworks.com/'
    PROFILE_PATH = 'api/v1/userprofile/?format=json'
    
    @classmethod
    def login( cls, username, password ):
        cls.credentials = base64.encodestring( username + ':' + password )[:-1]
        try:
            return _API._make_request(cls.DOMAIN + cls.PROFILE_PATH)['objects'][0]
        except Exception, e:
            print e
            cls.credentials = None
            raise Exception( "Couldn't login. To reset your password, please go to: " + cls.DOMAIN + 'accounts/password_reset/' )
    
        
    @classmethod
    def local(cls, port = 8000):
        cls.DOMAIN = 'http://localhost:%d/' % port
    
    @classmethod    
    def staging(cls):
        cls.DOMAIN = 'https://staging.mobileworks.com/'
        
    @classmethod
    def sandbox(cls):
        cls.DOMAIN = 'https://sandbox.mobileworks.com/'
        
    @classmethod
    def production(cls):
        cls.DOMAIN = 'https://work.mobileworks.com/'
