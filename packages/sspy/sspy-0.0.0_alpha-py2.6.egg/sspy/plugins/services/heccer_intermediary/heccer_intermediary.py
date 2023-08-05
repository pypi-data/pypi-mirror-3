"""
This is the solver plugin for Heccer to interact with
the interface of SSPy.
"""
import os
import pdb
import sys

try:

    from heccer import Heccer
    from heccer import Compartment
    from heccer import Intermediary
    
except ImportError, e:

    sys.exit("Error importing the Heccer Python module: %s\n" % e)



class Service:

#---------------------------------------------------------------------------
    def __init__(self, name="Untitled Heccer Intermediary", plugin=None,
                 arguments=None, verbose=False):

        self._name = name

        self._plugin_data = plugin

        self.verbose = verbose

        self._intermediary = None

        self._method = ""

        self._ParseArguments(arguments)

#---------------------------------------------------------------------------

    def GetCore(self):
        """
        @brief Returns the constructed Heccer intermediary
        """
        return self._intermediary
    
#---------------------------------------------------------------------------

    def GetName(self):

        return self._name


#---------------------------------------------------------------------------

    def GetType(self):

        return self._plugin_data.GetName()

#---------------------------------------------------------------------------

    def GetPluginName(self):

        return self._plugin_data.GetName()

#---------------------------------------------------------------------------

    def GetArguments(self):

        return self._arguments

#---------------------------------------------------------------------------            
    def SetParameter(self, path, field, value):
        """!
        @brief Set's a parameter on the service
        """
        print "Setting parameters is not avaialable on the Heccer Intermediary"

        return

#---------------------------------------------------------------------------

    def GetCoordinates(self):

        print "Getting coordinates is not available on the Heccer Intermediary"
    
        return None
    
#---------------------------------------------------------------------------            

    def _ParseArguments(self, arguments):
        """

        """
        method = ""
        
        comp2mech = []

        num_compartments = -1

        compartments = []

        if arguments.has_key('method'):

            method = arguments['method']

        if arguments.has_key('comp2mech'):

            comp2mech = arguments['comp2mech'] 
            
        if arguments.has_key('iCompartments'):

            # Probably won't need this since I can determine
            # the number of compartments easily.
            num_compartments = arguments['iCompartments']
                
        if arguments.has_key('compartments'):

            compartments = self._CreateCompartmentArray(arguments['compartments'])

        # Sets the arguments so we can retrieve them
        self._arguments = arguments

        self._intermediary = Intermediary(compartments, comp2mech)

        
#---------------------------------------------------------------------------

    def _CreateCompartmentArray(self, compartments):

        compartment_list = []

        try:
            
            for c in compartments:

                comp = Compartment()

                if c.has_key('dCm'):

                    comp.dCm = float(c['dCm'])

                if c.has_key('dEm'):

                    comp.dEm = c['dEm']
                
                if c.has_key('dInitVm'):

                    comp.dInitVm = c['dInitVm']
                
                if c.has_key('dRa'):

                    comp.dRa = c['dRa']

                if c.has_key('dRm'):

                    comp.dRm = float(c['dRm'])

                compartment_list.append(comp)

        except TypeError, e:

            raise Exception("Invalid arguments, cannot create Heccer Intermediary: %s", e)
            
        return compartment_list

