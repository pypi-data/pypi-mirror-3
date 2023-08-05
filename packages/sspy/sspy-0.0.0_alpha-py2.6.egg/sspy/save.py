"""!


"""
import os
import pdb
import sys

try:
    import yaml
except ImportError:
    sys.exit("Need PyYaml http://pyyaml.org/\n")


class SaveError(Exception):
    pass


indent = "  "

#*********************************** Begin Save ****************************

class Save:
    """
    Class exports the schledule to YAML. Has the potential to be pluggable
    with some simpl changes.
    """
    
#---------------------------------------------------------------------------
    
    def __init__(self, scheduler, filename=None):
        """
        @param scheduler Reference to the scheduler
        """
        
        self.scheduler = scheduler

        self.filename = None

#---------------------------------------------------------------------------

    def SaveToFile(self, filename=None):

        schedule = {}

        name = self.Name()
        
        if not name is None:

            schedule['name']=name
            
        apply_block = self.Apply()

        if not apply_block is None:

            schedule['apply']=apply_block

        loaded_services = self.scheduler.GetLoadedServices()

        if len(loaded_services) > 0:

            schedule['services']=self.Services()

        loaded_solvers = self.scheduler.GetLoadedSolvers()

        if len(loaded_solvers) > 0:

            schedule['solverclasses']=self.SolverClasses()


        inputclasses_block = self.InputClasses()

        if not inputclasses_block is None:

            schedule['inputclasses'] = inputclasses_block


        outputclasses_block = self.OutputClasses()

        if not outputclasses_block is None:

            schedule['outputclasses'] = outputclasses_block


        if filename is None:

            print yaml.dump(schedule,explicit_start=True,default_flow_style=False)
            
#---------------------------------------------------------------------------

    def SetFilename(self, filename):

        self.filename = filename

#---------------------------------------------------------------------------

    def Analyzers(self):

        return dict(analyzers={})

#---------------------------------------------------------------------------

    def ApplicationClasses(self):

        pass

#---------------------------------------------------------------------------

    def Apply(self):
        """

        This apply block excludes the 'results' key.
        """

        steps = None
        time = None

        try:

            steps = self.scheduler.steps 

        except Exception:

            pass

        try:

            time = self.scheduler.simulation_time

        except Exception:

            pass

        simulations = []

        verbosity_level = self.scheduler.GetVerbosityLevel()

        if not steps is None:

            sim = dict(arguments=[steps, dict(verbose=verbosity_level)],
                       method='steps')

            simulations.append(sim)

        elif not time is None:

            sim = dict(arguments=[time, dict(verbose=verbosity_level)],
                       method='advance')

            simulations.append(sim)
            

        apply_block = dict(simulation=simulations)

        return apply_block

#---------------------------------------------------------------------------

    def Models(self):

        pass

#---------------------------------------------------------------------------

    def Name(self):

        return self.scheduler.GetName()

#---------------------------------------------------------------------------

    def Optimize(self):

        pass

#---------------------------------------------------------------------------

    def InputClasses(self):

        inputs = self.scheduler.GetLoadedInputs()

        if len(inputs) <= 0:

            return None

        else:

            i = inputs[0]

            input_type = i.GetType()

            if input_type == 'perfectclamp':

                options = {}

                if not i.command_voltage is None:
                    
                    options['command']=i.command_voltage

                if not i.command_file is None:

                    options['filename']=i.command_file

                if i.GetName() != "Untitled PerfectClamp":

                    options['name']=i.GetName()

                perfectclamp_block = {}
                perfectclamp_block['module_name']='Experiment'
                perfectclamp_block['options']=options
                perfectclamp_block['package']='Experiment::PerfectClamp'

                return {'perfectclamp': perfectclamp_block}
                
            else:

                raise SaveError("Can't save input, '%s' currently not supported" % input_type)

#---------------------------------------------------------------------------

    def Inputs(self):

        pass

#---------------------------------------------------------------------------

    def OutputClasses(self):
        """
        Currently only takes the first output class. The sspy format only
        allows one of one type.
        """
        outputs = self.scheduler.GetLoadedOutputs()

        if len(outputs) <= 0:

            return None

        else:

            o = outputs[0]

            output_type = o.GetType()

            if output_type == 'double_2_ascii':

                options = {}
                options['filename']=o.GetFilename()

                if not o.format is None:

                    options['format']=o.format

                if not o.mode is None:

                    options['output_mode']='steps'

                output_class = {}
                output_class['module_name']='Experiment'
                output_class['options']=options
                output_class['package']='Experiment::Output'

                return {'double_2_ascii': output_class}

            else:

                raise SaveError("Can't save output, '%s' currently not supported" % output_type)
            
#---------------------------------------------------------------------------

    def Outputs(self):

        outputs = self.scheduler.GetOutputs()

        
 
#---------------------------------------------------------------------------

    def Services(self):

        services = self.scheduler.GetLoadedServices()

        services_block = {}

        if len(services) <= 0:

            return None

        else:

            service = services[0]

            service_type = service.GetType()

            if service_type == 'model_container':

                arguments = {}
                arguments['arguments']=[service.files]

                initializers = {}
                initializers['initializers']=[arguments,]

                model_container_block = {}
                model_container_block['model_container']=initializers
                model_container_block['module_name']="Neurospaces"

            else:

                raise SaveError("Currently only saves 'model_container' schedules, this sched is %s" % service_type)


        return model_container_block


#---------------------------------------------------------------------------

    def SolverClasses(self):
        """
        Right now sspy (and ssp) only handles one solver per simulation.
        """
        solvers = self.scheduler.GetLoadedSolvers()

        solverclasses_block = {}

        if len(solvers) <= 0:

            return None

        else:

            solver = solvers[0]

            services = self.scheduler.GetLoadedServices()

            # This will be the default service type
            service_name = "model_container"
            
            if len(services) > 0:
                
                service_name = services[0].GetType()


            if solver.GetType() == 'heccer':

                reporting = {}
                reporting['granularity']=solver.granularity
                reporting['tested_things']=solver.dump_options

                configuration = {}
                configuration['reporting']=reporting


                constructor_settings = {}                
                constructor_settings['dStep']=solver.GetTimeStep()
                constructor_settings['configuration']=configuration

                if solver.options > 0:

                    options = {}
                    options['iOptions']=solver.options

                    constructor_settings['options']=options

                heccer_block = {}
                heccer_block['constructor_settings']=constructor_settings

                solverclasses_block['heccer']=heccer_block
                solverclasses_block['module_name']='Heccer'


            elif solver.GetType() == 'chemesis3':

                constructor_settings = {}

                constructor_settings['dStep']=solver.GetTimeStep()

                chemesis_block = {}
                chemesis_block['constructor_settings']=constructor_settings
                
                solverclasses_block['chemesis3']=chemesis_block
                solverclasses_block['module_name']='Chemesis3'


            solverclasses_block['service_name']=service_name

            return solverclasses_block

#---------------------------------------------------------------------------







#************************************ End Save ****************************
