import numpy as np

# EN: Import post-processors for exporting results
# PT-BR: Importa pós-processadores para exportar resultados
from .mass_model.report_mass import MassPostProcessor
from .energy_model.energy_postprocess import EnergyPostProcessor

# EN: Import Stream class to build outlet streams
# PT-BR: Importa classe Stream para criar correntes de saída
from .stream import Stream


class SimulationResults:
    """
    EN:
    Container for all simulation results.

    Stores:
        geometry
        mass model variables
        energy model variables

    Provides export utilities.

    PT-BR:
    Container para todos os resultados da simulação.

    Armazena:
        geometria
        variáveis do modelo de massa
        variáveis do modelo de energia

    Fornece utilidades de exportação.
    """

    def __init__(self):

        # -----------------------------
        # geometry
        # geometria
        # -----------------------------

        # EN/PT: number of discretization nodes
        self.N = None

        # EN/PT: axial coordinate vector
        self.z = None

        # EN/PT: list of components
        self.components = None

        # -----------------------------
        # mass model
        # modelo de massa
        # -----------------------------

        # EN/PT: total retentate flow profile
        self.F = None

        # EN/PT: total permeate flow profile
        self.G = None

        # EN/PT: retentate composition profile
        self.x_ret = None

        # EN/PT: permeate composition profile
        self.y_per = None

        # EN/PT: retentate pressure profile
        self.P = None

        # EN/PT: permeate pressure profile
        self.p = None

        # EN/PT: total membrane flux
        self.J = None

        # EN/PT: component fluxes
        self.J_comp = None

        # EN/PT: composition of membrane flux
        self.z_J = None

        # -----------------------------
        # energy model
        # modelo de energia
        # -----------------------------

        # EN/PT: retentate temperature profile
        self.T_ret = None

        # EN/PT: permeate temperature profile
        self.T_per = None

        # EN/PT: retentate enthalpy
        self.h_ret = None

        # EN/PT: permeate enthalpy
        self.h_per = None

        # EN/PT: enthalpy of membrane flux
        self.h_J = None

        # EN/PT: heat transfer coefficient profile
        self.UA = None

        # EN/PT: case name
        self.case_name = None

        # EN/PT: permeability
        self.permeability = None

        # EN/PT: viscosity
        self.viscosity = None

        # EN/PT: molecularweight
        self.molecularweight = None



    # ------------------------------------------------
    # derived quantities
    # propriedades derivadas
    # ------------------------------------------------

    @property
    def recovery(self):

        # EN: Fraction of feed recovered in permeate
        # PT-BR: Fração da alimentação recuperada no permeado

        if self.F is None:
            return None

        return 1 - self.F[-1] / self.F[0]


    # ------------------------------------------------
    # export mass model
    # exportar modelo de massa
    # ------------------------------------------------

    def export_mass_excel(self, filename="mass_results.xlsx"):

        # EN: Ensure mass results are available
        # PT-BR: Verifica se resultados de massa existem
        if self.F is None:
            raise RuntimeError("Mass results not available")

        post = MassPostProcessor()

        # EN/PT: Export results to Excel
        post.export_results_to_excel(
            filename=filename,
            case_name=self.case_name,
            components=self.components,
            F=self.F,
            x_ret=self.x_ret,
            G=self.G,
            y_per=self.y_per,
            J=self.J,
            J_comp=self.J_comp,
            z_J=self.z_J,
            P=self.P,
            p=self.p
        )


    # ------------------------------------------------
    # export energy model
    # exportar modelo de energia
    # ------------------------------------------------

    def export_energy_excel(self, filename="energy_results.xlsx"):

        # EN: Ensure energy model was executed
        # PT-BR: Verifica se o modelo de energia foi executado
        if self.T_ret is None:
            raise RuntimeError("Energy model was not executed")

        post = EnergyPostProcessor(self.components)

        post.export_results_to_excel(
            filename=filename,
            case_name=self.case_name,
            components=self.components,

            F=self.F,
            x_ret=self.x_ret,
            h_ret=self.h_ret,
            h_ret_mix=self.h_ret,

            G=self.G,
            y_per=self.y_per,
            h_per=self.h_per,
            h_per_mix=self.h_per,

            J=self.J,
            J_comp=self.J_comp,
            z_J=self.z_J,
            h_J=self.h_J,

            P=self.P,
            p=self.p,

            T_ret=self.T_ret,
            T_per=self.T_per,

            UA=self.UA
        )


    # ------------------------------------------------
    # export both
    # exportar ambos
    # ------------------------------------------------

    def export_all(self,
                   mass_file="mass_results.xlsx",
                   energy_file="energy_results.xlsx"):

        # EN/PT: Export both models
        self.export_mass_excel(mass_file)

        if self.T_ret is not None:
            self.export_energy_excel(energy_file)


    # ------------------------------------------------
    # search composition by index or component name
    # busca de componente por nome ou índice
    # ------------------------------------------------

    def _comp_index(self, comp):
        """
        EN:
        Resolve component index.

        Parameters
        ----------
        comp : str or int
            Component name or index.

        Returns
        -------
        int
            Component index.

        PT-BR:
        Resolve o índice do componente.

        Parâmetros
        ----------
        comp : str ou int
            Nome ou índice do componente.

        Retorna
        -------
        int
            Índice do componente.
        """

        # EN/PT: if index
        if isinstance(comp, int):

            if comp < 0 or comp >= len(self.components):
                raise IndexError(
                    f"Component index {comp} out of range (0-{len(self.components)-1})"
                )

            return comp

        # EN/PT: if name
        if isinstance(comp, str):

            if comp not in self.components:
                raise ValueError(
                    f"Component '{comp}' not found. "
                    f"Available: {self.components}"
                )

            return self.components.index(comp)

        raise TypeError("Component must be name (str) or index (int)")    


    # ------------------------------------------------
    # component-based access
    # acceso por componente
    # ------------------------------------------------

    def component_flux(self, comp):
        """
        EN: Membrane flux profile for a component
        PT-BR: Perfil de fluxo na membrana por componente
        """
        i = self._comp_index(comp)
        return self.J_comp[:, i]
    

    def retentate_composition(self, comp):

        i = self._comp_index(comp)
        return self.x_ret[:, i]
    

    def permeate_composition(self, comp):

        i = self._comp_index(comp)
        return self.y_per[:, i]


    def component_retentate_flow(self, comp):

        i = self._comp_index(comp)
        return self.F * self.x_ret[:, i]
    

    def component_permeate_flow(self, comp):

        i = self._comp_index(comp)
        return self.G * self.y_per[:, i]


    def list_components(self):

        # EN: Return list of components
        # PT-BR: Retorna lista de componentes
        return self.components
    

    # ------------------------------------------------
    # outlet streams
    # correntes de saída
    # ------------------------------------------------

    def outlet(self, side="retentate"):

        # EN: Return outlet stream as Stream object
        # PT-BR: Retorna corrente de saída como objeto Stream

        if side == "retentate":

            return Stream(
                flow=self.F[-1],
                composition=self.x_ret[-1],
                pressure=self.P[-1],
                temperature=self.T_ret[-1] if self.T_ret is not None else None,
                components=self.components,
                permeability=self.permeability,
                viscosity=self.viscosity,
                molecularweight=self.molecularweight
            )

        if side == "permeate":

            # EN: Counter-current → outlet is index 0
            # PT-BR: Contracorrente → saída é índice 0
            return Stream(
                flow=self.G[0],
                composition=self.y_per[0],
                pressure=self.p[0],
                temperature=self.T_per[0] if self.T_per is not None else None,
                components=self.components,
                permeability=self.permeability,
                viscosity=self.viscosity,
                molecularweight=self.molecularweight                
            )

        raise ValueError("side must be 'retentate' or 'permeate'")
