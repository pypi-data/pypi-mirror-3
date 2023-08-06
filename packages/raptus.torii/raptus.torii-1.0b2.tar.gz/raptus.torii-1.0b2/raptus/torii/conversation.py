import sys, os
import cPickle
import threading
import Zope2
import Globals
from copy import copy
from Testing.makerequest import makerequest
from codeop import compile_command
from raptus.torii import config
from raptus.torii import carrier


class Conversation(threading.Thread):
    
    def __init__(self, connection, configuration):
        super(Conversation, self).__init__()
        self.connection = connection
        self.configuration = configuration
        self.locals = copy(configuration.utilities)
        
        self.interpreter = configuration.interpreter(self.locals)

        self.arguments = self.conversation(carrier.FetchArguments()).arguments
        self.locals.update(arguments=self.arguments)
        self.locals.update(conversation=self.conversation)
        self.conversation(carrier.BuildReadline(self.interpreter.getReadline()))
    def run(self):
        dbConnection = Zope2.DB.open()
        application=Zope2.bobo_application(connection=dbConnection)
        application=makerequest(application)
        self.locals.update(app=application)

        for func in self.configuration.utilities.values():
            getattr(func, 'func_globals', {}).update(self.locals)

        for name, func in self.configuration.properties.items():
            if hasattr(func, 'func_code'):
                di = func.func_globals
                di.update(self.locals)
                res = eval(func.func_code,di)
                self.locals.update({name:res})
                continue
            try:
                res = func()
                self.locals.update({name:res})
                continue
            except:
                self.locals.update({name:func})

        mode = dict(    help = lambda: self.conversation(carrier.PrintHelpText()),
                        debug = self.interactiveMode,
                        list = self.listScripts,
                        run = self.runScript,
                   )
        if not Globals.DevelopmentMode:
            msg  = """
                       Sorry, but run the debug mode on productive Zope is too risky!
                       Pleas stop your Server and run it in the Foreground (fg) mode.
                   """
            mode.update(dict(debug=lambda: self.conversation(carrier.PrintText(msg))))


        try:
            if len(self.arguments) > 1 and self.arguments[1] in mode:
                mode[self.arguments[1]]()
            else:
                mode['help']()
            self.conversation(carrier.ExitTorii())
                
        except:
            dbConnection.transaction_manager.abort()
            dbConnection.close()
            self.connection.close()

    def listScripts(self):
        self.conversation(carrier.PrintText('here is a list with all available scripts:\n'))
        for name, path in self.configuration.scripts.items():
            self.conversation(carrier.PrintText(' '*10+name))

    def runScript(self):
        name = self.arguments[2]
        path = self.configuration.scripts.get(name, None)
        if path is None:
            self.conversation(carrier.PrintText("Sorry, but this script dosen't exist"))
            return
        f = file(path)
        code = compile_command(f.read(),path,'exec')
        if code is None:
            self.conversation(carrier.PrintText('script is not finished, blank line at the end missing?'))
        f.close()
        self.interpreter.runcode(code)
        stderr = self.interpreter.getErrorStream()
        if stderr.len:
            self.conversation(carrier.SendStderr(stderr))

    def interactiveMode(self):
        self.conversation(carrier.PrintText('Available global variables:'))
        for key in self.locals.keys():
            self.conversation(carrier.PrintText(key))
        
        while True:
            self.interpreter.resetStream()
            
            input = self.conversation(carrier.GetCodeLine(self.interpreter.getPrompt1()))
            try:
                while self.interpreter.push(input.line):
                    input = self.conversation(carrier.GetNextCodeLine(self.interpreter.getPrompt2()))
            except Exception, mesg:
                pass

            stderr = self.interpreter.getErrorStream()
            if stderr.len:
                self.conversation(carrier.SendStderr(stderr))
            stderr = self.interpreter.getSyntaxErrorStream()
            if stderr.len:
                self.conversation(carrier.SendStderr(stderr))
            stdout = self.interpreter.getStdout()
            if stdout.len:
                self.conversation(carrier.SendStdout(stdout, self.interpreter.getPromptOut()))


    def conversation(self, carrierObject):
        cPickle.dump(carrierObject, self.connection.makefile())
        while True:
            obj = cPickle.load(self.connection.makefile())
            if isinstance(obj, carrier.BaseCarrier):
                break;
            else:
                obj.executable(self.interpreter)
                cPickle.dump(obj, self.connection.makefile())
        return obj

    
