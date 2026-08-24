"""
Stream definitions for the STHE simulator.

This module contains the classes that describe the process streams.
No calculations are performed here.
"""


class State:
    """
    Thermodynamic state of a process stream.
    """

    def __init__(self):

        # Operating conditions
        self.temperature = None      # [K]
        self.pressure = None         # [Pa]
        self.flow = None             # [kg/s]

        # Fluid definition
        self.fluid = None
        self.components = None
        self.composition = None

        # Optional physical properties
        self.density = None          # [kg/m3]
        self.viscosity = None        # [Pa.s]
        self.cp = None               # [J/kg.K]
        self.conductivity = None     # [W/m.K]


class Stream:
    """
    Process stream.
    """

    def __init__(self):

        # Stream identification
        self.name = None
        self.description = None

        # Stream states
        self.inlet = State()
        self.outlet = State()


class Streams:
    """
    Process streams of the exchanger.
    """

    def __init__(self):

        self.hot = Stream()
        self.cold = Stream()

