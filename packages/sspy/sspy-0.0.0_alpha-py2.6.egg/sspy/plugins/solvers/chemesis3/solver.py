"""
This is the solver plugin for Heccer to interact with
the interface of SSPy.
"""
import os
import pdb
import sys

try:
    from chemesis3 import Chemesis3

except ImportError, e:

    sys.exit("Error importing the chemesis3 module: %s\n" % e)


class Solver:

#---------------------------------------------------------------------------

    def __init__(self,  name="Untitled solver", plugin=None, 
                 constructor_settings=None, verbose=False):
        """

        Should be able to pass the scheudler and use it as
        an internal member here.
        """
        self._name = name

        self._model_name = name

        self._plugin_data = plugin

        self.verbose = verbose
        
        self._chemesis3 = None

        self._module_name = None

        self.time_step = None

        self.granularity = 1

        self._constructor_settings = {}
        
        self._configuration = {}
            
        self._compiled = False

        self.options = 0

        # this is just to keep track of granularity printing
        self.current_step = 0

        self._ParseConstructorSettings(constructor_settings)

        #self._heccer.SetTimeStep(time_step)

#---------------------------------------------------------------------------
        
    def Initialize(self):

        self.current_step = 0
        
        self._chemesis3.Initiate()

#---------------------------------------------------------------------------

    def GetCore(self):

        return self._chemesis3

#---------------------------------------------------------------------------

    def GetName(self):

        return self._name

#---------------------------------------------------------------------------


    def SetTimeStep(self, time_step):
        """
        @brief Sets the heccer time step
        """
        if not self._chemesis3 is None:
        
            self._chemesis3.SetTimeStep(time_step)

        else:

            self.time_step = time_step

#---------------------------------------------------------------------------

    def GetTimeStep(self):
        """
        @brief Just returns the time step used for the schedulee
        """
        if not self._chemesis3 is None:

            time_step = self._chemesis3.GetTimeStep()

            return time_step
        
        else:
            
            return self.time_step
    
#---------------------------------------------------------------------------

    def GetType(self):

        return self._plugin_data.GetName()


#---------------------------------------------------------------------------

    def SetConfiguration(self, config):

        pass

#---------------------------------------------------------------------------

    def New(self, modelname, filename):

        print "Modelname %s, Filename %s" % (modelname, filename)
        

#---------------------------------------------------------------------------

    def Advance(self):

        pass

#---------------------------------------------------------------------------

    def Compile(self):
        """
        @brief 
        """

        if self._compiled is False:

            self._chemesis3.Compile()

            self._compiled = True

#---------------------------------------------------------------------------

    def IsCompiled(self):

        return self._compiled

#---------------------------------------------------------------------------

    def Connect(self, service=None):
        """!
        @brief Connects a service to the this solver

        Compatible services need to be coded into this method.

        """

        if not service:

            raise Exception("No service to connect to solver '%s'" % self.GetName())


        service_type = service.GetType()
                

        if service_type == "model_container":

            model_container = service.GetCore()

            if not model_container:

                raise Exception("Model Container is not defined")

            else:

                self._chemesis3 = Chemesis3(name=self._model_name, model=model_container)


        else:

            raise Exception("Incompatible Service '%s' of type '%s'" % (service.GetName(), service.GetType()))

        # Set any simulator specific variables here
        if not self.time_step is None:

            self._chemesis3.SetTimeStep(float(self.time_step))



#---------------------------------------------------------------------------

    def SetModelName(self, model_name):
        """!
        @brief Sets the model name for the solver to connect to

        Since a solver can target a particular part of the model
        to solve we need to set this field to let it know which.
        It is not used until heccer connection. 
        """
        self._model_name = model_name

#---------------------------------------------------------------------------

    def SetGranularity(self, granularity):
        """!
        @brief sets the granularity of the solver output
        """
        self.granularity = granularity

#---------------------------------------------------------------------------

    def Deserialize(self, filename):

        pass

#---------------------------------------------------------------------------

    def DeserializeState(self, filename):

        pass

#---------------------------------------------------------------------------

    def Finish(self):

        pass

#---------------------------------------------------------------------------

    def Name(self):

        return self._name

#---------------------------------------------------------------------------

    def SetSolverField(self, field, value):

        pass

#---------------------------------------------------------------------------

    def GetSolverField(self, field):

        pass

#---------------------------------------------------------------------------


    def Serialize(self, filename):

        pass

#---------------------------------------------------------------------------

    def SerializeState(self, filename):

        pass

#---------------------------------------------------------------------------
        
    def Output(self, serial, field):

        print "Serial and field is %s:%s" % (serial, field)

#---------------------------------------------------------------------------

    def Run(self, time):

        print "Simulation time is %s" % time

#---------------------------------------------------------------------------

    def Step(self, time=None):
        """

        """
        if self._chemesis3 is not None:

            self._chemesis3.Step(time)

            self.current_step += 1
        else:

            raise Exception("No simulation time given")

#---------------------------------------------------------------------------

    def Report(self):

        granularity_result = self.current_step % self.granularity
        
        if granularity_result == 0:

            print "No 'Dump' method for Chemesis3"

#---------------------------------------------------------------------------

    def Steps(self, steps):

        pass

#---------------------------------------------------------------------------
  
    def _ParseConstructorSettings(self, constructor_settings=None):
        """
        @brief An internal helper method for parsing and setting constructor values
        
        """
        if constructor_settings is None:

            return 

        if constructor_settings.has_key('service_name'):

            self._service_name = constructor_settings['service_name']

        # This will probably be unneeded in python
        if constructor_settings.has_key('module_name'):

            self._module_name = constructor_settings['module_name']


        if constructor_settings.has_key('constructor_settings'):

            self._constructor_settings = constructor_settings['constructor_settings']
                
            if constructor_settings['constructor_settings'].has_key('configuration'):

                self._configuration = constructor_settings['constructor_settings']['configuration']


        if self._constructor_settings.has_key('dStep'):

            self.time_step = self._constructor_settings['dStep']

        elif self._constructor_settings.has_key('step'):

            self.time_step = self._constructor_settings['step']

 



