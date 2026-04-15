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
        L,
        D_shell,
        D_o,
        D_i,
        N_fibers,
        N_segments,
    ):
        """
        Parameters
        ----------
        L : float
            Module length [m]
            Comprimento do módulo [m]
        D_shell : float
            Shell diameter [m]
            Diâmetro do casco [m]
        D_o : float
            Fiber outer diameter [m]
            Diâmetro externo da fibra [m]
        D_i : float
            Fiber inner diameter [m]
            Diâmetro interno da fibra [m]
        N_fibers : int
            Number of fibers
            Número de fibras
        N_segments : int
            Number of FDM segments
            Número de segmentos FDM
        """
        self.L = L
        self.D_shell = D_shell
        self.D_o = D_o
        self.D_i = D_i
        self.N_fibers = N_fibers
        self.N = N_segments

        # ===============================
        # Derived quantities
        # Grandezas derivadas
        # ===============================
        self.Dz = self.L / self.N

        # Membrane area per unit length
        # Área de membrana por unidade de comprimento
        self.AREA_PER_L = np.pi * self.D_o * self.N_fibers

        # Membrane area per segment
        # Área de membrana por segmento
        self.AREA_SEG = self.AREA_PER_L * self.Dz