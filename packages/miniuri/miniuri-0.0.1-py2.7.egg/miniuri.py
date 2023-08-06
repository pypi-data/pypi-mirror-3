class Uri( object ):
    """
    This is a universal URI parser class.
    Pass a URI string in for access to the following attributes: 

    foo://username:password@test.com:808/go/to/index.php?pet=cat&name=bam#eye
    \_/   \_______________/ \______/ \_/       \___/ \_/ \_______________/\_/
     |           |             |      |          |    |       |            | 
     |       userinfo       hostname  |          |    |      query   fragment
     |    \___________________________|/\________|____|_/
     |                  |             |      |   |    |
    scheme          authority         |    path  |  extension
                                      |          |
                                     port     filename

    This example shows how you can set and get any of the URI attributes:
    .. code-block:: python

     >>> from miniuri import Uri
     >>> u = Uri( "http://www.foxhop.net/samsung/HL-T5087SA/red-LED-failure" )
     >>> u.uri = "https://fox:pass@www.foxhop.net:81/path/filename.jpg?p=2#5"
     >>> print u.uri
     https://fox:pass@www.foxhop.net:81/path/filename.jpg?p=2#5
     >>> print u.hostname
     www.foxhop.net
     >>> print u.scheme
     https
     >>> u.username = 'max'
     >>> print u
     https://max:pass@www.foxhop.net:81/path/filename.jpg?p=2#5
    """

    def __init__( self, uri = None ):
        if uri: self.uri = uri # invoke uri.setter

    @property
    def uri( self ):
        """build and return uri from attributes"""
        scheme = path = filename = query = fragment = ''
        if self.path: path = '/'.join( self.path.split('/')[:-1] )
        if self.scheme: scheme = self.scheme + '://'
        if self.filename: filename = '/' + self.filename
        if self.query: query = '?' + self.query
        if self.fragment: fragment = '#' + self.fragment
        return ''.join( [scheme, self.authority, path, filename, query, fragment] )

    @uri.setter
    def uri( self, uri ):
        """parse and set all uri attributes"""
        self.scheme = self.username = self.password = None
        self.hostname = self.port = self.path = None
        self.filename = self.query = self.fragment = None 

        if '://' in uri: # attempt to parse scheme
            self.scheme, uri = uri.split( '://' )

        # invoke authority setter
        self.authority = uri.split( '/' )[0]

        uri = uri[ len( self.authority ): ] 

        if '#' in uri: # set fragment
            uri, self.fragment = uri.split( '#' )  
        
        if '?' in uri: # set path and possibly query
            self.path, self.query = uri.split( '?' )
        else: self.path = uri
        
        self.filename = self.path.split( '/' )[-1]
        
    @property
    def authority( self ):
        """return a authority string from attributes"""
        a = ''
        if self.username:
            a += self.username
            if self.password: a += ':' + self.password
            a += '@'
        a += self.hostname
        if self.port: a += ':' + self.port
        return a

    @authority.setter
    def authority( self, a ):
        """set all the attribute that makeup a authority"""
        self.username = self.password = self.port = None
        self.hostname = a
        if '@' in a:
            self.userinfo, self.hostname = a.split( '@' ) # userinfo setter
        if ':' in self.hostname:
            self.hostname, self.port = self.hostname.split( ':' )

    @property
    def userinfo( self ):
        """return username:password"""
        if self.username and self.password: 
            return self.username + ':' + self.password
        if self.username: return self.username
        else: return None

    @userinfo.setter
    def userinfo( self, info ):
        """set username and password"""
        self.username, self.password = info, None 
        if ':' in info:
            self.username, self.password = info.split( ':' )

    @property
    def extension( self ):
        """return extension"""
        if '.' in self.filename: return self.filename.split('.')[-1]
        else: return None 

    @property
    def parts( self ):
        """remove scheme then return a list of uri parts splitting on / """
        p = self.uri
        if self.scheme: p = p[ len(self.scheme) + 3: ]
        return p.split( '/' )

    def __str__( self ): return self.uri
