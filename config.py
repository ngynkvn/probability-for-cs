import configparser
import numpy as np

rng = np.random.default_rng()


class Config:
    """
    Singleton / Global object that holds config parameters for application.
    """

    SIM_CONFIG = configparser.ConfigParser()
    DEBUG_CONFIG = configparser.ConfigParser()

    def __init__(self, config):
        if "Simulation" not in config:
            raise ValueError('Missing "Simulation" header from config file.')
        else:
            Config.SIM_CONFIG = config["Simulation"]
        if "Debug" in config:
            Config.DEBUG_CONFIG = config["Debug"]
