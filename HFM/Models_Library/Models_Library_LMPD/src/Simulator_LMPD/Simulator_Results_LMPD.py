#region Title: SimulatorResultsLMPD
# Nature: Results container
# Methodology: Stores the terminal state the algebraic model produces, and the
#              diagnostics that say how far it had to depart from the classical
#              log-mean to get there.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       11-Aug-2026    J.V.A. Tupinamba               First version, mirrors SimulatorResultsHFM
##################################################################################################################
#endregion

import numpy as np

from Common.Streams.Streams import Stream


class SimulatorResultsLMPD:
    """
    EN: Container for the results of one algebraic evaluation.

        The contrast with SimulatorResultsHFM is deliberate and is the point of
        the model: there are no profile arrays here. An LMPD model carries no
        profiles, so what it returns is terminal states plus the correction
        factor that stands for everything between them.

    PT-BR: Resultados de uma avaliacao algebrica. Nao ha vetores de perfil: o
           modelo LMPD nao carrega perfil nenhum, so estados terminais e o fator
           de correcao que responde pelo que ha entre eles.
    """

    def __init__(self):
        self.components: list = []
        self.case_name: tuple = ("lmpd", "case")
        self.feasible: bool = True
        self.converged: bool = False
        self.message: str = ""

        # -----------------------------
        # terminal state / estado terminal
        # -----------------------------
        self.stage_cut: float = float("nan")
        self.FRet: float = float("nan")
        self.FPerm: float = float("nan")
        self.ZRet: np.ndarray = np.array([])
        self.ZPerm: np.ndarray = np.array([])
        self.ZPermSealed: np.ndarray = np.array([])
        self.PRetIn: float = float("nan")
        self.PRetOut: float = float("nan")
        self.PPermOut: float = float("nan")
        self.PPermSealed: float = float("nan")

        # -----------------------------
        # correction factor / fator de correcao
        # -----------------------------
        self.Phi: np.ndarray = np.array([])
        self.c_chord: np.ndarray = np.array([])
        self.slope_feed: np.ndarray = np.array([])
        self.slope_sealed: np.ndarray = np.array([])
        self.If: float = float("nan")
        self.family: str = ""
        self.closure: str = ""

        # -----------------------------
        # solver / solucao
        # -----------------------------
        self.residual: float = float("nan")
        self.n_unknowns: int = 0
        self.n_evaluations: int = 0

    # ------------------------------------------------------------------ views
    def _i(self, comp: str) -> int:
        return self.components.index(comp)

    def retentate_fraction(self, comp: str) -> float:
        """EN: Retentate mole fraction of one component."""
        return float(self.ZRet[self._i(comp)])

    def permeate_fraction(self, comp: str) -> float:
        """EN: Permeate mole fraction of one component."""
        return float(self.ZPerm[self._i(comp)])

    def correction(self, comp: str) -> float:
        """EN: Correction factor of one component. 1.0 is the classical model."""
        return float(self.Phi[self._i(comp)])

    def retentate_stream(self, temperature: float) -> Stream:
        """EN: Retentate as a Stream, so it can feed another unit."""
        return Stream(flow=self.FRet, composition=self.ZRet,
                      pressure=self.PRetOut, temperature=temperature,
                      components=self.components)

    def permeate_stream(self, temperature: float) -> Stream:
        """EN: Permeate as a Stream."""
        return Stream(flow=self.FPerm, composition=self.ZPerm,
                      pressure=self.PPermOut, temperature=temperature,
                      components=self.components)

    def summary(self) -> str:
        """EN: One-screen report. PT-BR: Relatorio de uma tela."""
        L = [f"LMPD  family={self.family}  closure={self.closure}"
             f"  converged={self.converged}  |r|={self.residual:.2e}",
             f"  stage cut          {self.stage_cut:.6f}",
             f"  retentate flow     {self.FRet:.6g} mol/s",
             f"  permeate  flow     {self.FPerm:.6g} mol/s",
             f"  P_R  {self.PRetIn/1e5:.3f} -> {self.PRetOut/1e5:.3f} bar",
             f"  P_P  {self.PPermSealed/1e5:.3f} -> {self.PPermOut/1e5:.3f} bar",
             f"  I_f                {self.If:.5f}"]
        for k, comp in enumerate(self.components):
            L.append(f"  {comp:<6} x_R {self.ZRet[k]:.6f}   y_P {self.ZPerm[k]:.6f}"
                     f"   Phi {self.Phi[k]:.5f}")
        return "\n".join(L)
