###################################################################################################################
#region Titles and Header
# Nature: Communication with Aspen Plus
# Methodology: Set trimming + Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          27-Nov-2024     Alice Peccini             Proposed 
##################################################################################################################
# INPUT: Functions to initialize, run and get results from Aspen Plus 
##################################################################################################################
# INSTRUCTIONS
# Add python functions (def), input parameters and variables are defined in the "Examples_Repository.py" dictionary
#                          named Model_Declarations['Discretized_Values_of_Variables'] or in the one
#                          named Model_Parameters
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
import numpy as np
import win32com.client as win32
import pywintypes
import os

#endregion
##################################################################################################################

##################################################################################################################
#region Calculations

# -------------------------------------------- ASPEN INITIALIZATION -------------------------------------------- # 

def fun_initial_Aspen(file_name, stream_name, block_name, comp_name, z_feed, F_feed, T_feed, P_col, x_TOP, x_BOTTOM, 
                      D_LB, D_UB, RR_LB, RR_UB):

     # Build path Aspen subfolder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    aspen_dir = os.path.join(script_dir, 'Aspen')

    # Build the correct path to the backup (.bkp) file inside the 'Aspen' subfolder
    file_path = os.path.join(aspen_dir, file_name)

    #  Initialize Aspen Plus
    Aspen = None
    try:
        Aspen = win32.Dispatch('Apwn.Document')  # Attempt to connect to Aspen Plus
    except (AttributeError, pywintypes.com_error):
        print("Error accessing COM object. Rebuilding cache and trying again...")
        try:
            win32.gencache.Rebuild()
            Aspen = win32.Dispatch('Apwn.Document')  # Retry connection
        except Exception as cache_error:
            print(f"[ERROR] Failed to rebuild COM cache: {cache_error}")
            exit(1)  # Encerra a execução imediatamente

    try:
        Aspen.InitFromArchive2(file_path)  # Initialize Aspen Plus with the backup (.bkp) file
        print("Aspen Plus successfully initialized!")
    except pywintypes.com_error as e:
        print("\n[ERROR] Failed to initialize Aspen Plus.")
        print("Please check if the license is active and ensure Aspen Plus is properly installed.")
        print(f"Error details: {e}")
        print("Execution will be terminated.")
        exit(1)  # Encerra a execução imediatamente

    Aspen.Visible = 0           # Run in the background
    Aspen.SuppressDialogs = 1   # Suppress pop-ups
    Aspen.Reinit()              # Reset file from previous runs

    # Set feed stream data:
    for comp, mole_frac in zip(comp_name, z_feed):   # Molar fractions for components
        molar_flow = F_feed*mole_frac                       # Calculate molar flow for the component
        Aspen.Tree.FindNode(rf'\Data\Streams\{stream_name}\Input\FLOW\MIXED\{comp}').Value = molar_flow     # Input molar flow for each component
    Aspen.Tree.FindNode(rf'\Data\Streams\{stream_name}\Input\TEMP\MIXED').Value = T_feed                    # Input feed stream temperature (K)
    Aspen.Tree.FindNode(rf'\Data\Streams\{stream_name}\Input\PRES\MIXED').Value = P_col                     # Input feed stream pressure (Pa)
    
    # Set column data that remain the same for every candidate:
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\PRES1').Value = P_col                            # Column pressure (Pa)
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\VALUE\1').Value = x_TOP                          # Top product specification (mole frac)
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\VALUE\2').Value = x_BOTTOM                       # Bottom product specification (mole frac)

    # Distillate rate and reflux ratio bounds for aspen search:
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\LB\1').Value = D_LB                              # Distillare rate lower bound (kmol/h)
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\UB\1').Value = D_UB                              # Distillare rate upper bound (kmol/h)
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\LB\2').Value = RR_LB                             # Molar reflux ratio lower bound
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\UB\2').Value = RR_UB                             # Molar reflux ratio upper bound

    return Aspen

    
#------------------------------------------- RUNNING ASPEN SIMULATION ------------------------------------------ # 

