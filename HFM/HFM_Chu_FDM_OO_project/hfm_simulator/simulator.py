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
from .energy_model.thermo_model_no_mix_enth import ThermoModel

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
        self.segments = 50

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
        F_feed_total = feed.flow
        x_feed = feed.composition

        # EN: Convert total flow to component flow
        # PT-BR: Converte vazão total em vazão por componente
        F_feed = F_feed_total * np.array(x_feed)

        P_feed = feed.pressure
        T = feed.temperature

        props = self.properties

        # EN: Permeability comes from feed (design choice)
        # PT-BR: Permeabilidade vem da alimentação (decisão de design)
        J_vals = feed.permeability

        n_comp = len(J_vals)

        # EN: Permeate pressure from scenario
        # PT-BR: Pressão do permeado do cenário
        P_perm = p["P_p"]

        # EN: Gas constant
        # PT-BR: Constante dos gases
        R = p["R"]


        # ------------------------------------------------
        # Geometry
        # Geometria
        # ------------------------------------------------

        geom = Geometry(
            L=p["L"],
            D_shell=p["D"],
            D_o=p["D_o"],
            D_i=p["D_i"],
            N_fibers=(1 - p["Void_Frac"]) * (p["D"]**2) / (p["D_o"]**2),
            N_segments=self.segments
        )

        N = geom.N
        width = 2 * n_comp + 2


        # ------------------------------------------------
        # Module selection
        # Seleção do módulo
        # ------------------------------------------------

        if self.pressure_drop:

            # EN: Hydraulic correlations for pressure drop
            # PT-BR: Correlações hidráulicas para queda de pressão
            K_shell = (
                192 * geom.N_fibers * geom.D_o *
                (geom.D_shell + geom.N_fibers * geom.D_o)
            ) / (
                np.pi * (geom.D_shell**2 - geom.N_fibers * geom.D_o**2)**3
            )

            K_bore = 128 / (np.pi * geom.D_i**4 * geom.N_fibers)

            module = HFM_WithDP(
                geometry=geom,
                properties=props,
                R=R,
                T=T,
                J=J_vals,
                K_shell=K_shell,
                K_bore=K_bore,
                n_comp=n_comp,
                F_feed=F_feed,
                P_feed=P_feed,
                P_perm=P_perm
            )

        else:

            module = HFM_NoDP(
                geometry=geom,
                properties=props,
                R=R,
                T=T,
                J=J_vals,
                n_comp=n_comp,
                F_feed=F_feed,
                P_feed=P_feed,
                P_perm=P_perm
            )


        # ------------------------------------------------
        # Initial guess
        # Chute inicial
        # ------------------------------------------------

        F_guess = np.zeros((N + 1, n_comp))
        G_guess = np.zeros((N + 1, n_comp))

        for i in range(n_comp):

            F_guess[:, i] = np.linspace(F_feed[i], F_feed[i]*0.8, N+1)
            G_guess[:, i] = np.linspace(F_feed[i]*0.8, 1e-6, N+1)

        P_guess = np.linspace(P_feed, P_feed - 1e4, N+1)
        p_guess = np.linspace(P_perm, P_perm + 1e4, N+1)

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

        sol_mat = sol.reshape((N+1, width))


        # ------------------------------------------------
        # Extract results
        # Extrair resultados
        # ------------------------------------------------

        F_fin = sol_mat[:, :n_comp]
        G_fin = sol_mat[:, n_comp:2*n_comp]

        P_fin = sol_mat[:, 2*n_comp]
        p_fin = sol_mat[:, 2*n_comp+1]


        # ------------------------------------------------
        # STREAM VARIABLES
        # Variáveis de corrente
        # ------------------------------------------------

        F = F_fin.sum(axis=1)
        G = G_fin.sum(axis=1)

        X_R = F_fin / F[:, None]

        X_P = np.zeros_like(G_fin)

        for k in range(len(G)):

            if G[k] > 1e-12:
                X_P[k] = G_fin[k] / G[k]


        # ------------------------------------------------
        # MEMBRANE FLUXES
        # Fluxos de membrana
        # ------------------------------------------------

        J_comp = np.zeros((N+1, n_comp))

        for k in range(1, N+1):
            J_comp[k,:] = G_fin[k-1,:] - G_fin[k,:]

        J = J_comp.sum(axis=1)

        Z_J = np.zeros((N+1, n_comp))

        for k in range(1, N+1):

            if J[k] > 1e-12:
                Z_J[k] = J_comp[k] / J[k]


        # ------------------------------------------------
        # RESULTS OBJECT
        # Objeto de resultados
        # ------------------------------------------------

        results = SimulationResults()

        results.N = N
        results.z = np.linspace(0, geom.L, N+1)

        results.components = components
        results.case_name = p.get("name", "case")

        results.F = F
        results.G = G

        results.x_ret = X_R
        results.y_per = X_P

        results.P = P_fin
        results.p = p_fin

        results.J = J
        results.J_comp = J_comp
        results.z_J = Z_J

        results.permeability = feed.permeability
        results.viscosity = feed.viscosity
        results.molecularweight = feed.molecularweight


        # ------------------------------------------------
        # ENERGY MODEL
        # Modelo de energia
        # ------------------------------------------------

        if self.energy:

            thermo = ThermoModel(
                components=components,
                P_ret=P_fin,
                p_per=p_fin,
                x_ret=X_R,
                y_per=X_P,
                z_J=Z_J
            )

            UA = geom.AREA_SEG * np.ones(len(F)) * self.heat_transfer_coef

            energy_module = EnergyModule(
                F_ret=F,
                G_per=G,
                P_ret=P_fin,
                P_per=p_fin,
                x_ret=X_R,
                y_per=X_P,
                thermo=thermo,
                T_ret_in=T,
                UA=UA,
                J_per=J,
                z_J=Z_J
            )

            T_guess = np.zeros(2*(N+1))

            T_guess[:N+1] = np.linspace(T, T-0.1, N+1)
            T_guess[N+1:] = np.linspace(T-2, T-2.1, N+1)

            energy_solver = EnergySolver(
                energy_module,
                thermo
            )

            energy_results = energy_solver.solve(T_guess)

            results.T_ret = energy_results["T_ret"]
            results.T_per = energy_results["T_per"]

            results.h_ret = energy_results["h_ret"]
            results.h_per = energy_results["h_per"]
            results.h_J = energy_results["h_J"]

            results.UA = UA

        return results

