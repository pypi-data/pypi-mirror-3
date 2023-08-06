import urllib2, json, base64

class MobileWorks:
    
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
    
    task_url = 'https://work.mobileworks.com/api/v2/task/'
    job_url = 'https://work.mobileworks.com/api/v2/job/'
    
    def __init__( self, username, password ):
        self.credentials = base64.encodestring( username + ':' + password )[:-1]

    def __make_request( self, url, method = None, post_data = None ):
        """
        Creates and sends an HTTP request.
        """
        req = MobileWorks.Request( url, method = method, data = post_data )
        req.add_header( 'Authorization', 'Basic ' + self.credentials )
        
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
    
    def post_task( self, **task_params ):
        """
        Posts a task to API and returns the URL of the created task.
        """
        return self.__make_request( self.task_url, 'POST', json.dumps( task_params ) )['Location']
        
    def retrieve_task( self, task_url ):
        """
        Gets the information of the task located in `task_url`.
        """
        return self.__make_request( task_url )
    
    def delete_task( self, task_url ):
        """
        Deletes the task located in `task_url`.
        """
        return self.__make_request( task_url, 'DELETE' )
        
    def post_job( self, **job_params ):
        """
        Posts a job to API and returns the URL of the created job.
        """
        return self.__make_request( self.job_url, 'POST', json.dumps( job_params ) )['Location']
    
    def retrieve_job( self, job_url ):
        """
        Gets the information of the job located in `job_url`.
        """
        return self.__make_request( job_url )
    
    def delete_job( self, job_url ):
        """
        Deletes the job located in `job_url`.
        """
        return self.__make_request( job_url, 'DELETE' )
