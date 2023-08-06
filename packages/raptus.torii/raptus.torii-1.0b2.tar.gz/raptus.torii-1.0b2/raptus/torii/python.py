import sys
import code
import StringIO
from raptus.torii.interpreter import AbstractInterpreter

class InteractiveConsole(code.InteractiveConsole):
    errstream = StringIO.StringIO()
    def write(self, data):
        self.errstream.write(data)
    def flushErr(self):
        self.errstream = StringIO.StringIO()

class Outputcache(object):
    output = StringIO.StringIO()
    def __call__(self, arg):
        if arg is not None:
            self.output.write(arg)

    def flush(self):
        self.output = StringIO.StringIO()

class Python(AbstractInterpreter):
    """ default interpreter for torii
    """

    def __init__(self, locals):
        self.console = InteractiveConsole(locals)
        self.outputcache = Outputcache()

    def getPrompt1(self):
        return '>>> '

    def getPrompt2(self):
        return '... '

    def getPromptOut(self):
        return ''

    def getReadline(self):
        return None

    def resetStream(self):
        self.outputcache.flush()
        self.console.flushErr()
        
    def push(self, line):
        displayhook_old = sys.displayhook
        sys.displayhook = self.outputcache
        return self.console.push(line)
        sys.displayhook = displayhook_old
        
    def runcode(self,code):
        displayhook_old = sys.displayhook
        sys.displayhook = self.outputcache
        self.console.runcode(code)
        sys.displayhook = displayhook_old
    
    def complete(self, text):
        return []
    
    def getStdout(self):
        return self.outputcache.output
    
    def getErrorStream(self):
        return self.console.errstream
    
    def getSyntaxErrorStream(self):
        return StringIO.StringIO()
    
