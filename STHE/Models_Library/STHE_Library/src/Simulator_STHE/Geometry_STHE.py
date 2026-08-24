"""
Geometry definitions for the STHE simulator.

This module contains the classes that describe the exchanger geometry.
No calculations are performed here.
"""


class Shell:
    """
    Shell geometry.
    """

    def __init__(self):

        # Shell inside diameter [m]
        self.diameter = None

        # Fouling factor [m2 K / W]
        self.fouling_factor = None

class Tubes:
    """
    Tube bundle geometry.
    """

    def __init__(self):

        # Tube length [m]
        self.length = None

        # Tube outside diameter [m]
        self.outside_diameter = None

        # Tube inside diameter [m]
        self.inside_diameter = None

        # Tube pitch ratio (-)
        self.pitch_ratio = None

        # Tube layout
        self.layout = None

        # Number of tube passes
        self.passes = None

        # Wall conductivity [W/(m K)]
        self.wall_conductivity = None

        # Fouling factor [m2 K / W]
        self.fouling_factor = None

        # stream in tube side "hot_stream or cold_stream"
        self.stream = "hot_stream"


class Baffles:
    """
    Baffle geometry.
    """

    def __init__(self):

        # Number of baffles
        self.number = None

        # Baffle cut (-)
        self.cut = None

        # Number of sealing strips
        self.sealing_strips = None


class Geometry:
    """
    Complete exchanger geometry.
    """

    def __init__(self):

        self.shell = Shell()

        self.tubes = Tubes()

        self.baffles = Baffles()