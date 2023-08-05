"""!


"""

class SSPYInterfaceError(Exception):

    pass



def parse(arg):
    """

    Borrowed from the Python.org Turtle Shell example
    
    Convert a series of zero or more numbers to an argument tuple
    """
    return tuple(map(int, arg.split()))

        
#---------------------------------------------------------------------------


class SSPYInterface:
    """!

    SSPy is a stateless program that simply loads and runs a
    declarative schedule. The SSPy interface creates states
    for working with sspy internal services, solvers, inputs,
    and outputs dynamically.
    """
    def __init__(self, scheduler=None):

        if scheduler is None:

            raise SSPYInterfaceError("No valid sspy object to interface to")

        self.scheduler = scheduler

        self.cwe = None
        
#---------------------------------------------------------------------------

    def __del__(self):
        """
        Do any cleanup here. Possibly a save dump to
        preserve any work.
        """
        self.scheduler = None

#---------------------------------------------------------------------------

    def get_version(self):

        print "%s (%s)" % (self.scheduler.GetVersion(), self.scheduler.GetRevisionInfo())

#---------------------------------------------------------------------------


    def set_cwe(self, element):

        self.cwe = cwe

#---------------------------------------------------------------------------

    def get_cwe(self, element):

        return self.cwe 
        

#---------------------------------------------------------------------------

    def run(self, arg):

        args = arg.split()

        if len(args) > 2:

            print ""
        time = float(arg)

        try:

            self.scheduler.Run(time)

        except Exception, e:

            print "%s" % e

#---------------------------------------------------------------------------

    def help_run(self):
        pass

#---------------------------------------------------------------------------

    def shell_command(self, arg):

        "Run a shell command"
        print "running shell command:", arg
        output = os.popen(arg).read()
        print output

#---------------------------------------------------------------------------

    def list_solver_plugins(self, arg):

        verbose = False
        
        if arg == 'v' or arg == 'verbose':

            verbose = True

        try:
            
            self.scheduler.ListSolverPlugins(verbose)

        except Exception, e:

            print "%s" % e
            
#---------------------------------------------------------------------------

    def list_output_plugins(self, arg):

        verbose = False
        
        if arg == 'v' or arg == 'verbose':

            verbose = True

        try:
            
            self.scheduler.ListOutputPlugins(verbose)

        except Exception, e:

            print "%s" % e

#---------------------------------------------------------------------------


    def list_input_plugins(self, arg):

        verbose = False
        
        if arg == 'v' or arg == 'verbose':

            verbose = True

        try:
            
            self.scheduler.ListInputPlugins(verbose)

        except Exception, e:

            print "%s" % e

#---------------------------------------------------------------------------

    def list_service_plugins(self, arg):

        verbose = False
        
        if arg == 'v' or arg == 'verbose':

            verbose = True

        try:
            
            self.scheduler.ListServicePlugins(verbose)

        except Exception, e:

            print "%s" % e

#---------------------------------------------------------------------------

    def load_input(self, arg):

        try:
            
            self.scheduler.LoadInput(arg)

        except Exception, e:

            print "%s" % e
        
#---------------------------------------------------------------------------

