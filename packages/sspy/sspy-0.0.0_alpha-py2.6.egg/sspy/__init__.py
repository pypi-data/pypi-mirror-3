"""!
@package sspy

The simple scheduler in python is a software package that 
uses the model container and heccer solver to run a simulation 
with a set of simulation parameters. It can be extended by using 
plugins for solvers and simulation objects.

"""
import os
import pdb
import pprint
import sys

try:
    import yaml
except ImportError:
    sys.exit("Need PyYaml http://pyyaml.org/\n")

from __cbi__ import PackageInfo

_package_info = PackageInfo()

__version__ = _package_info.GetVersion()

import errors

from registry import SolverRegistry
from registry import ServiceRegistry
from registry import OutputRegistry
from registry import InputRegistry

from schedulee import Schedulee

_module_directory =  os.path.dirname(os.path.abspath(__file__))


#*********************************** Begin SSPy ****************************
class SSPy:


#---------------------------------------------------------------------------

    def __init__(self, name="Untitled", verbose=False,
                 solver_directory= os.path.join(_module_directory, 'plugins', 'solvers'),
                 service_directory= os.path.join( _module_directory, 'plugins', 'services'),
                 input_directory= os.path.join( _module_directory, 'plugins', 'inputs'),
                 output_directory= os.path.join( _module_directory, 'plugins', 'outputs')
                 ):


        self.verbose = verbose
        self.simulation_verbose = None
        self.verbose_level = 0
        
        # set up the pretty printer for printing out dicts and arrays
        #        self.pp = pprint.PrettyPrinter()


        # Registry objects for dynamically creating solvers and
        # other objects
        self._solver_registry = SolverRegistry(solver_directory, verbose=self.verbose)
        self._service_registry = ServiceRegistry(service_directory, verbose=self.verbose)
        self._output_registry = OutputRegistry(output_directory, verbose=self.verbose)
        self._input_registry = InputRegistry(input_directory, verbose=self.verbose)

        self.name = name

        self._analyzers = {}

        #----------------------------------------------
        #Internal data members that are representative
        # of variables parsed from a declaration.
        #----------------------------------------------
        self._loaded_services = []
        self._solvers = []
        self._inputs = []
        self._input_parameters = []
        self._outputs = []
        self._output_parameters = []
        self._runtime_parameters = []
        self._element_list = []

        # Each member of this array is in the format:
        #  dict(modelname="modelname",
        #       runtime_parameters=[ (component name, field, value), ...],
        #       solverclass="solver type")
        #
        self.models = []
        #----------------------------------------------

        
        # Simulation variables
        self.modelname = None # might need to make this a list of modelnames
        self.steps = None
        self.time_step = None
        self.current_simulation_time = None
        self.simulation_time = None

        # Internal schedule data to manage.
        self._schedule_data = {}
        self._schedule_file = ""

        # arrays of schedulees to process when run.
        self._schedulees = []

        # status variables to check
        self._compiled = False
        self._initialized = False
        self._schedule_loaded = False
        self._services_connected = False
        self._inputs_connected = False
        self._outputs_connected = False
        self._scheduled = False
        self._runtime_parameters_applied = False
        

#---------------------------------------------------------------------------


    def __del__(self):

        pass

#---------------------------------------------------------------------------

    def GetName(self):

        return self.name

#---------------------------------------------------------------------------

    def GetVersion(self):

        return __cbi__.GetVersion()

#---------------------------------------------------------------------------

    def GetRevisionInfo(self):

        return __cbi__.GetRevisionInfo()

#---------------------------------------------------------------------------

    def GetVerbosityLevel(self):
        """
        This is ugly, will need to change this.
        """
        if self.verbose and self.simulation_verbose:

            return 2

        elif self.verbose and not self.simulation_verbose:

            return 1

        elif not self.verbose and self.simulation_verbose:

            return 1

        else:

            return 0

#---------------------------------------------------------------------------

    def LoadSolverPlugin(self, path):
        """!
        @brief Loads a solver plugin
        @param path A path to a solver plugin file or directory.
        """

        plugin_path = ""
        
        if os.path.isdir(path):

            plugin_path = os.path.join(path, 'solver.yml')

            
            if not os.path.isfile( plugin_path ):

                raise Exception("No solver.yml dscriptor file found in the plugin directory")

        else:

            plugin_path = path
            
            
        if not os.path.isfile( plugin_path ):

            raise Exception("Not a valid solver plugin path: %s" % path)


        try:

            self._solver_registry.LoadPlugin(plugin_path)

        except Exception, e:
            # probably redundant, but eeh
            raise Exception(e)

#---------------------------------------------------------------------------

    def _LoadPlugin(self, registry, plugin_file, path):

        """!
        @brief Helper method for loading a plugin
        @param registry A plugin registry object
        @param plugin_file The file name of the plugin file to detect.
        @param path A path to a service plugin file or directory.
        """

        plugin_path = ""

        if os.path.isdir(path):

            plugin_path = os.path.join(path, plugin_file)

            
            if not os.path.isfile( plugin_path ):

                raise Exception("No %s descriptor file found in the plugin directory" % plugin_file)

        elif os.path.isfile(path):    

            dirrectory, filename = os.path.split(path)

            if filename != plugin_file:

                raise Exception("Invalid descriptor file found, expected %s, found %s" % (plugin_file, filename))

            else:
                
                plugin_path = path
                        
        else:

            raise Exception("%s is not a valid file or directory" % path)

        registry.LoadPlugin(plugin_path)


#---------------------------------------------------------------------------

    def LoadServicePlugin(self, path):
        """!
        @brief Loads a service plugin
        @param path A path to a service plugin file or directory.
        """

        self._LoadPlugin(self._service_registry, 'service.yml', path)

