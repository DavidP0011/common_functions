# dpm_common_functions/__init__.py

# Reexporta la función de autenticación
from .dpm_GCP_ini_utils import _ini_authenticate_API

# Puedes reexportar más funciones o submódulos
# from .otro_modulo import otra_funcion

__all__ = ["_ini_authenticate_API"]  # Lista de símbolos públicos
