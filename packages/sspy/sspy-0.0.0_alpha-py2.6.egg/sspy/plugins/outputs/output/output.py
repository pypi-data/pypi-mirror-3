"""
This is the output plugin for outputting data
from connected solvers
"""
import os
import pdb
import sys

try:

    import experiment.output as og

except ImportError, e:

    sys.exit("Error importing the Experiment Output Python module: %s\n" % e)


_default_filename = "/tmp/OutputGenerator"

class Output:

#---------------------------------------------------------------------------

    def __init__(self,  name="Untitled Output", plugin=None, filename=None,
                 arguments=None, verbose=False):

        self._name = name

        self._plugin_data = plugin

        self.verbose = verbose


        # should be inconsequential in an output object
        # it is only here for reporting purposes to keep
        # the object consistent when it's passed on to
        # the schedulee.
        self.time_step = 0.0
        
        self._output_gen = None

        self.filename = _default_filename

        self.format = None

        self.mode = None

        self.resolution = None
        
        self.outputs = []

        self._solver = None

        if not arguments is None:
            
            self._ParseArguments(arguments)

            

#---------------------------------------------------------------------------

    def Compile(self):
        """
        @brief 
        """
        self._output_gen.Compile()

#---------------------------------------------------------------------------

    def Finish(self):
        """
        @brief 
        """
        self._output_gen.Finish()

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

    def SetOutputs(self, outputs):
        """
        @brief Sets the list of outputs

        Needs to be saved for later since they cannot be set
        until the solver is created after a connect. 
        """
        
        self.outputs = outputs

#---------------------------------------------------------------------------

    def AddOutput(self, name, field):
        """!

        @brief Adds an output to the solver


        Performs a check for the solver type. Any issues after the solver check
        should throw an exception. 
        """

        if self._solver is None:
            # if it's none then we store it for later use

            self.outputs.append(dict(field=field,component_name=name))
            
#         if self._solver is None:

#             raise Exception("Can't add output to %s, it is not connected to a solver" % self.GetName())

        else:

            try:
                solver_type = self._solver.GetType()

                my_solver = self._solver.GetCore()

                address = my_solver.GetAddress(name, field)

                self._output_gen.AddOutput(name, address)
                
            except Exception, e:

                raise Exception("Output error: can't add output for %s, %s: %s" % (name, field, e))

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

    def Finish(self):

        self._output_gen.Finish()

#---------------------------------------------------------------------------

    def Initialize(self):

        # if the output object is not built declaratively
        # then it must be built here just before connection to a solver. 
        if self._output_gen is None:

            self._output_gen = og.Output(self.filename)

            if self._output_gen is None:

                raise Exception("Can't create output generator object '%s'" % self.GetName())

        # Here we set any output parameters we loaded into the plugin

        if not self.format is None:

            self._output_gen.SetFormat(self.format)


        if not self.mode is None:
            
            if self.mode == 'steps':
                        
                self._output_gen.SetSteps(1)


        if not self.resolution is None:

            self._output_gen.SetResolution(self.resolution)

#---------------------------------------------------------------------------

    def Reset(self):
        """!
        @brief Destroys and recreates the core output object
        """

        
        self._output_gen = None

        self.Initialize()


    
#---------------------------------------------------------------------------

    def Connect(self, solver):
        """!
        @brief Connects the output to a solver

        To properly connect a solver and an output you must:

            1. Retrieve the timestep from the solver and set it
            with the SetTimeStep method to ensure the scheudlee
            properly updates the object.

            2. Connect the solver core to the output core.

            3. Add the outputs via whatever method the cores use
            to communicate.

        """

        # Here we save a copy of the solver
        # in case we don't set any outputs during connection
        # but with to set them later (via shell)
        self._solver = solver
        
        solver_type = solver.GetType()

        # initialize the object at this point
        self.Initialize()

        # Shouldn't be needed anymore, it should work for both heccer and chemesis3
        #if solver_type == 'heccer':

        my_solver = solver.GetCore()

        # Here we need to get the timestep and set it
        # for our object
        time_step = my_solver.GetTimeStep()
            
        self.SetTimeStep(time_step)

        # Now after connection we can add any stored
        # outputs from a configuration. Otherwise
        # they can only be added after this connection step
        # has proceeded. 
        self._ParseOutputs()




#---------------------------------------------------------------------------


    def Step(self, time=None):
        """

        """
        self._output_gen.Step(time)


#---------------------------------------------------------------------------

    def Report(self):

        pass

#---------------------------------------------------------------------------

    def SetMode(self, mode=None):
        """

        """
            
        self.mode = mode

#---------------------------------------------------------------------------

    def SetResolution(self, res=None):
        """

        """
        self.resolution = res
            
            
#---------------------------------------------------------------------------

    def SetFormat(self, strfmt=None):
        """

        """

        self.format = strfmt

    
#---------------------------------------------------------------------------

    def SetFilename(self, filename=None):
        """
        
        """
        if not filename:

            return
        
        self.filename = filename

#---------------------------------------------------------------------------

    def GetFilename(self):

        return self.filename
        
#---------------------------------------------------------------------------

    def _ParseArguments(self, arguments):
        """
        @brief Parses the output initialization data

        Ignored keys:

            ['double_2_ascii']['options']['package']
            ['double_2_ascii']['module_name']
        """
        
        if arguments.has_key('double_2_ascii'):

            configuration = arguments['double_2_ascii']


        else:

            raise Exception("No 'double_2_ascii' configuration block present")

        output_mode = None
        resolution = None
        string_format = None
        
        if configuration.has_key('options'):

            options = configuration['options']

            if options.has_key('output_mode'):

                output_mode = options['output_mode']

            if options.has_key('resolution'):

                resolution = options['resolution']

            if options.has_key('format'):

                string_format = options['format']

            if options.has_key('filename'):

                self.filename = options['filename']

            else:

                self.filename = None


        self._output_gen = og.Output(self.filename)

        self.SetMode(output_mode)

        self.SetResolution(resolution)

        self.SetFormat(string_format)

#---------------------------------------------------------------------------


    def _ParseOutputs(self):
        """!

        @brief Parses the set outputs from the schedule configuration.

        Outputs can also be set via a yaml string fed to the parse method.
        """
        
        if not self.outputs is None:

            #
            # Could be possible to move this loop to it's own method
            # for loading outputs.
            #
            component_name = ""
            field = ""

            for i, o in enumerate(self.outputs):

                if o.has_key('outputclass'):

                    if o['outputclass'] != 'double_2_ascii':
                        # if this output is not meant
                        # for this object type then we
                        # continue and ignore it
                        continue

                if o.has_key('component_name'):
                    
                    component_name = o['component_name']

                else:

                    print "Output Error, no component name for output %d" % i

                    continue

                if o.has_key('field'):

                    field = o['field']

                else:

                    print "Output Error, no field given for output %d" % i

                    continue


                if self.verbose:

                    print "\tAdding output %d, '%s' with field '%s'" % (i+1, component_name, field)

                    
                self.AddOutput(component_name, field)
