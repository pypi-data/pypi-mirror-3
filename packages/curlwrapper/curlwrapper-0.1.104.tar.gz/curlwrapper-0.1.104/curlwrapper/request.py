import urllib
import mimetypes
import time

class Request:
    """This is the Request object that contains the tricky stuff 
    for a http request"""
    def __init__(self, url='', post=None, referer=None, 
            proxy=None, headers={}, forbid_redirect=False,
            trycount=None, fd=None, onprogress=None, only_head=False, multipart=False, 
            method = "GET"):
        """Download an URL with GET or POST methods.

        @param post: It can be a string that will be POST-ed to the URL.
            When None is given, the method will be GET instead.
        @param extraheaders: You can add/modify HTTP headers with a dict here.
        @param forbid_redirect: Set this flag if you do not want to handle
            HTTP 301 and 302 redirects.
        @param trycount: Specify the maximum number of retries here.
            0 means no retry on error. Using -1 means infinite retring.
            None means the default value (that is self.trycount).
        @param fd: You can pass a file descriptor here. In this case,
            the data will be written into the file. Please note that
            when you save the raw data into a file then it won't be cached.
        @param onprogress: A function that has two parameters:
            the size of the resource and the downloaded size. This will be
            called for each 1KB chunk. (If the HTTP header does not contain
            the content-length field, then the size parameter will be zero!)
        @param only_head: Create the openerdirector and return it. In other
            words, this will not retrieve any content except HTTP headers.
        @param multipart: only if we are using the curl multi part functions

        @return: The raw HTML page data, unless fd was specified. When fd
            was given, the return value is undefined.
        """

        #unimplemented
        self.cookies = []
        #implemented
        self.url = url
        self.referer = referer

        self.multipart = multipart 

        if post:
            if isinstance(post, dict):
                for k, v in post.items():
                    post[k] = v.encode('utf-8')
                self.post = urllib.urlencode(post)
            elif isinstance(post, list) and not self.multipart:
                self.post = urllib.urlencode(post)  
            if self.method == "GET":
                self.method = "POST"
        self.method = method
        self.post = post
        self.proxy = proxy
        self.tries = 0
        self.headers = headers
        self.only_head = only_head
        
        return None    
	
    def encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = "---------------------------%s" % (int(time.time()))
        CRLF = '\r\n'
        l = []
        for (key, value) in fields:
            l.append('--' + BOUNDARY)
            l.append('Content-Disposition: form-data; name="%s"' % key)
            l.append('')
            l.append(value)
        for (key, filename, value) in files:
            l.append('--' + BOUNDARY)
            l.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            l.append('Content-Type: %s' % self.get_content_type(filename))
            l.append('')
            l.append(value)
        l.append('--' + BOUNDARY + '--')
        l.append('')
        body = CRLF.join(l)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        self.post = body
        self.headers['Content-Type'] = content_type
        return content_type, body

    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


