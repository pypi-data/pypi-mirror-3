import sys


class BaseCarrier(object):
    """ The communicatin between ZopeServer and Client goes over the instance BaseCarrier.
        The server send a pickle-instance to the client. The clinet recive the object and run
        a executable methode on this class. After all this the client send the object back
        to the ZopeServer.
    """
    
    def executable(self, client):
        """ this methode is called from the clinet
            each time while recived this object.
        """
        print "ooops you need to override this methode in the BaseCarrier"
        
class BaseCounterCarrier(object):
    """ CounterCarrier is a request from the client to the server.
    """
    def executable(self, interpreter):
        print 'override this methode in counterCarrier'
    
    
    
class FetchArguments(BaseCarrier):
    
    def executable(self, client):
        self.arguments = sys.argv

class BuildReadline(BaseCarrier):
    def __init__(self, readline):
        self.readline = readline
    
    def executable(self, client):
        if self.readline is not None:
            self.readline(client)

class GetCodeLine(BaseCarrier):
    
    def __init__(self, prompt ):
        self.prompt = prompt
    def executable(self, client):
        self.line = raw_input(self.prompt)
        

class GetNextCodeLine(GetCodeLine):
    
    def executable(self, client):
        self.line = raw_input(self.prompt)


class SendStdout(BaseCarrier):
    
    def __init__(self, stringIO, prompt=''):
        self.stringIO = stringIO
        self.prompt = prompt
    
    def executable(self, client):
        self.stringIO.seek(0)
        sys.stdout.write(self.prompt)
        for out in self.stringIO:
            print >> sys.stdout, out


class SendStderr(SendStdout):
    
    def executable(self, client):
        self.stringIO.seek(0)
        for out in self.stringIO:
            print >> sys.stderr, out

class PrintHelpText(BaseCarrier):
    
    def executable(self, client):
        print >> sys.stdout, client.__doc__

class PrintText(BaseCarrier):
    
    def __init__(self, text):
        self.text = text
    
    def executable(self, client):
        print >> sys.stdout, self.text

class ExitTorii(BaseCarrier):
    
    def executable(self, client):
        client.sock.close()
        sys.exit()

class FetchCompleter(BaseCounterCarrier):
    def __init__(self, text, state):
        self.text = text
        self.state = state
    def executable(self, interpreter):
        self.result = interpreter.complete(self.text)