#---------------------------------------------------------------------------

    def LoadSolverPlugin(self, path):
        """!
        @brief Loads a solver plugin
        @param path A path to a solver plugin file or directory.
        """

        self._LoadPlugin(self._solver_registry, 'solver.yml', path)

#---------------------------------------------------------------------------

    def LoadInputPlugin(self, path):
        """!
        @brief Loads an input plugin
        @param path A path to an input plugin file or directory.
        """

        self._LoadPlugin(self._input_registry, 'input.yml', path)

#---------------------------------------------------------------------------

    def LoadOutputPlugin(self, path):
        """!
        @brief Loads an output plugin
        @param path A path to an output plugin file or directory.
        """

        self._LoadPlugin(self._output_registry, 'output.yml', path)


#---------------------------------------------------------------------------

    def _PrintPlugin(self, p=None, verbose=False):

        if p is None:

            return

        print "%s" % p.GetName()
            
        if verbose:

            if p.GetLabel() is not None: print "label: %s" % p.GetLabel()
            if p.GetVersion() is not None: print "version: %s" % p.GetVersion()
            if p.GetDescription() is not None: print "description: %s" % p.GetDescription()
            if p.GetFormat() is not None: print "format:\n\n%s" % p.GetFormat()
            print ""


#---------------------------------------------------------------------------

    def _PrintSimObject(self, p=None, verbose=False):

        if p is None:

            return

        print "%s" % p.GetName()
            
        if verbose:

#            if p.GetLabel() is not None: print "Label: %s" % p.GetLabel()
            print ""

#---------------------------------------------------------------------------

    def _PrintOutputObject(self, o=None, verbose=False):

        if o is None:

            return

                    
        if verbose:
            
            print "name: %s" % o.GetName()

            if not o.GetFilename() is None: print "filename: %s" % o.GetFilename()

            try:
                if not o.format is None: print "format: %s" % o.format
                if not o.mode is None: print "mode: %d" % o.mode
                if not o.resolution is None: print "resolution: %d" % o.resolution

            except Exception, e:

                print e
                
            try:

                print "outputs:"
                for x in o.outputs:

                    try:
                        
                        print " %s\t%s\t%s" % (x['outputclass'], x['component_name'], x['field'])

                    except KeyError, k:

                        print k

            except:

                pass
            
            print ""
            
        else:
            
            print "%s" % o.GetName()

            


#---------------------------------------------------------------------------


    def GetSolverPlugins(self):

        try:
            
            return self._solver_registry.GetPlugins()

        except Exception:

            return None
        
#---------------------------------------------------------------------------

    def ListSolverPlugins(self, verbose=False):

        solver_plugins = self.GetSolverPlugins()

        if len(solver_plugins) == 0:

            print "no solver plugins loaded"
            
            return 

        print "solver plugins:\n"
        
        for sp in solver_plugins:

            self._PrintPlugin(sp, verbose)
            
        print ""
                
#---------------------------------------------------------------------------

    def GetServicePlugins(self):

        try:
            
            return self._service_registry.GetPlugins()

        except Exception:

            return None
        
#---------------------------------------------------------------------------

    def ListServicePlugins(self, verbose=False):

        service_plugins = self.GetServicePlugins()

        if len(service_plugins) == 0:

            print "no service plugins loaded"
            
            return 

        print "service plugins:\n"
        
        for sp in service_plugins:

            self._PrintPlugin(sp, verbose)

        print ""
        
#---------------------------------------------------------------------------

    def GetOutputPlugins(self):

        try:
            
            return self._output_registry.GetPlugins()

        except Exception:

            return None
        
#---------------------------------------------------------------------------

    def ListOutputPlugins(self, verbose=False):

        output_plugins = self.GetOutputPlugins()

        if len(output_plugins) == 0:

            print "no output plugins loaded"
            
            return 

        print "output plugins:\n"
        
        for op in output_plugins:

            self._PrintPlugin(op, verbose)

        print ""

#---------------------------------------------------------------------------

    def GetInputPlugins(self):

        try:
            
            return self._input_registry.GetPlugins()

        except Exception:

            return None
        
#---------------------------------------------------------------------------

    def ListInputPlugins(self, verbose=False):

        input_plugins = self.GetInputPlugins()

        if len(input_plugins) == 0:

            print "no input plugins loaded"
            
            return 

        print "input plugins:\n"
        
        for ip in input_plugins:

            self._PrintPlugin(ip, verbose)

        print ""

#---------------------------------------------------------------------------

    def GetElements(self, service_name=None):
        """!
        @returns the elements present in this schedules services

        Right now just returns the elements present in the first
        service.
        """

        if not service_name is None:
            
            for s in self._loaded_services:

                if s.GetName() == service_name:

                    self._element_list = s.GetElements()

                    break

        else:

            if len(self._loaded_services) > 0:

                s = self._loaded_services[0]

                self._element_list = s.GetElements()

        return self._element_list


#---------------------------------------------------------------------------

    def GetCoordinates(self, service_name=None):
        """!
        @returns the coordinates present in this schedules services

        Right now just returns the elements present in the first
        service.
        """

        if not service_name is None:
            
            for s in self._loaded_services:

                if s.GetName() == service_name:

                    coordinate_list = s.GetCoordinates()

        else:

            if len(self._loaded_services) > 0:

                s = self._loaded_services[0]

                coordinate_list = s.GetCoordinates()

        return coordinate_list

#---------------------------------------------------------------------------

    def Load(self, filename):
        """
        @brief Loads a yaml specification
        """
        if os.path.exists(filename):

            norm_file_path = os.path.normpath(filename)

            if self.verbose:

                print "Loading schedule '%s'" % norm_file_path
                
            try:
                
                self._schedule_data = yaml.load(open(norm_file_path,'rb'))
            
            except yaml.YAMLError, exc:    

                raise errors.ScheduleError("Failed to load schedule '%s' from file: %s" % (filename, exc))

        else:

            self._schedule_loaded = False
            
            raise errors.ScheduleError("Schedule file '%s' doesn't exist" % filename)

        self._schedule_file = norm_file_path

        try:

            self.ParseSchedule(self._schedule_data)

        except errors.ScheduleError, e:

            print "%s" % e

            self._schedule_loaded = False

        self._schedule_loaded = True

