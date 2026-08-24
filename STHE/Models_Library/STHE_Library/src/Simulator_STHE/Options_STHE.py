"""
Options for the STHE simulator.

This module contains the configuration of the simulator.
"""


class SolverOptions:

    def __init__(self):

        # Numerical tolerance
        self.tolerance = 1e-6

        # Maximum iterations
        self.maximum_iterations = 100

        # Verbosity level
        self.verbosity = "normal"

class PropertyOptions:

    def __init__(self):

        # Flow basis
        self.flow_basis = "mass"

        # Default property package
        self.property_package = "CoolProp"


class CorrelationOptions:

    def __init__(self):

        # Tube-side heat transfer model
        self.tube_method = "Gnielinski"

        # Shell-side heat transfer model
        self.shell_method = "Bell"

        # LMTD correction factor parameter (Smith, 2005)
        self.Xp = 0.9


class ThermalOptions:

    def __init__(self):

        # Thermal calculation method used by STHE.simulate().
        #
        # "NoNTU" -> NoNTU Eq. (32), currently with F_T = 1.
        # "NTU"   -> Effectiveness-NTU method.
        #
        # NoNTU is the default so the new formulation is used unless
        # the user explicitly selects NTU.
        self.method = "NoNTU"

        # LMTD correction factor used by the NoNTU calculation
        # when F_method = "fixed".
        self.F_T = 1.0

        # Correction-factor method used by NoNTU.
        #
        # "fixed"
        #     Use F_T directly from self.F_T.
        #
        # "STHE_correction_factor"
        #     Iterate between NoNTU and the existing
        #     STHE_correction_factor calculation.
        #
        # Gardner and Underwood can be added later without
        # changing the NoNTU calculation interface.
        self.F_method = "STHE_correction_factor"

        # Controls for the iterative correction-factor calculation.
        self.F_tolerance = 1.0e-6
        self.F_maximum_iterations = 50
        self.F_relaxation = 1.0


class ReportOptions:

    def __init__(self):

        # Print calculation summary
        self.summary = True

        # Save calculation log
        self.log = True


class Options:

    def __init__(self):

        self.solver = SolverOptions()

        self.properties = PropertyOptions()

        self.correlations = CorrelationOptions()

        self.thermal = ThermalOptions()

        self.report = ReportOptions()