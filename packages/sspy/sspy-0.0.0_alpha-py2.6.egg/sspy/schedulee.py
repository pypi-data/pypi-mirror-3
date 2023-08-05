"""!
@file schedulee.py

This file contains the implementation for a basic schedulee.
This was formerly called SimpleHeccer in a previous implementation.
The name is kept general since it will become pluggable. This class
mainly functions as an abstraction to handle error checking
and strict typing. 
"""
import pdb
import sys


from errors import ScheduleeError

#
# Should probably be a way to automatically update this list
# depending on the types of plugins present but not going to think
# of that yet
#
schedulee_types = ['solver', 'input', 'output']

class Schedulee:
    """!
    @brief Abstraction class for schedulee objects.
    """

#---------------------------------------------------------------------------

    def __init__(self, schedulee=None, schedulee_type=None, verbose=False):


        if schedulee is None:

            raise ScheduleeError("Not defined")

        if schedulee_type is None:

            raise ScheduleeError("Type not defined")

        if schedulee_type not in schedulee_types:

            raise ScheduleeError("Invalid type '%s'" % schedulee_type)

        try:
            
            self.time_step = schedulee.GetTimeStep()

        except Exception, e:

            raise ScheduleeError("Can't obtain time step: %s\n" % e)

        if self.time_step < 0.0 or self.time_step is None:

            raise ScheduleeError("Invalid step value: '%s'\n" % self.time_step)

        self.current_time = 0.0

        self.current_step = 0

        self._schedulees_type = schedulee_type

        self._schedulee = schedulee

        self.type = schedulee_type

        self.verbose = verbose

#---------------------------------------------------------------------------

    def Finish(self):
        """

        """
        try:

            self._schedulee.Finish()

        except Exception, e:

            raise ScheduleeError("%s" % e)
        
#---------------------------------------------------------------------------

    def GetCore(self):
        """

        """
        return self._schedulee

#---------------------------------------------------------------------------

    def GetName(self):

        return self._schedulee.GetName()

#---------------------------------------------------------------------------


    def GetType(self):

        return self.type

#---------------------------------------------------------------------------

    def New(self, model, name, filename):
        """
        not needed?
        """
        pass


#---------------------------------------------------------------------------

    def Pause(self):
        """
        not sure how this will work
        """
        pass

#---------------------------------------------------------------------------

    def Step(self):

        try:

            self._schedulee.Step(self.current_time)

        except Exception, e:

            raise ScheduleeError("%s" % e)

        self.current_time += self.time_step

        self.current_step += 1
        
#---------------------------------------------------------------------------        

    def SetTimeStep(self, time_step):
        """

        """
        try:
            
            return self._schedulee.SetTimeStep(time_step)

        except TypeError, e:

            return ScheduleeError("Can't set time step: %s" % e)
        
#---------------------------------------------------------------------------        

    def GetTimeStep(self):
        """

        """
        try:
            
            return self._schedulee.GetTimeStep()

        except TypeError, e:

            return ScheduleeError("Can't retrieve time step: %s" % e)

#---------------------------------------------------------------------------

    def GetCurrentStep(self):
        """
        @brief Returns the current step
        """
        return self.current_step

#---------------------------------------------------------------------------
    
    def GetCurrentTime(self):
        """
        @brief Returns the current simulation time
        """
        return self.current_time

#---------------------------------------------------------------------------

    def Compile(self):

        try:

            self._schedulee.Compile()

        except Exception, e:

            raise ScheduleeError("%s" % e)

#---------------------------------------------------------------------------

    def Initialize(self):

        try:

            self._schedulee.Initialize()

        except Exception, e:

            raise ScheduleeError("%s" % e)

        self.current_time = 0.0

#---------------------------------------------------------------------------

    def Report(self):
        """

        """

        if self.verbose:

            pass
            # commented this out since it produces a lot of unuseful output
#            print "%s: %d %f" % (self.GetName(), self.GetTimeStep(), self.GetCurrentTime())
        
        try:
            # The internals of the report are handled by passing
            # verbose options to the simulation object through the
            # specifcation file
            self._schedulee.Report()

        except Exception, e:

            raise ScheduleeError("Can't report schedulee for '%s': %s" % (self.GetName(),e))


        
#---------------------------------------------------------------------------

    def Run(self, time):

         pass


#----------------------------------------------------------------------------