#---------------------------------------------------------------------------

    def Dump(self):
        """

        """
        
        try:

            data = yaml.dump(self._schedule_data,
                             allow_unicode=True)

#                       encoding=encoding,
        except yaml.YAMLError, e:

            print "Error dumping schedule data: %s" % e


        if self.verbose:

            print "Dumping schedule data for %s\n" % self._schedule_file
            
        print data

#---------------------------------------------------------------------------

    def AddSchedulee(self, s, schedulee_type):
        """
        @brief Adds jobs to be scheduled.

        Adds input, output and solver objects to be scheduled.
        """

        # error checking?

        try:
            
            schedulee = Schedulee(s, schedulee_type, self.verbose)
        
        except Exception, e:

            sys.stderr.write("Can't schedule simulation object: %s" % e)
    
            return False
        
        self._schedulees.append(schedulee)

        return True

#---------------------------------------------------------------------------

    def ScheduleAll(self):

        if self._scheduled:

            if self.verbose:

                print "All objects are already scheduled"

                return
            
        else:

            if self.verbose:

                print "Scheduling all simulation objects"



        if len(self._inputs) > 0:
            
            if self.verbose:

                print "\tScheduling inputs:"
        
            for i in self._inputs:

                if self.verbose:

                    print "\t\tScheduling input '%s'" % i.GetName()

                self.AddSchedulee(i, 'input')


        if len(self._solvers) > 0:
            
            if self.verbose:

                print "\tScheduling solvers:"

            for s in self._solvers:

                if self.verbose:

                    print "\t\tScheduling solver '%s'" % s.GetName()

                self.AddSchedulee(s, 'solver')

        if len(self._outputs) > 0:

            if self.verbose:

                print "\tScheduling outputs:"

            for o in self._outputs:

                if self.verbose:

                    print "\t\tScheduling output '%s'" % o.GetName()
                    
                self.AddSchedulee(o, 'output')


        # If we have a stored timestep then we apply
        # it here.
        if not self.time_step is None:

            for s in self._schedulees:

                s.SetTimeStep(self.time_step)
                
        self._scheduled = True

#---------------------------------------------------------------------------

    def GetLoadedServices(self):

        return self._loaded_services

#---------------------------------------------------------------------------

    def ListLoadedServices(self, verbose=False):

        loaded_services = self.GetLoadedServices()

        if len(loaded_services) == 0:

            print "no services loaded"
            
            return 

        print "loaded services:\n"
        
        for s in loaded_services:

            self._PrintSimObject(s, verbose)
            
        print ""

#---------------------------------------------------------------------------

    def GetLoadedSolvers(self):

        return self._solvers

#---------------------------------------------------------------------------

    def ListLoadedSolvers(self, verbose=False):

        loaded_solvers = self.GetLoadedSolvers()

        if len(loaded_solvers) == 0:

            print "no solvers have been loaded"
            
            return 

        print "loaded solvers:\n"
        
        for s in loaded_solvers:

            self._PrintSimObject(s, verbose)
            
        print ""

#---------------------------------------------------------------------------

    def GetLoadedInputs(self):

        return self._inputs

#---------------------------------------------------------------------------

    def ListLoadedInputs(self, verbose=False):

        loaded_inputs = self.GetLoadedInputs()

        if len(loaded_inputs) == 0:

            print "no inputs have been loaded"
            
            return 

        print "loaded inputs:\n"
        
        for i in loaded_inputs:

            self._PrintSimObject(i, verbose)
            
        print ""

#---------------------------------------------------------------------------

    def GetLoadedOutputs(self):

        return self._outputs

#---------------------------------------------------------------------------

    def ListLoadedOutputs(self, verbose=False):

        loaded_outputs = self.GetLoadedOutputs()

        if len(loaded_outputs) == 0:

            print "no outputs have been loaded"
            
            return 

        print "loaded outputs:\n"
        
        for o in loaded_outputs:

            self._PrintOutputObject(o, verbose)
            
        print ""

#---------------------------------------------------------------------------

    def GetSchedulees(self):

        return self._schedulees

#---------------------------------------------------------------------------

    def SetVerbose(self, verbose):

        self.verbose = verbose

#---------------------------------------------------------------------------


    def Step(self):
        """
        @brief Perform one step over all schedulees
        """
        for s in self._schedulees:

            s.Step()

#---------------------------------------------------------------------------

    def Advance(self):
        """

        """
        self.Step()

#---------------------------------------------------------------------------

    def Compile(self):
        """
        @brief Compiles all solvers 
        """
        if self.verbose:
            
            print "Compiling all solvers"

        for solver in self._solvers:

            try:

                if self.verbose:

                    print "\tCompiling Solver: %s" % solver.GetName()

                solver.Compile()

            except Exception, e:

                raise errors.ScheduleeError("Error compiling solver '%s': %s" % (solver.GetName(),e))

        self._compiled = True

#---------------------------------------------------------------------------
    
    def Analyze(self):

        pass

