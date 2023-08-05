import os
from coils.core import *
import ftpserver
from filesystem import CoilsFilesystem
from authorizer import CoilsAuthorizer
        
        
if __name__ == "__main__":
   
    initialize_COILS()
   
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = ftpserver.DummyAuthorizer()
   
    # Define a new user having full r/w permissions and a read-only
    # anonymous user
   
    # Instantiate FTP handler class
    ftp_handler = ftpserver.FTPHandler
    ftp_handler.authorizer = CoilsAuthorizer()
    ftp_handler.abstracted_fs = CoilsFilesystem
   
    # Define a customized banner (string returned when client connects)
    ftp_handler.banner = "pyftpdlib %s based ftpd ready." %ftpserver.__ver__
   
    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    #ftp_handler.masquerade_address = '151.25.42.11'
    #ftp_handler.passive_ports = range(60000, 65535)
   
    # Instantiate FTP server class and listen to 0.0.0.0:21
    address = ('', 21000)
    ftpd = ftpserver.FTPServer(address, ftp_handler)
   
    # set a limit for connections
    ftpd.max_cons = 256
    ftpd.max_cons_per_ip = 5
   
    # start ftp server
    ftpd.serve_forever()