def fun_run_Aspen(v_Ns, v_Nf, Aspen, block_name, stream_names, components, v_Nc): 

    feed_name = stream_names[0]
    distillate_name = stream_names[1]

    # Update RadFrac inputs for current candidate:
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\NSTAGE').Value = v_Ns
    Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Input\FEED_STAGE\{feed_name}').Value = v_Nf

    # Running Aspen simulation:
    results = None
    Aspen.Engine.Run2()

    # Checks for errors or warning:
    is_error = Aspen.Tree.FindNode(r'\Data\Results Summary\Run-Status\Output\PER_ERROR').Value

    # If Results are available without errors or warning:
    if is_error == 0:
        print(f'Simulation converged successfully for Ns = {v_Ns} and Nf = {v_Nf}')
        results = fun_getfromAspen(Aspen, block_name, distillate_name, v_Ns, components, v_Nc)
    else:
        # Retrieves status message
        message = Aspen.Tree.FindNode(r'\Data\Results Summary\Run-Status\Output\PER_ERROR\2').Value

        # If it is a warning
        if message == 'completed with warnings:':
            # Retrieves block name (OBSERVATION: THIS ONLY WORKS FOR A SINGLE BLOCK SO FAR)
            block = Aspen.Tree.FindNode(r'\Data\Results Summary\Run-Status\Output\PER_ERROR\3').Value
            block = block.strip()   # Removes blank spaces
            print(f'Aspen Simulation for candidate Ns = {v_Ns} and Nf = {v_Nf} was completed with warnings')

            # Retrieves warning message:
            block_warning =  Aspen.Tree.FindNode(rf'\Data\Blocks\{block}\Output\PER_ERROR')
            warning_messages = []
            stop = 0
            i = 1
            while stop == 0:
                try:
                    message = Aspen.Tree.FindNode(rf'\Data\Results Summary\Run-Status\Output\PER_ERROR\{i}').Value
                    warning_messages.append(message)
                    i = i + 1
                except:
                    stop = 1
            complete_warning = "\n".join(warning_messages)
            print('\nWARNING:', complete_warning)

            # Instructions for user:
            print('You may want to check your Aspen file and make changes so this does not happen again')
            print('For now, this candidate will be considered not converged. Reseting and trying again\n')
        else:
            print(f'Simulation did NOT converged for Ns = {v_Ns} and Nf = {v_Nf}','Reseting and trying again')
            
        Aspen.Reinit()
        Aspen.Engine.Run2()
        is_error = Aspen.Tree.FindNode(r'\Data\Results Summary\Run-Status\Output\PER_ERROR').Value
        if is_error == 0:
            print(f'Simulation converged successfully for Ns = {v_Ns} and Nf = {v_Nf}')
            results = fun_getfromAspen(Aspen, block_name, distillate_name, v_Ns, components, v_Nc)
        else:
            print(f'Simulation did NOT converged for Ns = {v_Ns} and Nf = {v_Nf} on the second try, reseting for next run')
            Aspen.Reinit()

    return results

#----------------------------------------- GETTING RESULTS FROM ASPEN ------------------------------------------ # 

