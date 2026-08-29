# HFM/HFM_Chu_FDM_OO/module_base.py

class BaseHFMModule:
    """
    Base interface for Hollow Fiber Membrane (HFM) models.

    EN:
    ----
    This class defines the common interface for all HFM physical models.
    Any specific model (with or without pressure drop or other) must implement
    the residuals(x) method.

    PT-BR:
    ------
    Esta classe define a interface comum para todos os modelos físicos
    de membranas de fibras ocas (HFM).
    Qualquer modelo específico (com ou sem queda de pressão ou outro) deve
    implementar o método residuals(x).
    """

    def residuals(self, x):
        raise NotImplementedError(
            "HFM model must implement residuals(x)"
        )