#---------------------------------------------------------------------------

    def ApplyRuntimeParameters(self):
        """!
        @brief Applies model specific runtime parameters

        Sets the model runtime parameters that were parsed.
        Directly reads from self.models so that this data
        can be manipulated by a gui or other interface. 
        
        """
        
        if self.models is None or len(self.models) == 0:

            if self.verbose:

                print "No model runtime parameters defined"

            return

        num_models = len(self.models)

        if self.verbose:

            print "Applying model runtime parameters to %d models" % num_models

        for m in self.models:

            try:
                
                modelname = m['modelname']

                if self.verbose:

                    print "\tSetting runtime parameters for '%s'" % modelname


                self.SetModelName(modelname)
                    
                if m.has_key('runtime_parameters'):
                    
                    for parameter in m['runtime_parameters']:

                        component_name = parameter[0]
                        field = parameter[1]
                        val = parameter[2]

                        self.SetParameter(path=component_name, parameter=field, value=val)

            except Exception, e:

                print e

                continue

        # Now apply genericly set parameters

        if len(self._runtime_parameters) > 0:

            if self.verbose:

                print "Applying generically set model runtime parameters"

            
            for p in self._runtime_parameters:

                try:

                    path = p['path'] 
                    parameter = p['parameter']
                    value = p['value']
                    service = None if not p.has_key('service') else p['service']

                    self.SetParameter(path, parameter, value, service)
                    
                except Exception, e:

                    print e

                    continue

#---------------------------------------------------------------------------

    def ConnectServices(self):
        """
        @brief Connects services to solvers and solvers to protocols

        """
        num_services = len(self._loaded_services)
        
        num_solvers = len(self._solvers)

        if num_services == 0:

            print "No services to connect"

            return False

        if num_solvers == 0:

            print "No solvers to connect"

            return False

        if self.verbose:

            print "Connecting %d solvers to %d services" % (num_solvers, num_services)
        
        for service in self._loaded_services:

            for solver in self._solvers:

                if self.verbose:

                    print "\tConnecting solver '%s' to service '%s'" % (solver.GetName(),service.GetName())

                try:

                    solver.Connect(service)

                except Exception, e:

                    print "\tCan't connect solver '%s' to service '%s': %s" % (solver.GetName(), service.GetName(), e)

        self._services_connected = True
 
#---------------------------------------------------------------------------


    def ConnectOutputs(self):
        """!
        @brief 
        """
                   
        num_outputs = len(self._outputs)

        num_solvers = len(self._solvers)

        if num_solvers == 0:

            print "No solvers to connect to outputs"

            return False

        if num_outputs > 0:

            if self.verbose:
                
                print "Connecting %d outputs to %d solvers" % (num_outputs, num_solvers)

            # Connect solvers to outputs
            for o in self._outputs:

                for solver in self._solvers:

                    if self.verbose:

                        print "\tConnecting solver '%s' to output '%s'" % (solver.GetName(),o.GetName())
   
                    try:

                        o.Connect(solver)
                    
                    except Exception, e:

                        print "\tCan't connect solver '%s' to output '%s': %s" % (solver.GetName(), o.GetName(), e)


        # Here we connect all of the output parameters we stored
        for o in self._output_parameters:

            self.ConnectOutputParameter(o['path'],
                                        o['parameter'],
                                        o['output_name'],
                                        o['output_type'])

        self._outputs_connected = True


#---------------------------------------------------------------------------

    def ConnectInputs(self):
        """!
        @brief  

        """
        
        num_inputs = len(self._inputs)

        num_solvers = len(self._solvers)

        if num_solvers == 0:

            print "No solvers to connect to inputs"

            return False
        
        if num_inputs > 0:

            if self.verbose:
                
                print "Connecting %d inputs to %d solvers" % (num_inputs, num_solvers)
        
            # Now we connect solvers to inputs
            for i in self._inputs:

                for solver in self._solvers:

                    if self.verbose:

                        print "\tConnecting solver '%s' to input '%s'" % (solver.GetName(),i.GetName())
                        
                    try:

                        i.Connect(solver)
                        
                    except Exception, e:

                        print "\tCan't connect solver '%s' to input '%s': %s" % (solver.GetName(), i.GetName(), e)

        self._inputs_connected = True
    
#---------------------------------------------------------------------------

    def Daemonize(self):

        pass

#---------------------------------------------------------------------------

    def Finish(self):
        """
        @brief Performs a finish on all schedulees
        """
        for s in self._schedulees:

            s.Finish()

        
#---------------------------------------------------------------------------

    def CreateService(self, name="default_model_container", type=None, arguments=None, verbose=False):
        """
        @brief Creates a new service with the given name, type and arguments.
        """

        service = self._service_registry.CreateService(name,
                                                       type,
                                                       arguments)

        self._loaded_services.append(service)

        return service

#---------------------------------------------------------------------------

    def CreateSolver(self, name=None, type=None, data=None, verbose=False):
        """
        @brief Creates a new service with the given name, type and arguments.
        """

        solver = self._solver_registry.CreateSolver(name, type, data, verbose)

        self._solvers.append(solver)

        return solver

#---------------------------------------------------------------------------

    def CreateInput(self, name=None, type=None, data=None, verbose=False):
        """
        @brief Creates a new service with the given name, type and arguments.
        """


        inp = self._input_registry.CreateInput(name, type, data, verbose)

        self._inputs.append(inp)

        return inp

#---------------------------------------------------------------------------

    def CreateOutput(self, name=None, type=None, data=None, verbose=False):
        """
        @brief Creates a new output with the given name, type and arguments.
        """


        out = self._output_registry.CreateOutput(name, type, data, verbose)

        self._outputs.append(out)

        return out

#---------------------------------------------------------------------------

    def CreatePerfectClamp(self, name=None, data=None, verbose=False):
        """
        @brief Creates a new service with the given name, type and arguments.
        """


        inp = self._input_registry.CreateInput(name, 'perfectclamp', data, verbose)

        self._inputs.append(inp)

        return inp

#---------------------------------------------------------------------------

    def CreateOutputfile(self, name=None, mode=None, resolution=None, format=None, verbose=False):
        """
        @brief Creates a double_2_ascii output file.
        """

