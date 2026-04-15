import numpy as np

# EN: Import mass model components
# PT-BR: Importa componentes do modelo de massa
from .mass_model.geometry import Geometry
from .mass_model.module_dp import HFM_WithDP
from .mass_model.module_nodp import HFM_NoDP
from .mass_model.solver import HFMSolver

# EN: Import energy model components
# PT-BR: Importa componentes do modelo de energia
from .energy_model.energy_module import EnergyModule
from .energy_model.energy_solver import EnergySolver


# EN: Import results container
# PT-BR: Importa objeto de resultados
from .results import SimulationResults

# EN: Import Stream class (used for feed definition)
# PT-BR: Importa classe Stream (usada para definir a alimentação)
from .stream import Stream


class HFMSimulator:

    def __init__(self):

        # EN: Activate/deactivate energy balance
        # PT-BR: Ativa/desativa balanço de energia
        self.energy = True

        # EN: Activate/deactivate pressure drop
        # PT-BR: Ativa/desativa queda de pressão
        self.pressure_drop = False

        # EN: Number of discretization segments
        # PT-BR: Número de segmentos de discretização
        self.NCells = 50

        # EN: Global heat transfer coefficient [W/(m2 K)]
        # PT-BR: Coeficiente global de transferência de calor
        self.heat_transfer_coef = 4

        # EN: Scenario (geometry + operating conditions)
        # PT-BR: Cenário (geometria + condições operacionais)
        self.scenario = None

        # EN: Feed stream (VERY IMPORTANT)
        # PT-BR: Corrente de alimentação (MUITO IMPORTANTE)
        self.feed = None

        # EN: Mixture properties model
        # PT-BR: Modelo de propriedades da mistura
        self.properties = None

        # EN: Enthalpy Calculation Method
        # PT-BR: Método de Cálculo da Entalpia
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption
        self.enthalpy_method = 'Mix'



    # ---------------------------------------
    # scenario
    # cenário
    # ---------------------------------------

    def set_scenario(self, scenario):

        # EN: Assign scenario dictionary
        # PT-BR: Define o cenário
        self.scenario = scenario


    # ---------------------------------------
    # feed
    # alimentação
    # ---------------------------------------

    def set_feed(self, stream):

        # EN: Ensure feed is a Stream object
        # PT-BR: Garante que a alimentação é um objeto Stream
        if not isinstance(stream, Stream):
            raise TypeError("feed must be a Stream")

        self.feed = stream


    # ---------------------------------------
    # mixture properties
    # propriedades da mistura
    # ---------------------------------------

    def set_properties(self, properties):

        # EN: Assign thermophysical properties model
        # PT-BR: Define o modelo de propriedades
        self.properties = properties


    # ---------------------------------------
    # run simulation
    # rodar simulação
    # ---------------------------------------

    def run(self):

        # EN: Basic validations
        # PT-BR: Validações básicas
        if self.scenario is None:
            raise RuntimeError("Scenario not set")

        if self.properties is None:
            raise RuntimeError("Mixture properties not set")

        # ------------------------------------------------
        # Scenario data
        # Dados do cenário
        # ------------------------------------------------

        p = self.scenario

        # EN: Feed stream is the source of ALL inlet conditions
        # PT-BR: A corrente de alimentação define TODAS as condições de entrada
        feed = self.feed

        if feed is None:
            raise RuntimeError("Feed stream not set")

        # EN: Extract data from feed
        # PT-BR: Extrai dados da alimentação
        components = feed.components
        FFeed_total = feed.flow
        ZFeed = feed.composition

        # EN: Convert total flow to component flow
        # PT-BR: Converte vazão total em vazão por componente
        FFeed = FFeed_total * np.array(ZFeed)

        PFeed = feed.pressure
        T = feed.temperature

        props = self.properties

        # EN: permeance comes from feed (design choice)
        # PT-BR: Permeabilidade vem da alimentação (decisão de design)
        Permeance = feed.permeance

        n_comp = len(Permeance)

        # EN: Permeate pressure from scenario
        # PT-BR: Pressão do permeado do cenário
        PPerm = p["PPerm"]

        # EN: Gas constant
        # PT-BR: Constante dos gases
        R = p["R"]


        # ------------------------------------------------
        # Geometry
        # Geometria
        # ------------------------------------------------

        geom = Geometry(
            LHidraulic=float(p["LHidraulic"]),
            DiamShell=float(p["DiamShell"]),
            DiamFiber_o=float(p["DiamFiber_o"]),
            DiamFiber_i=float(p["DiamFiber_i"]),
            NFibers=int((1 - p["Void_Frac"]) * (p["DiamShell"]**2) / (p["DiamFiber_o"]**2)),
            NCells=self.NCells
        )

        NCells = geom.NCells
        width = 2 * n_comp + 2


        # ------------------------------------------------
        # Module selection
        # Seleção do módulo
        # ------------------------------------------------

        if self.pressure_drop:

            # EN: Hydraulic correlations for pressure drop
            # PT-BR: Correlações hidráulicas para queda de pressão
            K_shell = (
                192 * geom.NFibers * geom.DiamFiber_o *
                (geom.DiamShell + geom.NFibers * geom.DiamFiber_o)
            ) / (
                np.pi * (geom.DiamShell**2 - geom.NFibers * geom.DiamFiber_o**2)**3
            )

            K_bore = 128 / (np.pi * geom.DiamFiber_i**4 * geom.NFibers)

            module = HFM_WithDP(
                geometry=geom,
                properties=props,
                R=R,
                T=T,
                Permeance=Permeance,
                K_shell=K_shell,
                K_bore=K_bore,
                n_comp=n_comp,
                FFeed=FFeed,
                PFeed=PFeed,
                PPerm=PPerm
            )

        else:

            module = HFM_NoDP(
                geometry=geom,
                properties=props,
                R=R,
                T=T,
                Permeance=Permeance,
                n_comp=n_comp,
                FFeed=FFeed,
                PFeed=PFeed,
                PPerm=PPerm
            )


        # ------------------------------------------------
        # Initial guess
        # Chute inicial
        # ------------------------------------------------

        F_guess = np.zeros((NCells + 1, n_comp))
        G_guess = np.zeros((NCells + 1, n_comp))

        for i in range(n_comp):

            F_guess[:, i] = np.linspace(FFeed[i], FFeed[i]*0.8, NCells+1)
            G_guess[:, i] = np.linspace(FFeed[i]*0.8, 1e-6, NCells+1)

        P_guess = np.linspace(PFeed, PFeed - 1e4, NCells+1)
        p_guess = np.linspace(PPerm, PPerm + 1e4, NCells+1)

        x0 = np.hstack([
            F_guess,
            G_guess,
            P_guess.reshape(-1,1),
            p_guess.reshape(-1,1)
        ]).flatten()


        # ------------------------------------------------
        # MASS SOLVER
        # SOLVER DE MASSA
        # ------------------------------------------------

        solver = HFMSolver(module)

        sol, info = solver.solve(x0)

        sol_mat = sol.reshape((NCells+1, width))


        # ------------------------------------------------
        # Extract results
        # Extrair resultados
        # ------------------------------------------------

        FRet_fin = sol_mat[:, :n_comp]
        FPerm_fin = sol_mat[:, n_comp:2*n_comp]

        PRetCell_fin = sol_mat[:, 2*n_comp]
        PPermCell = sol_mat[:, 2*n_comp+1]


        # ------------------------------------------------
        # STREAM VARIABLES
        # Variáveis de corrente
        # ------------------------------------------------

        FRet = FRet_fin.sum(axis=1)
        FPerm = FPerm_fin.sum(axis=1)

        ZRet = FRet_fin / FRet[:, None]

        ZPerm = np.zeros_like(FPerm_fin)

        for k in range(len(FPerm)):

            if FPerm[k] > 1e-12:
                ZPerm[k] = FPerm_fin[k] / FPerm[k]


        # ------------------------------------------------
        # MEMBRANE FLUXES
        # Fluxos de membrana
        # ------------------------------------------------

        FMemb_comp = np.zeros((NCells+1, n_comp))

        for k in range(1, NCells+1):
            FMemb_comp[k,:] = FPerm_fin[k-1,:] - FPerm_fin[k,:]

        FMemb = FMemb_comp.sum(axis=1)

        ZMemb = np.zeros((NCells+1, n_comp))

        for k in range(1, NCells+1):

            if FMemb[k] > 1e-12:
                ZMemb[k] = FMemb_comp[k] / FMemb[k]


        # ------------------------------------------------
        # RESULTS OBJECT
        # Objeto de resultados
        # ------------------------------------------------

        results = SimulationResults()

        results.NCells = NCells
        results.z = np.linspace(0, geom.LHidraulic, NCells+1)

        results.components = components
        results.case_name = p.get("name", "case")

        results.FRet = FRet
        results.FPerm = FPerm

        results.ZRet = ZRet
        results.ZPerm = ZPerm

        results.PRetCell = PRetCell_fin
        results.PPermCell = PPermCell

        results.FMemb = FMemb
        results.FMemb_comp = FMemb_comp
        results.ZMemb = ZMemb

        results.Permeance = feed.permeance
        results.viscosity = feed.viscosity
        results.molecularweight = feed.molecularweight


        # ------------------------------------------------
        # ENERGY MODEL
        # Modelo de energia
        # ------------------------------------------------

        if self.energy:
            if self.enthalpy_method == 'Mix':
                from .energy_model.thermo_model import ThermoModelWithMixture
                thermo = ThermoModelWithMixture(
                    components=components,
                    PRet=PRetCell_fin,
                    PPerm=PPermCell,
                    ZRet=ZRet,
                    ZPerm=ZPerm,
                    ZMemb=ZMemb
                )
            else:
                from .energy_model.thermo_model_no_mix_enth import ThermoModel
                thermo = ThermoModel(
                    components=components,
                    PRet=PRetCell_fin,
                    PPerm=PPermCell,
                    ZRet=ZRet,
                    ZPerm=ZPerm,
                    ZMemb=ZMemb
                )



            if self.heat_transfer_coef:
                UA = geom.AREA_SEG * np.ones(len(FRet)) * self.heat_transfer_coef
            else:
                UA = None

            energy_module = EnergyModule(
                FRet=FRet,
                FPer=FPerm,
                PRet=PRetCell_fin,
                PPerm=PPermCell,
                ZRet=ZRet,
                ZPerm=ZPerm,
                thermo=thermo,
                T_ret_in=T,
                UA=UA,
                FMemb=FMemb,
                ZMemb=ZMemb,
                geom = geom
            )

            T_guess = np.zeros(2*(NCells+1))

            T_guess[:NCells+1] = np.linspace(T, T-0.1, NCells+1)
            T_guess[NCells+1:] = np.linspace(T-2, T-2.1, NCells+1)

            energy_solver = EnergySolver(
                energy_module,
                thermo
            )

            energy_results = energy_solver.solve(T_guess)

            results.T_ret = energy_results["T_ret"]
            results.T_per = energy_results["T_per"]

            mdot_b = sum(max(FPerm[0], 0.0) * props.M)
            A_bore = geom.NFibers * np.pi * (geom.DiamFiber_i/2) ** 2
            rho_b = results.PPermCell[0] * sum(props.M * results.ZPerm[0])/ (R*results.T_per[0]) #M méd
            vb = mdot_b / max(rho_b * A_bore, 1e-30)
            Re_b = rho_b * vb * (2.0 * (geom.DiamFiber_i/2)) / sum(props.M * results.ZPerm[0])
            print([vb,Re_b])
            mdot_s = max(FRet[-1], 0.0) * props.M


            results.hRet = energy_results["hRet"]
            results.hPerm = energy_results["hPerm"]
            results.hMemb = energy_results["hMemb"]

            results.UA = energy_results["UA"]
            results.U = energy_results["UA"]/geom.AREA_SEG
        mdot_b = sum(max(FPerm[0], 0.0) * props.M)
        A_bore = geom.NFibers * np.pi * (geom.DiamFiber_i / 2) ** 2
        rho_b = results.PPermCell[0] * sum(props.M * results.ZPerm[0]) / (R * T)  # M méd
        vb = mdot_b / max(rho_b * A_bore, 1e-30)
        Re_b = rho_b * vb * (2.0 * (geom.DiamFiber_i / 2)) / (sum(props.M * results.ZPerm[0])*sum(props.MU* results.ZPerm[0]))
        print('Bore outlet:',[vb, Re_b])

        mdot_s = sum(FRet[0] * props.M)
        A_shell_open = (np.pi / 4.0) * (
                geom.DiamShell ** 2
                - geom.NFibers * geom.DiamFiber_o ** 2
        )
        rho_s = results.PRetCell[0] * sum(props.M * results.ZRet[0]) / (R * T)  # M méd
        v_s = mdot_s / (rho_s * A_shell_open)

        Gs = mdot_s / A_shell_open

        D_h = (geom.DiamShell ** 2 - geom.NFibers * geom.DiamFiber_o ** 2) / (
                    geom.DiamShell + geom.NFibers * geom.DiamFiber_o)  # todo: revisar Dh

        Re_s = Gs * D_h / max(sum(props.MU* results.ZRet[0]), 1e-30)
        print('Shell inlet',[v_s, Re_s])
        return results

