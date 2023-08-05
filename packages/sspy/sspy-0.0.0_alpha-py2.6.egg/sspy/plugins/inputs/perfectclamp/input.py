"""
This is the input plugin for connecting an input
to a model.
"""
import os
import pdb
import sys

try:

    from experiment.perfectclamp import PerfectClamp

except ImportError, e:

    sys.exit("Error importing the experiment perfectclamp python module: %s\n" % e)


#---------------------------------------------------------------------------

class InputError(Exception):
    pass

#---------------------------------------------------------------------------

class Input:

    """!
    @brief class object for a perfectclamp input
    """
    
#---------------------------------------------------------------------------

    def __init__(self, name="Untitled PerfectClamp", plugin=None,
                 arguments=None, verbose=False):


        self._name = name

        self._plugin_data = plugin

        self.verbose = verbose

        self.time_step = 0.0
        
        self._perfectclamp = None
        
        self._inputs = []

        self.command_voltage = None

        self.command_file = None

        self._solver = None

        self._perfectclamp = PerfectClamp(self._name)

        self._ParseArguments(arguments)


#---------------------------------------------------------------------------

    def Format(self):
        
        """
        @brief Prints the text block format that is parsed for the input
        """
        return self._plugin_data.GetFormat()
            
#---------------------------------------------------------------------------

    def GetName(self):
        """
        @brief 
        """
        return self._name

#---------------------------------------------------------------------------

    def Name(self):

        return self._name

#---------------------------------------------------------------------------
    def GetTimeStep(self):
        """
        """
        
        return self.time_step

#---------------------------------------------------------------------------

    def SetTimeStep(self, time_step):
        """
        """
        
        self.time_step = time_step

#---------------------------------------------------------------------------
    

    def GetType(self):

        return self._plugin_data.GetName()

#---------------------------------------------------------------------------
    
    def AddInput(self, name, field):

        if self._solver is None:

            self._inputs.append(dict(field=field,compnent_name=name))

#            raise Exception("Can't add input to %s, it is not connected to a solver" % self.GetName())

        else:

            solver_type = self._solver.GetType()

            if solver_type == "heccer":

                my_heccer = solver.GetCore()
                
                address = my_heccer.GetCompartmentAddress(component_name, field)

                self._perfectclamp.AddInput(address)

#---------------------------------------------------------------------------

    def SetInputs(self, inputs):
        """!
        @brief Sets the inputs for this object
        """
        self._inputs = inputs

#---------------------------------------------------------------------------

    def SetCommandVoltage(self, voltage):

        self._perfectclamp.SetCommandVoltage(voltage)

        self.command_voltage = voltage
        
#---------------------------------------------------------------------------

    def Advance(self):

        pass


#---------------------------------------------------------------------------

    def Connect(self, solver):
        """!
        @brief Connects the input to a solvers input variable

        To properly connect an input to a solver you must:


            1. Retrieve the timestep from the solver and set it
            with the SetTimeStep method to ensure the scheudlee
            properly updates the object.

            2. Connect the solver core to the input core.

            3. Add the inputs via whatever method the cores use
            to communicate.
        
        """

        time_step = solver.GetTimeStep()

        self.SetTimeStep(time_step)

        solver_type = solver.GetType()

        self.Initialize()

        component_name = ""
        field = ""

        for i, inp in enumerate(self._inputs):

            if inp.has_key('inputclass'):

                if inp['inputclass'] != 'perfectclamp':
                    # if this output is not meant
                    # for this object type then we
                    # continue and ignore it
                    continue

            if inp.has_key('component_name'):

                component_name = inp['component_name']

            else:

                print "Input Error, no component name for input %d" % i

                continue

            if inp.has_key('field'):

                field = inp['field']

            else:

                print "Input Error, no field given for input %d" % i

            if solver_type == 'heccer':

                my_heccer = solver.GetCore()
                
                address = my_heccer.GetCompartmentAddress(component_name, field)

                #exception?

                if self.verbose:

                    print "\tConnecting input variable '%s -> '%s' from solver '%s'" % (component_name, field, solver.GetName())
                    
                self._perfectclamp.AddInput(address)
                

#---------------------------------------------------------------------------

    def Finish(self):
        """

        """
        self._perfectclamp.Finish()

#---------------------------------------------------------------------------

    def Initialize(self):
        """!
        @brief Initializes the perfect clamp from any internal variables that were set
        """
        if self._perfectclamp is None:

            self._perfectclamp = PerfectClamp(self._name)

        if self._perfectclamp is None:

            raise Exception("Can't initialize the PerfectClamp object '%s'" % self._name)

        # Apply the parameters loaded or set via api

        if not self.command_voltage is None and not self.command_file is None:

            self._perfectclamp.SetFields(self.command_voltage, self.command_file)

        elif not self.command_voltage:
            
            self._perfectclamp.SetCommandVoltage(self.command_voltage)

#---------------------------------------------------------------------------

    def Reset(self):
        """!
        @brief Destroys and recreates the core perfectclamp object
        """

        
        self._perfectclamp = None

        self.Initialize()

#---------------------------------------------------------------------------

    def Compile(self):
        """
        @brief Compiles the perfectclamp input
        """
        self._perfectclamp.Compile()

#---------------------------------------------------------------------------

    def New(self):

        pass


#---------------------------------------------------------------------------

    def Step(self, time):
        """
        @brief performs a single step for the input
        """
        self._perfectclamp.Step(time)

#---------------------------------------------------------------------------

    def Report(self):

        pass

#---------------------------------------------------------------------------

    def _ParseArguments(self, arguments=None):
        """!
        @brief Parsed the input initialization data

        The block of yaml to parse looks like this:
            
          perfectclamp:
              module_name: Experiment
              options:
                  command: -0.06
                  name: purkinje cell perfect clamp
              package: Experiment::PerfectClamp

        Ignored Keys:

            ['perfectclamp']['package']
            ['perfectclamp']['module_name']
            
        """
        if arguments is None:

            return

        if arguments.has_key('perfectclamp'):

            configuration = arguments['perfectclamp']

        else:

            raise Exception("No 'perfectclamp' configuration block present")


        if configuration.has_key('options'):

            options = configuration['options']

            if options.has_key('command'):

                self.command_voltage = options['command']

            if options.has_key('name'):

                self._name = options['name']

            if options.has_key('filename'):

                self.command_file = options['filename']
            
#---------------------------------------------------------------------------


