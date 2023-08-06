import sys
import socket
import cPickle
import StringIO
from optparse import OptionParser
from raptus.torii import config

class Client(object):
    
    """
                                                            
            .....:::::::MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM   
  OMMMMMMMMMMMMMMMMMMMMMMM   MMMMMMMMMMMMMMMMMMMMMMM~MM     
   MM 8M MMM   M  MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM      
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM,NM MM                
             M MD                       M MM                
             M MM?                   ==MMIMMM88NMMM         
        MMMMMM MMMMMMMMMMMMMMMMMMMMMMMM MIMM   M  M         
        MMM MM MMMMMMMMMMMMMMMMMMMMMMMMMM MMMMMMMMM         
             M M                        M MM                
             MMM                        MIMM                
             MMM                        MIMM                
             M?M                        M MM                
             MMM                        M MM                
             MMM                        MIMM                
             MMM                        M~MM                
             MMM                        M7MM                
             7MM                        MIMM                
             7MM                        MIMM                
             IMM                        M7MM                
              MM                        MIMM                
             7MM                        MIMM                
             :::                        MDMM                
    
    
     Torii is a traditional Japanese gate most commonly 
     found at the entrance of or within a Shinto shrine.
     But in the zopy-world raptus.torii provide a gate to a
     running zope-server (holy-zopy). The access to the server can be
     get of differnt ways. here the manual:


     help          this help
                  
     debug         interactive mode
                 
     list          summary-list of all available scripts

     run <script>  run the given script



    """
              
    
    def __init__(self, path):
        self.path = path
        
    
    def main(self):
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.path)
            while True:
                carrier = cPickle.load(self.sock.makefile())
                carrier.executable(self)
                cPickle.dump(carrier, self.sock.makefile())
        except socket.error, msg:
                    print >> sys.stdout, msg
        except KeyboardInterrupt:
            pass
        print >> sys.stdout, '\n'
        self.sock.close()


