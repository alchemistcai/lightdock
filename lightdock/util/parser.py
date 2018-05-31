"""Module to parse the LightDock program command line options"""

import argparse
import os
from lightdock.constants import GSO_SEED, STARTING_POINTS_SEED,\
    DEFAULT_TRANSLATION_STEP, DEFAULT_ROTATION_STEP, STARTING_NM_SEED, DEFAULT_NMODES_STEP, DEFAULT_LIST_EXTENSION, \
    DEFAULT_LIGHTDOCK_PREFIX
from lightdock.error.lightdock_errors import LightDockError
from lightdock.version import CURRENT_VERSION


def get_lightdock_structures(input_file):
    """Get a list of the PDB files in the input_file"""
    input_file_name, input_file_extension = os.path.splitext(input_file)
    file_names = []
    if input_file_extension == DEFAULT_LIST_EXTENSION:
        with open(input_file) as input_lines:
            for line in input_lines:
                file_name = line.rstrip(os.linesep)
                lightdock_structure = os.path.join(os.path.dirname(file_name),
                                                   DEFAULT_LIGHTDOCK_PREFIX % os.path.basename(file_name))
                if os.path.exists(lightdock_structure):
                    file_names.append(lightdock_structure)
    else:
        file_name = input_file
        lightdock_structure = os.path.join(os.path.dirname(file_name),
                                           DEFAULT_LIGHTDOCK_PREFIX % os.path.basename(file_name))
        if os.path.exists(lightdock_structure):
            file_names.append(lightdock_structure)
        else:
            raise LightDockError('Structure file %s not found' % lightdock_structure)
    return file_names


class SetupCommandLineParser(object):
    """Parses the command line of lightdock_setup"""
    @staticmethod
    def valid_file(file_name):
        if not os.path.exists(file_name):
            raise argparse.ArgumentTypeError("The file does not exist")
        return file_name
    
    @staticmethod
    def valid_integer_number(int_value):
        try:
            int_value = int(int_value)
        except:
            raise argparse.ArgumentTypeError("%s is an invalid value" % int_value)
        if int_value <= 0:
            raise argparse.ArgumentTypeError("%s is an invalid value" % int_value)
        return int_value
    
    @staticmethod
    def valid_float_number(float_value):
        try:
            float_value = float(float_value)
        except:
            raise argparse.ArgumentTypeError("%s is an invalid value" % float_value)
        if float_value <= 0.:
            raise argparse.ArgumentTypeError("%s is an invalid value" % float_value)
        return float_value

    def __init__(self):
        parser = argparse.ArgumentParser(prog="lightdock_setup")
        
        # Receptor
        parser.add_argument("receptor_pdb", help="Receptor structure PDB file", 
                            type=SetupCommandLineParser.valid_file, metavar="receptor_pdb_file")
        # Ligand
        parser.add_argument("ligand_pdb", help="Ligand structure PDB file",
                            type=SetupCommandLineParser.valid_file, metavar="ligand_pdb_file")
        # Clusters
        parser.add_argument("swarms", help="Number of swarms of the simulation",
                            type=SetupCommandLineParser.valid_integer_number)
        # Glowworms
        parser.add_argument("glowworms", help="Number of glowworms per cluster", 
                            type=SetupCommandLineParser.valid_integer_number)
        # Starting points seed
        parser.add_argument("--seed_points", help="Random seed used in starting positions calculation",
                            dest="starting_points_seed", type=int, default=STARTING_POINTS_SEED)
        # FTDock poses as cluster centers
        parser.add_argument("-ft", "--ftdock", help="Use previous FTDock poses as starting positions", 
                            dest="ftdock_file", type=CommandLineParser.valid_file,
                            metavar="ftdock_file")
        # Dealing with OXT atoms
        parser.add_argument("--noxt", help="Remove OXT atoms",
                            dest="noxt", action='store_true', default=False)
        # Normal modes
        parser.add_argument("-anm", "--anm", help="Activates the use of ANM backbone flexibility",
                            dest="use_anm", action='store_true', default=False)
        # Normal modes extent seed
        parser.add_argument("--seed_anm", help="Random seed used in ANM intial extent",
                            dest="anm_seed", type=int, default=STARTING_NM_SEED)

        self.args = parser.parse_args()



class CommandLineParser(object):
    """Parses the command line"""
    @staticmethod
    def valid_file(file_name):
        if not os.path.exists(file_name):
            raise argparse.ArgumentTypeError("The file does not exist")
        return file_name
    
    @staticmethod
    def valid_integer_number(int_value):
        try:
            int_value = int(int_value)
        except:
            raise argparse.ArgumentTypeError("%s is an invalid value" % int_value)
        if int_value <= 0:
            raise argparse.ArgumentTypeError("%s is an invalid value" % int_value)
        return int_value
    
    @staticmethod
    def valid_float_number(float_value):
        try:
            float_value = float(float_value)
        except:
            raise argparse.ArgumentTypeError("%s is an invalid value" % float_value)
        if float_value <= 0.:
            raise argparse.ArgumentTypeError("%s is an invalid value" % float_value)
        return float_value

    def __init__(self):
        parser = argparse.ArgumentParser(prog="lightdock")
        
        # Receptor
        parser.add_argument("setup_file", help="Setup file name", 
                            type=CommandLineParser.valid_file, metavar="setup_file")
        # Steps
        parser.add_argument("steps", help="number of steps of the simulation",
                            type=CommandLineParser.valid_integer_number)
        # Configuration file
        parser.add_argument("-f", "--file", help="algorithm configuration file",
                            dest="configuration_file", type=CommandLineParser.valid_file, 
                            metavar="configuration_file")
        # Scoring function
        parser.add_argument("-s", "--scoring_function", help="scoring function used",
                            dest="scoring_function")
        # GSO seed
        parser.add_argument("-sg", "--seed", help="seed used in the algorithm", 
                            dest="gso_seed", type=int, default=GSO_SEED)
        # Translation step
        parser.add_argument("-t", "--translation_step", help="translation step", 
                            type=CommandLineParser.valid_float_number, default=DEFAULT_TRANSLATION_STEP)
        # Rotation step
        parser.add_argument("-r", "--rotation_step", help="normalized rotation step", 
                            type=CommandLineParser.valid_float_number, default=DEFAULT_ROTATION_STEP)
        # Version
        parser.add_argument("-V", "-v", "--version", help="show version", 
                            action='version', version="%s %s" % (parser.prog, CURRENT_VERSION))
        # Number of cpu cores to use
        parser.add_argument("-c", "--cores", help="number of cpu cores to use",
                            dest="cores", type=CommandLineParser.valid_integer_number)
        # Profiling
        parser.add_argument("--profile", help="Output profiling data", 
                            dest="profiling", action='store_true', default=False)
        # MPI parallel execution
        parser.add_argument("-mpi", "--mpi", help="activates the MPI parallel execution", 
                            dest="mpi", action='store_true', default=False)
        # Normal modes step
        parser.add_argument("-ns", "--nmodes_step", help="normalized normal modes step",
                            type=CommandLineParser.valid_float_number, default=DEFAULT_NMODES_STEP)
        # Local minimization
        parser.add_argument("-min", "--min", help="activates the local minimization",
                            dest="local_minimization", action='store_true', default=False)

        self.args = parser.parse_args()

