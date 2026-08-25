#region Title: SimulatorGeometryLMPD
# Nature: Geometry definition
# Methodology: Same parameterisation as SimulatorGeometryHFM, so that a design
#              can be handed to either simulator unchanged. Carries no profile
#              and no mesh: the algebraic model has none.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       11-Aug-2026    J.V.A. Tupinamba               First version, mirrors the HFM geometry class
##################################################################################################################
#endregion

import numpy as np

R_GAS: float = 8.314462618


class SimulatorGeometryLMPD:
    """
    EN: Geometry of the hollow fiber module, for the algebraic model.

        PASSIVE class -- stores geometric data and derives the two pressure-drop
        coefficients. It knows no physics and no solver, exactly as its
        counterpart in the HFM library.

        The number of fibers is derived from the void fraction when not given,
        by the same relation the HFM library uses, so that both simulators place
        the same amount of membrane in the same shell.

    PT-BR: Geometria do modulo para o modelo algebrico. Classe PASSIVA, mesma
           parametrizacao da SimulatorGeometryHFM.
    """

    def __init__(self, LSingleMembrane: float, DiamShell: float,
                 DiamFiber_o: float, DiamFiber_i: float,
                 NFibers=None, Void_Frac=None,
                 NumberOfMembranesInSerie: int = 1,
                 NumberOfTubesInParallel: int = 1):
        """
        Parameters
        ----------
        LSingleMembrane : float
            Length of a single membrane [m] / Comprimento da membrana [m]
        DiamShell : float
            Shell diameter [m] / Diametro do casco [m]
        DiamFiber_o, DiamFiber_i : float
            Outer and inner fiber diameters [m] / Diametros externo e interno [m]
        NFibers : int or None
            Number of fibers; derived from Void_Frac when None
        Void_Frac : float or None
            Packing void fraction / Fracao de vazios
        """
        self.LSingleMembrane = LSingleMembrane
        self.NumberOfMembranesInSerie = NumberOfMembranesInSerie
        self.NumberOfTubesInParallel = NumberOfTubesInParallel
        self.DiamShell = DiamShell
        self.DiamFiber_o = DiamFiber_o
        self.DiamFiber_i = DiamFiber_i
        self.Void_Frac = Void_Frac
        self.NFibers = NFibers

        # ===============================
        # Derived quantities
        # Grandezas derivadas
        # ===============================
        self.LHidraulic = LSingleMembrane * NumberOfMembranesInSerie

        if not self.NFibers:
            if Void_Frac is None:
                raise ValueError(
                    "Either NFibers or Void_Frac must be given / "
                    "informe NFibers ou Void_Frac")
            self.NFibers = float(int(round(
                (1.0 - Void_Frac) * (DiamShell / DiamFiber_o) ** 2)))

        # EN: Total membrane area. The algebraic model integrates in area, so
        #     this is the single geometric quantity the balances see.
        # PT-BR: Area total. O modelo algebrico integra em area.
        self.AREA_TOTAL = np.pi * DiamFiber_o * self.NFibers * self.LHidraulic

        # EN: Bore coefficient, from Hagen-Poiseuille in the fiber lumen. The
        #     256 rather than 128 is because the relation is written in P^2 and
        #     the halving belongs to the flow closure, not to the coefficient.
        # PT-BR: Coeficiente do bore. O 256 e nao 128 porque a relacao esta em
        #        P^2 e a divisao por dois pertence ao fecho de vazao.
        self.K_BORE = (256.0 * R_GAS * self.LHidraulic
                       / (np.pi * DiamFiber_i ** 4 * self.NFibers))

        # EN: Shell coefficient, bundle correlation. Same expression as the
        #     reference model and as Chu et al. (2019), Eq. (3).
        # PT-BR: Coeficiente do casco, correlacao de feixe.
        den = DiamShell ** 2 - self.NFibers * DiamFiber_o ** 2
        if den <= 0.0:
            raise ValueError(
                "Fibers do not fit in the shell / as fibras nao cabem no casco")
        K_sh = (192.0 * self.NFibers * DiamFiber_o
                * (DiamShell + self.NFibers * DiamFiber_o) / (np.pi * den ** 3))
        self.K_SHELL = 2.0 * self.LHidraulic * K_sh * R_GAS

    def as_dict(self) -> dict:
        """EN: Flat view used by the residual. PT-BR: Visao plana p/ o residuo."""
        return dict(Di=self.DiamFiber_i, Do=self.DiamFiber_o, Nf=self.NFibers,
                    Atot=self.AREA_TOTAL, K_bore=self.K_BORE,
                    K_shell=self.K_SHELL, L=self.LHidraulic,
                    DiamShell=self.DiamShell)
