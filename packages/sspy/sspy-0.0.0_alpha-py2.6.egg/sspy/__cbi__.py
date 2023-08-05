"""
@file __cbi__.py

This file provides data for a packages integration
into the CBI architecture.
"""


__author__ = "Mando Rodriguez"
__copyright__ = "Copyright 2010, The GENESIS Project"
__credits__ = ["Mando Rodriguez","Hugo Cornelis","Allan Coop"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Mando Rodriguez"
__email__ = "rodrigueza14 at uthscsa.edu"
__requires__ = ['yaml']
__status__ = "Development"
__description__ = """
The simple scheduler in python is a software package that 
uses the model container (a service) and heccer (a solver) to run a simulation 
with a set of simulation parameters. It can be extended by using and creating 
plugins for solvers, services, inputs and outputs. 
"""

__url__ = "http://genesis-sim.org"
__download_url__ = "http://repo-genesis3.cbi.utsa.edu"

class PackageInfo:
        
    def GetRevisionInfo(self):
# $Format: "        return \"${monotone_id}\""$
        return "86a093ecc5d3027ffafe0151ba6c0319bc6b7b83"

    def GetName(self):
# $Format: "        return \"${package}\""$
        return "sspy"

    def GetVersion(self):
# $Format: "        return \"${major}.${minor}.${micro}-${label}\""$
        return "0.0.0-alpha"

    def GetDependencies(self):
        """!
        @brief Provides a list of other CBI dependencies needed.
        """
        dependencies = []
        
        return dependencies
