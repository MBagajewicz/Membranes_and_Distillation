# HFM/HFM_Chu_FDM_OO/geometry.py

import numpy as np


class Geometry:
    """
    Geometry of the hollow fiber module.

    PASSIVE Class:
    - only stores geometric data
    - calculates derived quantities
    - does not know physics, solver or properties
    """
    """
    Geometria do módulo de fibras ocas.

    Classe PASSIVA:
    - apenas armazena dados geométricos
    - calcula grandezas derivadas
    - não conhece física, solver ou propriedades
    """

    def __init__(
        self,
        LHidraulic,
        DiamShell,
        DiamFiber_o,
        DiamFiber_i,
        NFibers,
        NCells,
    ):
        """
        Parameters
        ----------
        LHidraulic : float
            Module length [m]
            Comprimento do módulo [m]
        DiamShell : float
            Shell diameter [m]
            Diâmetro do casco [m]
        DiamFiber_o : float
            Fiber outer diameter [m]
            Diâmetro externo da fibra [m]
        DiamFiber_i : float
            Fiber inner diameter [m]
            Diâmetro interno da fibra [m]
        NFibers : int
            Number of fibers
            Número de fibras
        NCells : int
            Number of FDM segments
            Número de segmentos FDM
        """
        self.LHidraulic = LHidraulic
        self.DiamShell = DiamShell
        self.DiamFiber_o = DiamFiber_o
        self.DiamFiber_i = DiamFiber_i
        self.NFibers = NFibers
        self.NCells = NCells

        # ===============================
        # Derived quantities
        # Grandezas derivadas
        # ===============================
        self.dz = self.LHidraulic / self.NCells

        # Membrane area per unit length
        # Área de membrana por unidade de comprimento
        self.AREA_PER_L = np.pi * self.DiamFiber_o * self.NFibers

        # Membrane area per segment
        # Área de membrana por segmento
        self.AREA_SEG = self.AREA_PER_L * self.dz