#         if not arguments is None:

#             if 

#         else:

#             if not 
            
        outp = self._output_registry.CreateOutput(name, 'double_2_ascii', arguments, verbose)

        self._inputs.append(inp)

        return inp
    
#---------------------------------------------------------------------------

    def GetEngineOutputs(self):

        pass

#---------------------------------------------------------------------------


    def SetTimeStep(self, time_step):
        """!
        @brief Sets the timestep across all schedulees

        """
        if self._scheduled:

            for s in self._schedulees:

                s.SetTimeStep(time_step)

        self.time_step = time_step

#---------------------------------------------------------------------------

    def GetTimeStep(self):
        """

        If a timestep has been loaded from the solvers, but not the
        top level then we need to retrieve it from there. We set the
        top level time_step variable to the first good timestep value
        we get from a solver.
        """
        time_step = None
        
        if len(self._solvers) > 0:

            time_step = self._solvers[0].GetTimeStep()

            if not time_step is None:

                self.time_step = time_step

        return self.time_step


#---------------------------------------------------------------------------

    def Help(self):

        pass

#---------------------------------------------------------------------------

    def History(self):

        pass

#---------------------------------------------------------------------------

    def Initialize(self):
        """
        @brief Initializes all schedulees

        Sets all schedulees in queue to steps = 0, and time = 0.
        """

        if self.verbose:

            print "Initializing all schedulees"

        for schedulee in self._schedulees:

            try:

                if self.verbose:

                    print "\tInitializing Schedulee: %s" % schedulee.GetName()


                schedulee.Initialize()

            except Exception, e:

                raise errors.ScheduleeError("Error initializing schedulee '%s': %s" % (schedulee.GetName(),e))

        
        self.current_simulation_time = 0
        
        self._initialized = True

#---------------------------------------------------------------------------

    def Reset(self):
        """!
        @brief 
        """

        self.current_simulation_time = 0
        

#---------------------------------------------------------------------------

    def InstantiateCommunicators(self):

        pass
#---------------------------------------------------------------------------

    def InstantiateInputs(self):

        pass
#---------------------------------------------------------------------------

    def InstantiateOutputs(self):

        pass
#---------------------------------------------------------------------------

    def InstantiateServices(self):

        pass

#---------------------------------------------------------------------------

    def LookupModel(self):

        pass

#---------------------------------------------------------------------------

    def LookupObject(self):

        pass

#---------------------------------------------------------------------------
    def LookupSolverEngine(self):

        pass

#---------------------------------------------------------------------------
    def New(self):

        pass

#---------------------------------------------------------------------------
    def Optimize(self):
        """!
        @brief optimize schedulees
        @depricated
        
        Probably not needed since this won't use any C code.

        """
        pass

#---------------------------------------------------------------------------
    def Pause(self):

        pass

#---------------------------------------------------------------------------
    def Reconstruct(self):

        pass

#---------------------------------------------------------------------------
    def RegisterDriver(self):

        pass

#---------------------------------------------------------------------------

    def SetParameter(self, path=None, parameter=None, value=None, service=None):
        """!
        @brief Sets a parameter on all or one loaded services. 
        """

        if self._loaded_services is None:

            # here we store any parameters we need if a service isn't loaded
            # they are applied during ApplyRuntimeParameters()
            # Edit: This is commented out, easier to export parameters if they're all saved
            # in the plugin.

#             self._runtime_parameters.append(dict(path=path,
#                                                  parameter=parameter,
#                                                  value=value,
#                                                  service=service))


            raise errors.ParameterSetError("Can't set parameter %s on element %s, no service loaded" % (parameter,path))
        
        else:

            if service is None:
                
                for s in self._loaded_services:
                        
                    s.SetParameter(path, parameter, value)

            else:

                for s in self._loaded_services:

                    if s.GetName() == service:

                        s.SetParameter(path, parameter, value)
                        
                

#---------------------------------------------------------------------------

    def ConnectOutputParameter(self, path, parameter, output_name=None, output_type=None):
        """!
        @brief Sets a parameter on all loaded output

        @param path The element path
        @param parameter The parameter to set the output on, usually a solved variable.
        @param output_name The name of a specific output object to add the output to. 
        @param output_type The type of outputs to add an output to.
        """

        if self._outputs is not None:

            for o in self._outputs:

                if not output_name is None:

                    if o.GetName() == output_name:
                        
                        o.AddOutput(path, parameter)
                        
                elif not output_type is None:

                    if o.GetType() == output_type:

                        o.AddOutput(path, parameter)
                else:

                    o.AddOutput(path, parameter)
        else:

            raise errors.OutputError("Can't connect output parameter (%s, %s), no outputs have been loaded" % (path,parameter))

#---------------------------------------------------------------------------


    def AddOutput(self, path, parameter, output_name=None, output_type=None):
        """
        
        """

        output_data = dict(path=path, parameter=parameter,
                           output_name=output_name, output_type=output_type)


        if output_data in self._output_parameters:

            raise errors.OutputError("Output has already been added")
        
        self._output_parameters.append(output_data)

        if self._outputs_connected:

            self.ConnectOutputParameter(path, parameter, output_name, output_type)

#---------------------------------------------------------------------------

    def SetOutputFormat(self, format, output_name=None, output_type=None):
        """!
        @brief Sets a parameter on all loaded output

        @param format A string for the output format.
        @param output_name The name of a specific output object to add the output to. 
        @param output_type The type of outputs to add an output to.
        """

        if self._outputs is not None:

            for o in self._outputs:
                        
                if not output_type is None:

                    if o.GetType() == output_type:

                        if output_name is None:

                            o.SetFormat(format)

                        elif o.GetName() == output_name:

                            o.SetFormat(format)

                elif not output_name is None:

                    if o.GetName() == output_name:
                        
                        o.SetFormat(format)
                    
                else:

                    o.SetFormat(format)
        else:

            print "No outputs have been loaded"

