"""
####################################################################################################################
HEX Library
Calculation: Heat Load
####################################################################################################################
"""


def HEX_heat_load(
    mass_flow_rate,
    specific_heat,
    inlet_temperature,
    outlet_temperature,
):
    """
    Calculate the heat load exchanged by a fluid stream.

    Parameters
    ----------
    mass_flow_rate : float
        Fluid mass flow rate.
    specific_heat : float
        Fluid specific heat capacity.
    inlet_temperature : float
        Fluid inlet temperature.
    outlet_temperature : float
        Fluid outlet temperature.

    Returns
    -------
    float
        Heat load.
    """

    return (
        mass_flow_rate
        * specific_heat
        * (inlet_temperature - outlet_temperature)
    )