

class AbstractInterpreter(object):
    
    def __init__(self, locals):
        pass

    def getPrompt1(self):
        """ return prompt like >>>
        """

    def getPrompt2(self):
        """ return prompt like ...
        """

    def getPromptOut(self):
        """ return prompt like Out[0]
        """

    def getReadline(self):
        """ return a  callable-object or a function to set the readline on the client
        """

    def resetStream(self):
        """ reset stdout and stderr stream. Called each time before
            a command is executed.
        """

    def push(self, line):
        """ push a single code line
        """
    
    def runcode(self,code):
        """ run a code-object
        """
    
    def complete(self, text):
        """ code completion
        """
    
    def getStdout(self):
        """ get the stdout for this cycle
        """
    
    def getErrorStream(self):
        """ return all generated errors in this cycle
        """
    def getSyntaxErrorStream(self):
        """ return all generated syntax-errors in this cycle
        """
    