#---------------------------------------------------------------------------

    def SetOutputFilename(self, filename, output_name=None, output_type=None):
        """!
        @brief Sets the output filename on all loaded output.

        @param filename A string for the output filename.
        @param output_name The name of a specific output object to add the output to. 
        @param output_type The type of outputs to add an output to.
        """

        if self._outputs is not None:

            for o in self._outputs:

                if not output_type is None:

                    if o.GetType() == output_type:

                        if output_name is None:

                            o.SetFilename(filename)

                        elif o.GetName() == output_name:

                            o.SetFilename(filename)
                            
                elif not output_name is None:

                    if o.GetName() == output_name:
                        
                        o.SetFilename(filename)
                        
                else:

                    o.SetFilename(filename)
        else:

            print "No outputs have been loaded"

#---------------------------------------------------------------------------

    def SetOutputMode(self, mode, output_name=None, output_type=None):
        """!
        @brief Sets a parameter on all loaded output

        @param mode A string for the mode to use
        @param output_name The name of a specific output object to add the output to. 
        @param output_type The type of outputs to add an output to.
        """

        if self._outputs is not None:

            for o in self._outputs:

                if not output_name is None:

                    if o.GetName() == output_name:
                        
                        o.SetMode(mode)
                        
                elif not output_type is None:

                    if o.GetType() == output_type:

                        o.SetMode(mode)
                else:

                    o.SetMode(mode)
        else:

            print "No outputs have been loaded"


#---------------------------------------------------------------------------

    def SetOutputResolution(self, res, output_name=None, output_type=None):
        """!
        @brief Sets a parameter on all loaded output

        @param res A value to use for output granularity
        @param output_name The name of a specific output object to add the output to. 
        @param output_type The type of outputs to add an output to.
        """

        if self._outputs is not None:

            for o in self._outputs:

                if not output_name is None:

                    if o.GetName() == output_name:
                        
                        o.SetResolution(res)
                        
                elif not output_type is None:

                    if o.GetType() == output_type:

                        o.SetResolution(res)
                else:

                    o.SetResolution(res)
        else:

            print "No outputs have been loaded"
            
#---------------------------------------------------------------------------

    def SetModelName(self, modelname):
        """
        @brief Sets the model name across all solvers
        """
        for s in self._solvers:

            if self.verbose:

                print "\t  Setting model name for solver '%s' to '%s'" % (s.GetName(), modelname)

            s.SetModelName(modelname)

#---------------------------------------------------------------------------

    def RunPrepare(self):



        if self.verbose:

            print "\n"

        if not self._runtime_parameters_applied:

            try:
                
                self.ApplyRuntimeParameters()

            except Exception, e:

                raise errors.RuntimeError("Can't apply runtime parameters: %s" % e)

        if self.verbose:

            print "\n"
                
        if not self._services_connected:

            try:
                
                self.ConnectServices()

            except Exception, e:
                
                raise errors.ConnectError("Can't connect services: %s" % e)

            if self.verbose:

                print "\n"

            
        if not self._compiled:

            try:
                
                self.Compile()

            except Exception, e:

                raise errors.CompileError("Can't compile schedule: %s" % e)

            if self.verbose:

                print "\n"

        if not self._outputs_connected:

            try:
                
                self.ConnectOutputs()

            except Exception, e:

                raise errors.ConnectError("Can't connect outputs: %s" % e)
                
            if self.verbose:

                print "\n"

        if not self._inputs_connected:

            try:
                
                self.ConnectInputs()

            except Exception, e:

                raise errors.ConnectError("Can't connect inputs: %s" % e)

            if self.verbose:

                print "\n"

        if not self._scheduled:

            try:
                
                self.ScheduleAll()

            except Exception, e:

                raise errors.ScheduleError("Can't schedule simulation objects: %s" % e)

            if self.verbose:

                print "\n"
                
        if not self._initialized:

            try:
                
                self.Initialize()

            except Exception, e:

                raise errors.ScheduleeError("Can't initialize schedulees: %s" % e)

            if self.verbose:

                print "\n"



#---------------------------------------------------------------------------

    def Run(self, time=None, steps=None):
        """!
        @brief Runs the simulation
        """
        run_steps = None
        run_current_steps = None
        run_time = None
        run_time_step = None
        
        self.RunPrepare()
        # catch exception?

        if not steps is None:

            run_steps = steps

        elif not time is None:

            run_time = time

        elif not self.steps is None:

            run_steps = self.steps

        elif not self.simulation_time is None:

            run_time = self.simulation_time

        # We have steps so we run for this number of steps
        if run_steps is not None:


            if self.verbose:

                print "Running simulation in steps mode"
            
            for i in range(run_steps + 1):

                self.Step()

        elif run_time is not None:

            run_time_step = self.GetTimeStep()

            if run_time_step is None:

                raise Exception("Can't run, no time step is set.")
                
            run_current_steps = 0

            if self.verbose:

                print "Running simulation in time mode"
                
            while self.current_simulation_time < run_time:

                self.Step()

                self.current_simulation_time += run_time_step

                run_current_steps += 1
                
                
        if self.verbose:

            print "Finishing simulation"
            
        self.Finish()
        

#---------------------------------------------------------------------------
    def Salvage(self):
        """
        @brief Method ensures that all needed keys are present
        @deprecated

        Most likely not needed since data from the specification is loaded
        into internal variables for processing and data manipulation instead
        of working off of the dictionary that is loaded straight from the file. 
        """
        pass

#---------------------------------------------------------------------------
    def Save(self):

        pass

#---------------------------------------------------------------------------

    def RegisterSchedulee(self, schedulee):

        pass

#---------------------------------------------------------------------------
    def ServiceRegister(self):

        pass