def fun_getfromAspen(Aspen,block_name, distillate_name, v_Ns,components,v_Nc):

    # Initialize 2D arrays for compositions (Nc x Ns):
    vapor_compositions = np.zeros((v_Nc, v_Ns))
    liquid_compositions = np.zeros((v_Nc, v_Ns))

    # Initialize 1D arrays for vapor flows, liquid flows, and temperatures (Ns,):
    vapor_mole_flows = np.zeros(v_Ns)
    liquid_mole_flows = np.zeros(v_Ns)
    vapor_mass_flows = np.zeros(v_Ns)
    liquid_mass_flows = np.zeros(v_Ns)
    temperatures = np.zeros(v_Ns)    

    # Extracting stage-wise results from Aspen:
    for st in range(1,v_Ns+1):
        
        vapor_mole_flows[st - 1] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\VAP_FLOW\{st}').Value        # kmol/h
        liquid_mole_flows[st - 1] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\LIQ_FLOW\{st}').Value       # kmol/h
        vapor_mass_flows[st - 1] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\VAP_FLOW_MS\{st}').Value     # kg/h
        liquid_mass_flows[st - 1] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\LIQ_FLOW_MS\{st}').Value    # kg/h
        temperatures[st - 1] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\B_TEMP\{st}').Value
        for i, comp in enumerate(components):  # Loop through components
            vapor_node = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\Y\{st}\{comp}')
            vapor_compositions[i, st - 1] = vapor_node.Value
            liquid_node = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\X\{st}\{comp}')
            liquid_compositions[i, st - 1] = liquid_node.Value  
                
    # Extracting overall column results:
    distillate_rate = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\MOLE_D').Value                        # kmol/h
    condenser_duty = abs(Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\COND_DUTY').Value)*1000/3600       # kJ/h to W
    reboiler_duty = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\REB_DUTY').Value*1000/3600              # kJ/h to W
    distillate_liquid_molar_density = Aspen.Tree.FindNode(rf'\Data\Streams\{distillate_name}\Output\RHO_LIQ').Value*1000 # distillate liquid molar density in mol/cm³ converted to kmol/m³
    distillate_liquid_molar_weight = Aspen.Tree.FindNode(rf'\Data\Streams\{distillate_name}\Output\MW_LIQ').Value       # distillateliquid molar weight
    distillate_liquid_mass_density = distillate_liquid_molar_density*distillate_liquid_molar_weight
    mass_distillate_rate = distillate_rate*distillate_liquid_molar_weight

    # Select the maximum vapor flow throughout the column (value in Vmax and index position in ArgV) and its corresponding values:
    maximum_vapor_flow = np.max(vapor_mass_flows)/3600                                                              # kg/h to kg/s                                              
    ArgV = np.argmax(vapor_mole_flows)    
    liquid_molar_density = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\RHO_LIQ\{ArgV + 1}').Value*1000  # liquid molar density in mol/cm³ converted to kmol/m³
    liquid_molar_weight = Aspen.Tree.FindNode(rf"\Data\Blocks\{block_name}\Output\MW_LIQ\{ArgV + 1}").Value         # liquid molar weight
    vapor_molar_density = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\RHO_GAS\{ArgV + 1}').Value*1000   # vapor molar density in mol/cm³ converted to kmol/m³
    vapor_molar_weight = Aspen.Tree.FindNode(rf"\Data\Blocks\{block_name}\Output\MW_GAS\{ArgV + 1}").Value          # vapor molar weight
    liquid_mass_density = liquid_molar_density*liquid_molar_weight                                                  # kg/m³
    vapor_mass_density = vapor_molar_density*vapor_molar_weight                                                     # kg/m³

    # Organize results in a nested dictionary
    results = {
        'vapor_mole_flows': vapor_mole_flows,
        'liquid_mole_flows': liquid_mole_flows,
        'vapor_mass_flows': vapor_mass_flows,
        'liquid_mass_flows': liquid_mass_flows,
        'temperatures': temperatures,
        'vapor_compositions': vapor_compositions,
        'liquid_compositions': liquid_compositions,
        'distillate_rate': distillate_rate,
        'condenser_duty': condenser_duty,
        'reboiler_duty': reboiler_duty,
        'maximum_vapor_flow': maximum_vapor_flow,
        'liquid_mass_density': liquid_mass_density,
        'vapor_mass_density': vapor_mass_density,
        'mass_distillate_rate': mass_distillate_rate,
        'distillate_liquid_mass_density': distillate_liquid_mass_density
    }

    return results

def fun_getfromAspen_hydraulics(v_Ns, Aspen, block_name):
    
    # Initialize 1D arrays for densities and surface tension (Ns,):
    density_liquid = np.zeros(v_Ns-2)
    density_vapor = np.zeros(v_Ns-2)
    surface_tension = np.zeros(v_Ns-2)

    # Extracting stage-wise results from Aspen:
    for st in range(2, v_Ns):
        density_liquid[st - 2] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\HYD_RHOL\{st}').Value*1000     # g/cm³ to kg/m³
        density_vapor[st - 2] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\HYD_RHOV\{st}').Value*1000      # g/cm³ to kg/m³
        surface_tension[st - 2] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\HYD_STEN\{st}').Value/1000    # dyne/cm to N/m
        
    # Organize results in a nested dictionary
    hydraulics = {
        'density_liquid': density_liquid,
        'density_vapor': density_vapor,
        'surface_tension': surface_tension
    }

    return hydraulics

def fun_getfromAspen_condenser(Aspen, block_name, stream_name):

    # Initialize dictionary
    Condenser_hot_stream = {}
    # Top Product stream name
    MW = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\MW_LIQ\1').Value
    Condenser_hot_stream['liquid_density'] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\RHO_LIQ\1').Value*1000*MW  # mol/cm³ to kmol/m³, then to kg/m³ 
    Condenser_hot_stream['vapor_density'] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\RHO_GAS\2').Value*1000*MW   # mol/cm³ to kmol/m³, then to kg/m³
    Condenser_hot_stream['liquid_viscosity'] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\HYD_MUL\1').Value/1000   # cP to Pa.s
    Condenser_hot_stream['vapor_viscosity'] = Aspen.Tree.FindNode(rf'\Data\Blocks\{block_name}\Output\HYD_MUV\2').Value/1000    # cP to Pa.s
    Condenser_hot_stream['thermal_conductivity'] = Aspen.Tree.FindNode(rf"\Data\Streams\{stream_name}\Output\STRM_UPP\KMX\MIXED\LIQUID").Value  # W/(m.K)
    
    return Condenser_hot_stream

def fun_getfromAspen_reboiler(Aspen, stream_name):

    Reboiler_cold_stream = {}
    Reboiler_cold_stream['critical_pressure'] = Aspen.Tree.FindNode(rf"\Data\Streams\{stream_name}\Output\STRM_UPP\PCMX\MIXED\TOTAL").Value # Pa
    
    return Reboiler_cold_stream
