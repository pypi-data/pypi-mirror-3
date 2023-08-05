"""
This is the solver plugin for Heccer to interact with
the interface of SSPy.
"""
import os
import pdb
import re
import sys

try:

    from model_container import ModelContainer

except ImportError, e:
        
    sys.exit("Error importing the Neurospaces Model Container Python module: %s\n" % e)



class Service:

#---------------------------------------------------------------------------
    def __init__(self, name="Untitled Model Container", plugin=None,
                 arguments=None, verbose=False):

        # Setting this here just in case

        self.library_path = os.path.join('/', 'usr', 'local', 'neurospaces', 'models', 'library')

        os.environ['NEUROSPACES_NMC_MODELS']= self.library_path

        self._name = name

        self._plugin_data = plugin

        self.verbose = verbose

        self.files = []

        self.parameters = []

        try:
            
            self._model_container = ModelContainer()

        except Exception, e:

            raise Exception("Service Error: Can't initialize Model Container '%s', %s" % (self._name, e))

        if self._model_container is None:

            raise Exception("Service Error: Can't initialize Model Container '%s'" % (self._name))


        self._arguments = arguments

        if not arguments is None:
            
            self._ParseArguments()


#---------------------------------------------------------------------------

    def Load(self, modelfile):

        self._model_container.Read(modelfile)

        self.files.append(modelfile)
        
#---------------------------------------------------------------------------


    def GetCore(self):
        """
        @brief Returns the constructed model container
        """
        return self._model_container
    
#---------------------------------------------------------------------------

    def GetName(self):

        return self._name

#---------------------------------------------------------------------------

    def GetPluginName(self):

        return self._plugin_data.GetName()

#---------------------------------------------------------------------------

    def GetType(self):

        return self._plugin_data.GetName()

#---------------------------------------------------------------------------

    def GetArguments(self):

        return self._arguments

#---------------------------------------------------------------------------

    def GetCoordinates(self):
        """!
        @brief Retrieves all visible coordinates
        """
        coord_list = []

        coord_list = self._model_container.CoordinatesToList('/**')

        return coord_list


#---------------------------------------------------------------------------

    def GetElements(self):
        """!
        @brief Retrieves all element names
        """
        element_list = []

        element_list = self._model_container.ChildrenToList('/')

        return element_list
    
#---------------------------------------------------------------------------

    def SetParameter(self, path, field, value, no_store=False):
        """!
        @brief Set's a parameter on the service

        Will automatically detect name space parameters. Need to add some sort
        of exception for when a parameter isn't set.

        Only time the no_store option should be set is when performing a reset
        to put the service back in the state it was previously.
        """

        if re.search("::",path):
            
            if self.verbose:
                
                print "\tModel Container: setting parameter concept %s %s %s" % (path, field, str(value))

            self._model_container.SetParameterConcept(path, field, value)
        
        
        else:
            
            if self.verbose:

                print "\tModel Container: setting parameter %s %s %s" % (path, field, str(value))
            
            self._model_container.SetParameter(path, field, value)


        if not no_store:
            
            # at the end we save any parameters passed.
            self.parameters.append(dict(component_name=path, field=field, value=value))

#---------------------------------------------------------------------------

    def _ParseArguments(self):
        """!

        Gets loadable ndf files from strings by checking for
        the .ndf suffix. 
        """
        
        files = []
        
        for a in self._arguments:

            possible_filename = ""
            
            if a == 'filename':

                possible_filename = self._arguments['filename']

            else:

                possible_filename = a
                
            if re.search(".ndf", possible_filename):

                files.append(possible_filename)
                

        for filename in files:

            if self.verbose:

                print "Loading model from file '%s'" % filename

            self.Load(filename)