#---------------------------------------------------------------------------

    def Shell(self):

        pass

#---------------------------------------------------------------------------

    def Step(self):
        """
        @brief Executes a single step on all schedulees and updates the simulation time

        
        """
        for schedulee in self._schedulees:

                
            schedulee.Step()

            if self.simulation_verbose:

                schedulee.Report()
            
#---------------------------------------------------------------------------

    def Steps(self):

        pass

#---------------------------------------------------------------------------

    def Version(self):
        """

        """
        from __cbi__ import GetVersion

        return GetVersion()


#---------------------------------------------------------------------------
    
    def ParseSchedule(self, schedule_data):
        """
        @brief Parses the schedule

        Method parses the schedule data read in and creates
        a simulation based on the specification read in. The parse
        order follows the user workflow.

        
        Parse out the following top level keys to pass to helper methods:
            analyzers
            application_classes
            apply
            inputs
            input_classes
            models
            name
            optimize
            outputclasses
            outputs
            services
            solverclasses 
        """

        if self.verbose:

            print "Parsing schedule data"
        

        # Finds internal identifier for the schedule.
        if self._schedule_data.has_key('name'):

            self.name = schedule_data['name']

            if self.verbose:

                print "Schedule name is '%s'\n" % self.name


        # Loads the appropriate services for loading a model
        #   Such as the model_container
        if self._schedule_data.has_key('services'):

            services = schedule_data['services']

            self._ParseServices(services)

        # This Loads the default options for registered solvers
        # along with the service that it requires. In the case
        # of Heccer, the default required service is the model
        # container.
        if self._schedule_data.has_key('solverclasses'):

            solvers = schedule_data['solverclasses']

            self._ParseSolvers(solvers)
            


        # Set of options that define how to run this schedule.
        if self._schedule_data.has_key('apply'):
            
            apply_parameters = schedule_data['apply']
            
            self._ParseAppliedParameters(apply_parameters)


        # This retrieves the model identifier from the model that
        # was loaded via services and the type of solver to use.
        # for instance if the root identifier of the loaded model is
        # called "/soma" then this is the modelname and the solver is set
        # to look for this symbol.
        if self._schedule_data.has_key('models'):

            models = schedule_data['models']

            self._ParseModelParameters(models)


        # 
        if self._schedule_data.has_key('application_classes'):

            application_classes = schedule_data['application_classes']

            self._ParseApplicationClasses(application_classes)


       # Set of options for configuring analyzers
        if self._schedule_data.has_key('analyzers'):
            
            self._analyzers = schedule_data['analyzers']

            
        # Here we parse for external simulation objects that generate input into
        # the model. 
        if self._schedule_data.has_key('inputclasses'):

            inputclasses = schedule_data['inputclasses']
            
            inputs = None
            # Key contains the attributes for the inputclass objects that
            # were loaded.
            if self._schedule_data.has_key('inputs'):

                inputs = schedule_data['inputs']


            self._ParseInputs(inputclasses, inputs)


        # Specifies the output objects to use.
        if self._schedule_data.has_key('outputclasses'):

            outputclasses = schedule_data['outputclasses']

            
            # Attributes for the outputclass objects that were loaded.

            outputs = None
            
            if self._schedule_data.has_key('outputs'):
                
                outputs = schedule_data['outputs']

            self._ParseOutputs(outputclasses, outputs)
                

#---------------------------------------------------------------------------


    def _ParseApplicationClasses(self, application_class_data):

        if self.verbose:

            print "Found application classes:"
            
        if application_class_data.has_key('analyzers'):

            analyzers = application_class_data['analyzers']

            if self.verbose:
                
                print "\tApplication class: analyzers"


        if application_class_data.has_key('finishers'):

            finishers = application_class_data['finishers']

            if self.verbose:
                
                print "\tApplication class: finishers"

        if application_class_data.has_key('initializers'):

            initializers = application_class_data['initializers']

            if self.verbose:
                
                print "\tApplication class: initializers"

        if application_class_data.has_key('modifiers'):

            modifiers = application_class_data['modifiers']

            if self.verbose:
                
                print "\tApplication class: modifiers"

        if application_class_data.has_key('results'):

            results = application_class_data['results']

            if self.verbose:
                
                print "\tApplication class: results"

        if application_class_data.has_key('services'):

            services = application_class_data['services']

            if self.verbose:
                
                print "\tApplication class: services"

        if application_class_data.has_key('simulation'):

            simulation = application_class_data['simulation']

            if self.verbose:
                
                print "\tApplication class: simulation"

#---------------------------------------------------------------------------

    def _ParseAppliedParameters(self, apply_parameters):
        """
        @brief Retrieves simulation parameters
        
        example snippet. First set of arguments has
        the steps, second set has the simulation time.
        
        simulation:  
          - arguments:  
            - 1000  
            - 1  
          description: run 1000 steps of the simulation.  
          method: steps  
          - arguments:  
            - 0.1  
          description: advance the simulation by 0.1s.  
          method: advance
        
        """
        verbosity_level = 0
        
        if self.verbose:

            print "\nFound applied simulation parameters:"

        if apply_parameters.has_key('simulation'):

            parameter_sets = apply_parameters['simulation']

            for p in parameter_sets:

                try:
                                                
                    if p.has_key('method'):

                        method = p['method']

                        if method == 'steps':

                            self.steps = p['arguments'][0]

                            try:
                                
                                verbosity_level = p['arguments'][1]['verbose']

                            except KeyError:
                                                            
                                pass

                            if( verbosity_level == 2 ):
                                
                                self.verbose = True

                                self.simulation_verbose = True

                            elif( verbosity_level == 1 ):

                                self.verbose = True

                                self.simulation_verbose = False

                            else:

                                self.verbose = False

                                self.simulation_verbose = False


                        elif method == 'advance':

                            self.simulation_time = p['arguments'][0]

                except:

                    continue


            if self.verbose:

                print "Simulation Parameters: "

                if self.steps is not None:

                    print "\tSimulation will run for %d steps" % self.steps

                if self.simulation_verbose is not None:

                    print "\tVerbosity level is %d" % verbosity_level

                if self.time_step is not None:

                    print "\tStep size is %f" % self.time_step

                print ""

