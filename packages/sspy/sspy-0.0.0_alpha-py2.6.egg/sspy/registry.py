"""!
@file registry.py


This module contains classes used to dynamically create
solvers and objects from plugin specifications. Specific classes
present are:


    SolverRegistry: A registry used to create solver objects.
    ServiceRegistry: Registry used to create modeling service objects.
    OutputRegistry: Registry used to create output objects.
    InputRegistry: Registry used to create an input object.
    
"""
import errors
import imp
import os
import pdb
import sys
import yaml

from plugin import Plugin


#************************* Begin Registry ****************************
class Registry:
    """
    @class Registry A base class for creating a plugin registry

    
    """
#---------------------------------------------------------------------------

    def __init__(self, plugin_directory=None, plugin_file=None, verbose=False):

        self._plugin_directory = ""

        self._plugin_file = ""

        self.verbose = verbose
        
        if plugin_directory is None:
#             curr_dir = os.path.dirname(os.path.abspath(__file__))

#             self._plugin_directory = os.path.join(curr_dir, "solvers")

#             if not os.path.isdir(self._plugin_directory):

            raise errors.PluginDirectoryError("No plugin directory specified")

        elif plugin_file is None:

            raise errors.PluginFileError("No plugin file identifier given")
        
        else:

            if os.path.isdir(plugin_directory):

                self._plugin_directory = plugin_directory

            else:

                raise errors.PluginDirectoryError("'%s' directory not found" % plugin_directory)


            self._plugin_file = plugin_file

        
        self._loaded_plugins = []

        plugins = self.GetPluginFiles()

        for p in plugins:

            self.LoadPlugin(p)


#---------------------------------------------------------------------------

    def LoadPlugin(self, plugin_file):

        if not os.path.exists(plugin_file):

            print "Error loading plugin, %s doesn't exist" % plugin_file
            
            return False

        try:

            plugin_entry = Plugin(plugin_file)

        except errors.PluginFileError, e:

            print "Error Loading Plugin %s, %s" % (plugin_file, e)

            return False

        if self.Exists(plugin_entry):

            raise errors.PluginError("Already a plugin with the name '%s'" % plugin_entry.GetName())

            return False

        else:
            
            self._loaded_plugins.append(plugin_entry)

            return True


#---------------------------------------------------------------------------

    def Exists(self, plugin):
        """
        @brief Determines if a plugin is present.
        """

        pi = self.GetPluginData(plugin.GetName())

        if pi is None:

            return False
        
        else:

            return True
        

#---------------------------------------------------------------------------

    def GetPluginData(self,name):

        for pi in self._loaded_plugins:

            if pi.GetName() == name:

                return pi

        return None
    
#---------------------------------------------------------------------------

    def GetPluginIndex(self,name):

        for index,pi in enumerate(self._loaded_plugins):

            if pi.GetName() == name:

                return index

        return -1
    

#---------------------------------------------------------------------------

    def GetPlugins(self):

        """!
        @brief Returns the list of solvers
        """
    
        return self._loaded_plugins

#---------------------------------------------------------------------------

    def GetEntries(self):
        """

        """
        return self.Gets()

#---------------------------------------------------------------------------

    def GetPluginFiles(self):

        """!
        @brief Returns the list of detected solver.
        """
        pis = self._FindPlugins()

        # exception?
    
        return pis

#---------------------------------------------------------------------------

    def _IsPlugin(self, path):
        """

        """
        return os.path.isfile( os.path.join( path, self._plugin_file ))

#---------------------------------------------------------------------------


    def _FindPlugins(self):
        """!
        @brief Finds all solvers plugin files in the solvers_dir

        Returns a list of the plugin files. 
        """

        plugins = []

        for path, directories, files in os.walk( self._plugin_directory ):
            if self._IsPlugin( path ):
                path.replace( '/','.' )

                pi = os.path.join(path, self._plugin_file)
            
                plugins.append(pi)

        return plugins
        

#*************************** End Registry ****************************









#************************* Begin SolverRegistry ****************************

class SolverRegistry(Registry):
    """
    @class SolverRegistry A registry for the solver objects
    """
    
    def __init__(self, solver_directory, verbose=False):

        Registry.__init__(self,
                          plugin_directory=solver_directory,
                          plugin_file="solver.yml",
                          verbose=verbose)

        self.verbose = verbose
        
#---------------------------------------------------------------------------

    def CreateSolver(self, name, type=None, constructor_settings=None, index=-1):

        plugin = None

        if type is not None:

            plugin = self.GetPluginData(type)

        elif index != -1:

            # bounds check?
            plugin = self._loaded_plugins[index]

        solver = self._InstantiateFromFile(plugin, name, constructor_settings)

        return solver
    
#---------------------------------------------------------------------------

    def _InstantiateFromFile(self, plugin, name="Untitled", constructor_settings=None):
        """
        @brief Creates a solver object from a plugin
        """
        class_inst = None
        expected_class = 'Solver'

        
        # First we check to see if we have the proper data to
        # allocate from a file.
        try:
            
            filepath = plugin.GetFile()

            solver_type = plugin.GetName()
            
        except AttributeError, e:

            raise errors.ScheduleError("Cannot create Solver, invalid plugin for solver '%s', %s" % (name,e))


        if not os.path.exists(filepath):

            raise errors.ScheduleError("Error: no such plugin to load class from: %s" % filepath)

        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)

        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)

        if expected_class in dir(py_mod):

            try:

                class_inst = py_mod.Solver(name=name,
                                           plugin=plugin,
                                           constructor_settings=constructor_settings,
                                           verbose=self.verbose) 

            except Exception, e:

                raise errors.SolverError("'Solver' class '%s' cannot be created: %s" % (name, e))

        return class_inst

