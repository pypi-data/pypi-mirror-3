from coils.core import *
import ftpserver

class CoilsAuthorizer(ftpserver.DummyAuthorizer):
    # Read permissions:
    #   - "e" = change directory (CWD command)
    #   - "l" = list files (LIST, NLST, STAT, MLSD, MLST commands)
    #   - "r" = retrieve file from the server (RETR command)
    #
    #  Write permissions:
    #   - "a" = append data to an existing file (APPE command)
    #   - "d" = delete file or directory (DELE, RMD commands)
    #   - "f" = rename file or directory (RNFR, RNTO commands)
    #   - "m" = create directory (MKD command)
    #   - "w" = store a file to the server (STOR, STOU commands)   
   
    def add_user(self, username, password, homedir, perm='elr',
                    msg_login="Login successful.", msg_quit="Goodbye."):
        raise NotImplementedException('FTP users cannot be defined.') 
        
    def add_anonymous(self, homedir, **kwargs):
        raise NotImplementedException('FTP users cannot be defined.') 
    
    def remove_user(self, username):
        raise NotImplementedException('FTP users cannot be defined.')         
    
    def override_perm(self, username, directory, perm, recursive=False):
        """Override permissions for a given directory."""    
        raise NotImplementedException('Not implemented.')         
    
    def has_user(self, username):
        raise NotImplementedException('Not implemented.')
        
    def has_perm(self, username, perm, path=None):
        """Whether the user has permission over path (an absolute
        pathname of a file or a directory).

        Expected perm argument is one of the following letters:
        "elradfmw".
        """ 
        return True 
        
    def get_perms(self, username):
        """Return current user permissions."""
        return 'elradfmw'
    
    def validate_authentication(self, username, password):
        try:
            ctx = AuthenticatedContext(metadata= { 'authentication': { 'login':     username,
                                                                       'mechanism': 'PLAIN',
                                                                       'secret':    password } } )
            self._ctx = ctx
        except:
            return False
        else:
            return True
            
    def get_msg_login(self, username):
        return 'fred'
        
    def get_home_dir(self, username):
        return '/tmp'