#---------------------------------------------------------------------------


    def _ParseModelParameters(self, model_data):

        """!
        @brief Applies model specific runtime parameters

        This was done somewhat lazy as far as checking for
        dictionary keys goes. Operates mainly as a parser that
        checks for keys and appends the dict to a new array. If there
        is a bad key in the set, the exception is caught and it proceeds
        to the next one. 
        """
        if model_data is None:

            return
        
        for m in model_data:

            try:
                
                modelname = m['modelname']

                runtime_parameters = []

                solverclass = None
                
                if m.has_key('solverclass'):

                    solverclass = m['solverclass']

                if m.has_key('runtime_parameters'):
                    
                    for parameter in m['runtime_parameters']:

                        component_name = parameter['component_name']
                        field = parameter['field']
                        val = parameter['value']

                        runtime_parameters.append((component_name, field, val))

                self.models.append(dict(modelname=modelname, runtime_parameters=runtime_parameters, solverclass=solverclass))

            except Exception, e:

                print "Error parsing model parameter for %s: %s" % (modelname,e)
                
                # catch the exception and allow the parse to continue if the next
                # one is good
                
                continue

#---------------------------------------------------------------------------


    def _ParseSolvers(self, solver_data):
        """!
        @brief Loads solvers from schedule data

        Processes a dictionary that was parsed from a schedule
        in YAML
        """

        try:

            items = solver_data.items()

        except AttributeError, e:

            raise errors.ScheduleError("Error parsing solvers, %s" % e)


        for solver_type, data in solver_data.iteritems():

            solver_name = ""
            
            if data.has_key('name'):

                solver_name = data['name']

            else:
                
                solver_name = "%s (%s)" % (self.name, solver_type)


            if self.verbose:

                print "Loading Solver '%s' of type '%s'" % (solver_name, solver_type)

            try:
                
                solver = self._solver_registry.CreateSolver(solver_name, solver_type, data, self.simulation_verbose)

            except Exception, e:

                raise errors.ScheduleError("Error, cannot create solver '%s' of type '%s', %s" % (solver_name, solver_type, e))

#             if solver is None:

#                 raise errors.SolverError("Solver wasn't created")

            self._solvers.append(solver)

#---------------------------------------------------------------------------

    def _ParseServices(self, service_data):
        """!
        @brief Loads services from schedule data

        Processes a dictionary that was parsed from a schedule
        in YAML
        """

        try:

            items = service_data.items()

        except AttributeError, e:

            raise errors.ScheduleError("Error parsing services, %s" % e)


        for service_type, data in service_data.iteritems():

            service_name = ""
            
            if data.has_key('name'):

                service_name = data['name']

            else:
                
                service_name = "%s (%s)" % (self.name, service_type)

            service_initiaizers = None

            if data.has_key('initializers'):

                initializers = data['initializers']

                for i in initializers:

                    if i.has_key('arguments'):
                        
                        arguments = i['arguments']

                    else:

                        print "Error processing arguments for '%s' of type '%s'" % (service_name, service_type)

                    for arg in arguments:

                        try:
                        
                            service = self._service_registry.CreateService(service_name,
                                                                           service_type,
                                                                           arg)
                        
                        except Exception, e:

                            print "Error creating service. %s" % e

                            continue


                        if self.verbose:

                            print "Loading Service '%s' of type '%s'" % (service_name, service_type)
            
                        self._loaded_services.append(service)

            else:
                
                raise errors.ScheduleError("Error parsing services, no initializers key")
                


            
#---------------------------------------------------------------------------

    def _ParseOutputs(self, output_data, output_parameters=None):
        """
        @brief Loads outputs from python dictionaries.
        """

        try:

            output_data.iteritems()

        except AttributeError, e:

            raise errors.ScheduleError("Error parsing outputs, %s" % e)


        for output_type, data in output_data.iteritems():

            output_name = ""
            
            if output_data.has_key('name'):

                output_name = data['name']

            else:
                
                output_name = "%s (%s)" % (self.name, output_type)


            if self.verbose:

                print "Loading Output '%s' of type '%s'" % (output_name, output_type)

            output = self._output_registry.CreateOutput(output_name, output_type, output_data)


        # After giving initializing data, we give the output parameters
        #
        if output_parameters is not None:

            for o in output_parameters:

                self.AddOutput(path=o['component_name'],
                               parameter=o['field'],
                               output_type=o['outputclass'],)

        self._outputs.append(output)

#---------------------------------------------------------------------------        

    def _ParseInputs(self, inp_data, inp_parameters=None):
        """
        @brief Loads inputs from python dictionaries.
        """

        try:

            inp_data.iteritems()

        except AttributeError, e:

            raise errors.ScheduleError("Error parsing inps, %s" % e)


        for inp_type, data in inp_data.iteritems():

            inp_name = ""
            
            if inp_data.has_key('name'):

                inp_name = data['name']

            else:
                
                inp_name = "%s (%s)" % (self.name, inp_type)


            if self.verbose:

                print "Loading Input '%s' of type '%s'" % (inp_name, inp_type)

            inp = self._input_registry.CreateInput(inp_name, inp_type, inp_data)

        # After giving initializing data, we give the inp parameters
        #
        if inp_parameters is not None:
            
            inp.SetInputs(inp_parameters)
        
        self._inputs.append(inp)

        
#*********************************** End SSPy *******************************