#---------------------------------------------------------------------------


#************************ End SolverRegistry **************************





#************************* Begin ServiceRegistry ****************************
class ServiceRegistry(Registry):

    def __init__(self, service_directory, verbose=False):

        Registry.__init__(self,
                          plugin_directory=service_directory,
                          plugin_file="service.yml",
                          verbose=verbose)




#---------------------------------------------------------------------------

    def CreateService(self, name, type=None, arguments=None, index=-1):

        plugin = None

        if type is not None:

            plugin = self.GetPluginData(type)

        elif index != -1:

            plugin = self._loaded_plugins[index]
            
            
        service = self._InstantiateFromFile(plugin, name, arguments)

        # verify sim legit?
        
        return service    


#---------------------------------------------------------------------------


    def _InstantiateFromFile(self, plugin, name="Untitled", arguments=None):
        """
        @brief Creates a service object from a plugin
        """
        class_inst = None
        expected_class = 'Service'

        
        # First we check to see if we have the proper data to
        # allocate from a file.
        try:
            
            filepath = plugin.GetFile()

        except AttributeError:

            raise errors.ScheduleError("Cannot create Service, invalid plugin for service '%s'" % (name))
        

        if not os.path.exists(filepath):

            raise errors.ServiceError("no plugin module to load class from: %s" % filepath)
        
            return None

        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)

        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)
#        pdb.set_trace()
        if expected_class in dir(py_mod):

            try:

                class_inst = py_mod.Service(name=name,
                                            plugin=plugin,
                                            arguments=arguments,
                                            verbose=self.verbose) 

            except Exception, e:

                raise errors.ServiceError("'Service' class '%s' cannot be created: %s" % (name, e))

        return class_inst

#---------------------------------------------------------------------------
#************************* End ServiceRegistry ****************************






#************************* Begin OutputRegistry ****************************
class OutputRegistry(Registry):
    """

    """
    
    def __init__(self, output_directory, verbose=False):

        Registry.__init__(self,
                          plugin_directory=output_directory,
                          plugin_file="output.yml",
                          verbose=verbose)




#---------------------------------------------------------------------------

    def CreateOutput(self, name, type=None, arguments=None, index=-1):


        plugin = None

        if type is not None:

            plugin = self.GetPluginData(type)

        elif index != -1:

            # bounds check?
            plugin = self._service_plugins[index]
            
            
        my_output = self._InstantiateFromFile(plugin, name, arguments)

        return my_output    


#---------------------------------------------------------------------------

    def _InstantiateFromFile(self, plugin, name="Untitled", arguments=None):
        """
        @brief Creates an output object from a plugin
        """
        class_inst = None
        expected_class = 'Output'

        
        # First we check to see if we have the proper data to
        # allocate from a file.
        try:
            
            filepath = plugin.GetFile()

            output_type = plugin.GetName()
            
        except AttributeError, e:

            raise errors.ScheduleError("Cannot create Output, invalid plugin for solver '%s', %s" % (name,e))


        if not os.path.exists(filepath):

            raise errors.ScheduleError("Error: no such plugin to load class from: %s" % filepath)

        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)

        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)

        if expected_class in dir(py_mod):

            
            try:
                
                class_inst = py_mod.Output(name=name,
                                           plugin=plugin,
                                           arguments=arguments,
                                           verbose=self.verbose) 

            except Exception, e:

                raise errors.OutputError("'Output' object '%s' cannot be created: %s" % (name, e))

        return class_inst


#---------------------------------------------------------------------------


#************************* End OutputRegistry ****************************







#************************* Begin InputRegistry ****************************
class InputRegistry(Registry):
    """

    """

    def __init__(self, input_directory, verbose=False):

        Registry.__init__(self,
                          plugin_directory=input_directory,
                          plugin_file="input.yml",
                          verbose=verbose)


#---------------------------------------------------------------------------

    def CreateInput(self, name, type=None, arguments=None, index=-1):


        plugin = None

        if type is not None:

            plugin = self.GetPluginData(type)

        elif index != -1:

            # bounds check?
            plugin = self._service_plugins[index]
            
            
        my_input = self._InstantiateFromFile(plugin, name, arguments)

        return my_input   


#---------------------------------------------------------------------------


    def _InstantiateFromFile(self, plugin, name="Untitled", arguments=None):
        """
        @brief Creates an output object from a plugin
        """
        class_inst = None
        expected_class = 'Input'

        
        # First we check to see if we have the proper data to
        # allocate from a file.
        try:
            
            filepath = plugin.GetFile()

            input_type = plugin.GetName()
            
        except AttributeError, e:

            raise errors.ScheduleError("Cannot create Input, invalid plugin for solver '%s', %s" % (name,e))


        if not os.path.exists(filepath):

            raise errors.ScheduleError("Error: no such plugin to load class from: %s" % filepath)

        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)

        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)

        if expected_class in dir(py_mod):

            
            try:
                
                class_inst = py_mod.Input(name=name,
                                           plugin=plugin,
                                           arguments=arguments,
                                           verbose=self.verbose) 

            except Exception, e:

                raise errors.OutputError("'Input' object '%s' cannot be created: %s" % (name, e))

        return class_inst


#---------------------------------------------------------------------------


#************************* End InputRegistry ****************************
